"""FastAPI сервер для GitHub App Webhooks"""
import hmac
import hashlib
import os
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from database import db, IssueStatus, PRReviewStatus

load_dotenv()

# Config
GITHUB_WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))


def verify_signature(payload: bytes, signature: str) -> bool:
    """Проверяет подпись webhook от GitHub."""
    if not GITHUB_WEBHOOK_SECRET:
        print("⚠️ GITHUB_WEBHOOK_SECRET not set, skipping verification")
        return True
    
    if not signature:
        return False
    
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


app = FastAPI(
    title="Coding Agent Webhook Server",
    description="Receives GitHub webhooks and queues issues for processing",
    version="1.0.0"
)


class HealthResponse(BaseModel):
    status: str
    pending_issues: int
    stats: dict


class IssueResponse(BaseModel):
    status: str
    doc_id: int
    message: str


@app.get("/", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    stats = db.get_stats()
    return HealthResponse(
        status="ok",
        pending_issues=stats["pending"],
        stats=stats
    )


@app.get("/issues")
async def list_issues():
    """Список всех issues в базе"""
    return {
        "issues": db.get_all(),
        "stats": db.get_stats()
    }


@app.get("/issues/pending")
async def list_pending():
    """Список pending issues"""
    return db.get_pending_issues()


@app.post("/webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    """Принимает webhooks от GitHub App.
    
    Поддерживаемые события:
    - issues.opened - новый issue создан
    - issues.reopened - issue переоткрыт
    - issue_comment.created - комментарий с @coding-agent
    """
    
    body = await request.body()
    
    # Проверяем подпись
    if not verify_signature(body, x_hub_signature_256):
        print("❌ Invalid webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    try:
        payload = await request.json()
    except Exception as e:
        print(f"❌ Failed to parse webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    print(f"ℹ️ Received webhook: {x_github_event}")
    
    # Обработка Issue events
    if x_github_event == "issues":
        action = payload.get("action")
        
        if action in ("opened", "reopened"):
            issue = payload.get("issue", {})
            repo = payload.get("repository", {})
            installation = payload.get("installation", {})
            
            repo_full_name = repo.get("full_name")
            issue_number = issue.get("number")
            title = issue.get("title", "")
            body_text = issue.get("body", "") or ""
            installation_id = installation.get("id")
            
            print(f"📋 New issue: {repo_full_name}#{issue_number} - {title}")
            
            doc_id = db.add_issue(
                repo_full_name=repo_full_name,
                issue_number=issue_number,
                title=title,
                body=body_text,
                installation_id=installation_id
            )
            
            return IssueResponse(
                status="queued",
                doc_id=doc_id,
                message=f"Issue #{issue_number} queued for processing"
            )
    
    # Обработка комментариев (для команды @coding-agent fix)
    if x_github_event == "issue_comment":
        action = payload.get("action")
        comment = payload.get("comment", {})
        issue = payload.get("issue", {})
        repo = payload.get("repository", {})
        
        if action == "created":
            comment_body = comment.get("body", "").lower()
            
            # Проверяем команду @coding-agent
            if "@coding-agent" in comment_body or "@code-agent" in comment_body:
                repo_full_name = repo.get("full_name")
                issue_number = issue.get("number")
                title = issue.get("title", "")
                body_text = issue.get("body", "") or ""
                
                print(f"🔄 Re-processing: {repo_full_name}#{issue_number}")
                
                # Проверяем существующий issue в БД
                existing = db.get_issue_by_number(repo_full_name, issue_number)
                if existing:
                    db.reset_to_pending(existing['doc_id'])
                    return IssueResponse(
                        status="requeued",
                        doc_id=existing['doc_id'],
                        message=f"Issue #{issue_number} requeued for processing"
                    )
                else:
                    doc_id = db.add_issue(
                        repo_full_name=repo_full_name,
                        issue_number=issue_number,
                        title=title,
                        body=body_text
                    )
                    return IssueResponse(
                        status="queued",
                        doc_id=doc_id,
                        message=f"Issue #{issue_number} queued for processing"
                    )
    
    # Обработка Pull Request events
    if x_github_event == "pull_request":
        action = payload.get("action")
        
        if action in ("opened", "synchronize", "reopened"):
            pr = payload.get("pull_request", {})
            repo = payload.get("repository", {})
            installation = payload.get("installation", {})
            
            repo_full_name = repo.get("full_name")
            pr_number = pr.get("number")
            installation_id = installation.get("id")
            
            # Получаем список изменённых файлов из PR
            changed_files = []
            if "changed_files" in pr:
                # В некоторых webhooks есть список файлов
                changed_files = [f.get("filename") for f in pr.get("files", [])]
            
            print(f"🔍 New PR for review: {repo_full_name}#{pr_number}")
            print(f"   Changed files: {len(changed_files) if changed_files else 'will fetch'}")
            
            doc_id = db.add_pr_review(
                repo_full_name=repo_full_name,
                pr_number=pr_number,
                changed_files=changed_files,  # Может быть пустым - worker получит из GitHub
                installation_id=installation_id
            )
            
            return IssueResponse(
                status="queued",
                doc_id=doc_id,
                message=f"PR #{pr_number} queued for review"
            )
    
    return {"status": "ignored", "event": x_github_event}


@app.post("/process/{repo_owner}/{repo_name}/{issue_number}")
async def manual_process(repo_owner: str, repo_name: str, issue_number: int):
    """Ручной запуск обработки issue (для тестирования)"""
    repo_full_name = f"{repo_owner}/{repo_name}"
    
    # Проверяем существующий
    existing = db.get_issue_by_number(repo_full_name, issue_number)
    if existing:
        db.reset_to_pending(existing['doc_id'])
        return IssueResponse(
            status="requeued",
            doc_id=existing['doc_id'],
            message=f"Issue #{issue_number} requeued"
        )
    
    # Добавляем новый (без body - worker получит из GitHub)
    doc_id = db.add_issue(
        repo_full_name=repo_full_name,
        issue_number=issue_number,
        title=f"Manual trigger #{issue_number}",
        body=""
    )
    
    return IssueResponse(
        status="queued",
        doc_id=doc_id,
        message=f"Issue #{issue_number} queued for processing"
    )


def run_server():
    """Запуск сервера"""
    import uvicorn
    print(f"🚀 Starting webhook server on port {SERVER_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=SERVER_PORT)


if __name__ == "__main__":
    run_server()
