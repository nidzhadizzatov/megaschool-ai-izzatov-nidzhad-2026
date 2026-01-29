from datetime import datetime
from enum import Enum
from pathlib import Path
from tinydb import TinyDB, Query
import os


class IssueStatus(str, Enum):
    PENDING = "pending"       # Ожидает обработки
    PROCESSING = "processing" # В обработке
    COMPLETED = "completed"   # PR создан
    FAILED = "failed"         # Ошибка


class PRReviewStatus(str, Enum):
    PENDING = "pending"       # Ожидает review
    REVIEWING = "reviewing"   # В процессе review
    APPROVED = "approved"     # Все файлы одобрены
    REJECTED = "rejected"     # Есть проблемы
    FAILED = "failed"         # Ошибка review


class IssueDB:
    """Wrapper для TinyDB - хранение issues и PR reviews из webhooks"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent
            db_path = os.getenv("DB_PATH", str(base_dir / "db.json"))
        self.db = TinyDB(db_path)
        self.issues = self.db.table("issues")
        self.pr_reviews = self.db.table("pr_reviews")
    
    def add_issue(
        self,
        repo_full_name: str,
        issue_number: int,
        title: str,
        body: str,
        installation_id: int = None
    ) -> int:
        """Добавить issue в очередь.
        
        Returns:
            doc_id записи
        """
        Issue = Query()
        # Проверяем, не существует ли уже активный
        existing = self.issues.search(
            (Issue.repo == repo_full_name) & 
            (Issue.issue_number == issue_number) &
            (Issue.status.one_of([IssueStatus.PENDING, IssueStatus.PROCESSING]))
        )
        if existing:
            return existing[0].doc_id
        
        doc_id = self.issues.insert({
            "repo": repo_full_name,
            "issue_number": issue_number,
            "title": title,
            "body": body,
            "installation_id": installation_id,
            "status": IssueStatus.PENDING,
            "attempts": 0,
            "error": None,
            "pr_number": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        return doc_id
    
    def get_pending_issues(self, limit: int = 10) -> list:
        """Получить issues ожидающие обработки."""
        Issue = Query()
        results = self.issues.search(Issue.status == IssueStatus.PENDING)
        # Добавляем doc_id к каждому результату
        for r in results:
            r['doc_id'] = r.doc_id
        return results[:limit]
    
    def get_issue_by_id(self, doc_id: int) -> dict | None:
        """Получить issue по ID."""
        result = self.issues.get(doc_id=doc_id)
        if result:
            result['doc_id'] = doc_id
        return result
    
    def get_issue_by_number(self, repo: str, issue_number: int) -> dict | None:
        """Получить issue по номеру."""
        Issue = Query()
        results = self.issues.search(
            (Issue.repo == repo) & (Issue.issue_number == issue_number)
        )
        if results:
            results[0]['doc_id'] = results[0].doc_id
            return results[0]
        return None
    
    def set_processing(self, doc_id: int) -> None:
        """Отметить issue как в обработке."""
        self.issues.update({
            "status": IssueStatus.PROCESSING,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def set_completed(self, doc_id: int, pr_number: int) -> None:
        """Отметить issue как завершённый."""
        self.issues.update({
            "status": IssueStatus.COMPLETED,
            "pr_number": pr_number,
            "error": None,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def set_failed(self, doc_id: int, error: str) -> None:
        """Отметить issue как неудачный."""
        issue = self.issues.get(doc_id=doc_id)
        attempts = (issue.get("attempts", 0) + 1) if issue else 1
        self.issues.update({
            "status": IssueStatus.FAILED,
            "error": error,
            "attempts": attempts,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def reset_to_pending(self, doc_id: int) -> None:
        """Сбросить статус на pending (для повторной обработки)."""
        self.issues.update({
            "status": IssueStatus.PENDING,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def increment_attempts(self, doc_id: int) -> int:
        """Увеличить счётчик попыток."""
        issue = self.issues.get(doc_id=doc_id)
        attempts = (issue.get("attempts", 0) + 1) if issue else 1
        self.issues.update({
            "attempts": attempts,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
        return attempts
    
    def get_all(self) -> list:
        """Получить все issues."""
        results = self.issues.all()
        for r in results:
            r['doc_id'] = r.doc_id
        return results
    
    def get_stats(self) -> dict:
        """Получить статистику."""
        Issue = Query()
        Review = Query()
        return {
            "pending": len(self.issues.search(Issue.status == IssueStatus.PENDING)),
            "processing": len(self.issues.search(Issue.status == IssueStatus.PROCESSING)),
            "completed": len(self.issues.search(Issue.status == IssueStatus.COMPLETED)),
            "failed": len(self.issues.search(Issue.status == IssueStatus.FAILED)),
            "total": len(self.issues.all()),
            "pr_pending": len(self.pr_reviews.search(Review.status == PRReviewStatus.PENDING)),
            "pr_reviewing": len(self.pr_reviews.search(Review.status == PRReviewStatus.REVIEWING)),
            "pr_approved": len(self.pr_reviews.search(Review.status == PRReviewStatus.APPROVED)),
            "pr_rejected": len(self.pr_reviews.search(Review.status == PRReviewStatus.REJECTED))
        }
    
    # ==================== PR Review Methods ====================
    
    def add_pr_review(
        self,
        repo_full_name: str,
        pr_number: int,
        changed_files: list[str],
        installation_id: int = None
    ) -> int:
        """Добавить PR в очередь на review.
        
        Args:
            repo_full_name: owner/repo
            pr_number: Номер PR
            changed_files: Список путей изменённых файлов
            installation_id: GitHub App installation ID
            
        Returns:
            doc_id записи
        """
        Review = Query()
        # Проверяем, не существует ли уже
        existing = self.pr_reviews.search(
            (Review.repo == repo_full_name) & 
            (Review.pr_number == pr_number) &
            (Review.status.one_of([PRReviewStatus.PENDING, PRReviewStatus.REVIEWING]))
        )
        if existing:
            return existing[0].doc_id
        
        doc_id = self.pr_reviews.insert({
            "repo": repo_full_name,
            "pr_number": pr_number,
            "changed_files": changed_files,
            "installation_id": installation_id,
            "status": PRReviewStatus.PENDING,
            "attempts": 0,
            "error": None,
            "review_results": [],  # [{file, issue_solved, notes}]
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        return doc_id
    
    def get_pending_pr_reviews(self, limit: int = 10) -> list:
        """Получить PR reviews ожидающие обработки."""
        Review = Query()
        results = self.pr_reviews.search(Review.status == PRReviewStatus.PENDING)
        for r in results:
            r['doc_id'] = r.doc_id
        return results[:limit]
    
    def get_pr_review_by_id(self, doc_id: int) -> dict | None:
        """Получить PR review по ID."""
        result = self.pr_reviews.get(doc_id=doc_id)
        if result:
            result['doc_id'] = doc_id
        return result
    
    def get_pr_review_by_number(self, repo: str, pr_number: int) -> dict | None:
        """Получить PR review по номеру."""
        Review = Query()
        results = self.pr_reviews.search(
            (Review.repo == repo) & (Review.pr_number == pr_number)
        )
        if results:
            results[0]['doc_id'] = results[0].doc_id
            return results[0]
        return None
    
    def set_pr_reviewing(self, doc_id: int) -> None:
        """Отметить PR review как в обработке."""
        self.pr_reviews.update({
            "status": PRReviewStatus.REVIEWING,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def set_pr_review_completed(self, doc_id: int, review_results: list, all_passed: bool) -> None:
        """Отметить PR review как завершённый.
        
        Args:
            doc_id: ID записи
            review_results: [{file, issue_solved, notes}]
            all_passed: True если все файлы прошли review
        """
        status = PRReviewStatus.APPROVED if all_passed else PRReviewStatus.REJECTED
        self.pr_reviews.update({
            "status": status,
            "review_results": review_results,
            "error": None,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def set_pr_review_failed(self, doc_id: int, error: str) -> None:
        """Отметить PR review как неудачный."""
        review = self.pr_reviews.get(doc_id=doc_id)
        attempts = (review.get("attempts", 0) + 1) if review else 1
        self.pr_reviews.update({
            "status": PRReviewStatus.FAILED,
            "error": error,
            "attempts": attempts,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
    
    def increment_pr_review_attempts(self, doc_id: int) -> int:
        """Увеличить счётчик попыток PR review."""
        review = self.pr_reviews.get(doc_id=doc_id)
        attempts = (review.get("attempts", 0) + 1) if review else 1
        self.pr_reviews.update({
            "attempts": attempts,
            "updated_at": datetime.now().isoformat()
        }, doc_ids=[doc_id])
        return attempts

    def get_tasks(self) -> list:
        """Получить все задачи, отсортированные по приоритету."""
        results = self.issues.all()
        for r in results:
            r['doc_id'] = r.doc_id
        # Сортируем задачи по приоритету в порядке убывания
        return sorted(results, key=lambda x: x.get('priority', 0), reverse=True)


# Singleton instance
db = IssueDB()