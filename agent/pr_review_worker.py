"""PR Review Worker - фоновый процесс для review Pull Requests"""
import os
import time
import signal
import sys
from dotenv import load_dotenv

from database import db, PRReviewStatus
from pr_reviewer import review_pr_files

load_dotenv()

WORKER_INTERVAL = int(os.getenv("WORKER_INTERVAL", "5"))  # секунды
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))


class PRReviewWorker:
    """Фоновый воркер для review PR"""
    
    def __init__(self):
        self.running = False
        self.processed_count = 0
        self.failed_count = 0
    
    def start(self):
        """Запускает воркер"""
        self.running = True
        
        # Graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
        print(f"🤖 PR Review Worker started (interval: {WORKER_INTERVAL}s)")
        print(f"   Max attempts per PR: {MAX_ATTEMPTS}")
        print("   Ctrl+C to stop gracefully\n")
        
        try:
            while self.running:
                self._process_batch()
                time.sleep(WORKER_INTERVAL)
        except KeyboardInterrupt:
            print("\n⚠️ Received interrupt signal")
        finally:
            self._cleanup()
    
    def _process_batch(self):
        """Обрабатывает одну порцию PR reviews"""
        pending = db.get_pending_pr_reviews(limit=5)
        
        if not pending:
            # Молча ждём
            return
        
        print(f"\n📊 Found {len(pending)} PR(s) pending review")
        
        for pr_review in pending:
            if not self.running:
                break
            
            doc_id = pr_review['doc_id']
            repo = pr_review['repo']
            pr_number = pr_review['pr_number']
            attempts = pr_review.get('attempts', 0)
            
            # Проверяем лимит попыток
            if attempts >= MAX_ATTEMPTS:
                print(f"❌ PR {repo}#{pr_number} exceeded max attempts ({MAX_ATTEMPTS})")
                db.set_pr_review_failed(doc_id, f"Max attempts ({MAX_ATTEMPTS}) exceeded")
                self.failed_count += 1
                continue
            
            print(f"🔍 Reviewing PR: {repo}#{pr_number} (attempt {attempts + 1}/{MAX_ATTEMPTS})")
            
            # Обновляем статус
            db.set_pr_reviewing(doc_id)
            db.increment_pr_review_attempts(doc_id)
            
            try:
                # Запускаем review
                result = review_pr_files(
                    pr_number=pr_number,
                    repo_name=repo,
                    changed_files=pr_review.get('changed_files', [])
                )
                
                if result.get("success"):
                    review_results = result.get("review_results", [])
                    all_passed = result.get("all_passed", False)
                    
                    db.set_pr_review_completed(doc_id, review_results, all_passed)
                    
                    status_emoji = "✅" if all_passed else "⚠️"
                    print(f"{status_emoji} Review completed: {len(review_results)} file(s) reviewed")
                    print(f"   All passed: {all_passed}")
                    
                    self.processed_count += 1
                else:
                    error = result.get("error", "Unknown error")
                    print(f"❌ Review failed: {error}")
                    db.set_pr_review_failed(doc_id, error)
                    self.failed_count += 1
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Exception during review: {error_msg}")
                db.set_pr_review_failed(doc_id, error_msg)
                self.failed_count += 1
    
    def _handle_shutdown(self, signum, frame):
        """Обработка сигналов остановки"""
        print(f"\n⚠️ Received signal {signum}, stopping gracefully...")
        self.running = False
    
    def _cleanup(self):
        """Очистка перед остановкой"""
        print("\n" + "="*50)
        print("📊 PR Review Worker Summary:")
        print(f"   Reviewed: {self.processed_count}")
        print(f"   Failed: {self.failed_count}")
        print("="*50)
        print("✅ Worker stopped gracefully")


def main():
    """Основная функция"""
    worker = PRReviewWorker()
    try:
        worker.start()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
