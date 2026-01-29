"""PR Reviewer - автоматический ревью Pull Requests"""
import os
import sys
import json
from github import Github
from dotenv import load_dotenv

from ai_client import ai_client

load_dotenv()


def review_file_for_issue(file_content: str, file_path: str, issue_description: str) -> dict:
    """Review одного файла на соответствие решению issue.
    
    Args:
        file_content: Содержимое файла
        file_path: Путь к файлу
        issue_description: Описание исходного issue
        
    Returns:
        { issue_solved: boolean, notes: string }
    """
    prompt = f"""Вы - опытный код-ревьюер. Проверьте, решает ли этот файл описанную проблему.

ИСХОДНАЯ ПРОБЛЕМА:
{issue_description}

ФАЙЛ: {file_path}
```
{file_content}
```

Проанализируйте:
1. Решает ли этот файл описанную проблему?
2. Есть ли ошибки в коде?
3. Соблюдены ли best practices?

ОБЯЗАТЕЛЬНО ответьте ТОЛЬКО в формате JSON:
{{
  "issue_solved": true/false,
  "notes": "Подробные заметки о том, что хорошо, что плохо, что исправлено"
}}
"""
    
    try:
        response = ai_client.analyze_file(prompt, expect_json=True)
        
        # Парсим JSON ответ
        if isinstance(response, str):
            result = json.loads(response)
        else:
            result = response
        
        # Проверяем наличие обязательных полей
        if "issue_solved" not in result or "notes" not in result:
            return {
                "issue_solved": False,
                "notes": f"AI response format error. Got: {result}"
            }
        
        return {
            "issue_solved": bool(result["issue_solved"]),
            "notes": str(result["notes"])
        }
    
    except json.JSONDecodeError as e:
        return {
            "issue_solved": False,
            "notes": f"Failed to parse AI response: {e}"
        }
    except Exception as e:
        return {
            "issue_solved": False,
            "notes": f"Error during file review: {e}"
        }


def review_pr_files(pr_number: int, repo_name: str = None, changed_files: list = None) -> dict:
    """Выполняет ревью файлов из PR.
    
    Args:
        pr_number: Номер PR
        repo_name: owner/repo (опционально, берётся из env)
        changed_files: Список файлов для review (если пустой - получим из GitHub)
        
    Returns:
        {
            success: bool,
            review_results: [{file, issue_solved, notes}],
            all_passed: bool,
            comment: str
        }
    """
    token = os.getenv("GITHUB_TOKEN")
    repo_name = repo_name or os.getenv("GITHUB_REPO")
    
    if not repo_name:
        return {"success": False, "error": "GITHUB_REPO not set"}
    
    if not token:
        return {"success": False, "error": "GITHUB_TOKEN not set"}
    
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        print(f"🔍 Reviewing PR #{pr_number}: {pr.title}")
        
        # Получаем issue description из PR body
        issue_description = pr.body or pr.title
        
        # Если нет changed_files, получаем из PR
        if not changed_files:
            changed_files = []
            for file in pr.get_files():
                changed_files.append(file.filename)
        
        print(f"   Files to review: {len(changed_files)}")
        
        review_results = []
        all_passed = True
        
        # Reviewим каждый изменённый файл
        for file_path in changed_files:
            print(f"   📄 Reviewing {file_path}...")
            
            try:
                # Получаем содержимое файла из PR branch
                file_content = repo.get_contents(file_path, ref=pr.head.sha).decoded_content.decode('utf-8')
            except Exception as e:
                # Если не можем получить (удалён, бинарный и т.д.)
                review_results.append({
                    "file": file_path,
                    "issue_solved": False,
                    "notes": f"Could not fetch file content: {e}"
                })
                all_passed = False
                continue
            
            # Reviewим файл
            file_review = review_file_for_issue(file_content, file_path, issue_description)
            
            review_results.append({
                "file": file_path,
                "issue_solved": file_review["issue_solved"],
                "notes": file_review["notes"]
            })
            
            if not file_review["issue_solved"]:
                all_passed = False
            
            status = "✅" if file_review["issue_solved"] else "❌"
            print(f"      {status} {file_path}")
        
        # Формируем комментарий для GitHub
        status_emoji = "✅" if all_passed else "⚠️"
        
        comment = f"""## {status_emoji} AI Code Review

**PR:** #{pr_number}  
**Files reviewed:** {len(review_results)}  
**Status:** {"All checks passed" if all_passed else "Issues found"}

---

"""
        
        for result in review_results:
            status = "✅ PASSED" if result["issue_solved"] else "❌ NEEDS WORK"
            comment += f"### {status}: `{result['file']}`\n\n"
            comment += f"{result['notes']}\n\n"
        
        comment += "---\n🤖 *Automated review by Coding Agent*"
        
        # Добавляем комментарий к PR
        try:
            pr.create_issue_comment(comment)
            print(f"📝 Added review comment to PR #{pr_number}")
        except Exception as e:
            print(f"⚠️ Could not post comment: {e}")
        
        return {
            "success": True,
            "review_results": review_results,
            "all_passed": all_passed,
            "comment": comment
        }
    
    except Exception as e:
        error_msg = f"Failed to review PR: {e}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def main():
    """CLI entry point"""
    pr_number = int(os.getenv("PR_NUMBER", 0))
    
    if not pr_number:
        if len(sys.argv) > 1:
            pr_number = int(sys.argv[1])
        else:
            print("❌ PR_NUMBER not set")
            sys.exit(1)
    
    result = review_pr_files(pr_number)
    
    if result.get("success") and result.get("all_passed"):
        print("✅ All files passed review")
        sys.exit(0)
    else:
        print("❌ Review found issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
