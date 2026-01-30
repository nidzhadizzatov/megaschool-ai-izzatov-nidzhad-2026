import os
import time
import signal
import sys
from dotenv import load_dotenv

from database import db, IssueStatus
from issue_solver import process_issue_from_db

load_dotenv()

WORKER_INTERVAL = int(os.getenv("WORKER_INTERVAL", "5"))  # секунды
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))


class Worker:
    """Фоновый воркер для обработки issues"""
    
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
        
        print("=" * 60)
        print("🚀 Worker started")
        print(f"   Checking for issues every {WORKER_INTERVAL} seconds")
        print(f"   Max attempts per issue: {MAX_ATTEMPTS}")
        print("   Press Ctrl+C to stop")
        print("=" * 60)
        
        while self.running:
            try:
                self._process_pending()
            except Exception as e:
                print(f"❌ Worker error: {e}")
            
            # Ждём перед следующей проверкой
            for _ in range(WORKER_INTERVAL):
                if not self.running:
                    break
                time.sleep(1)
        
        print("\n" + "=" * 60)
        print("👋 Worker stopped")
        print(f"   Processed: {self.processed_count}")
        print(f"   Failed: {self.failed_count}")
        print("=" * 60)
    
    def _handle_shutdown(self, signum, frame):
        """Обрабатывает сигнал завершения"""
        print("\n⚠️ Shutdown signal received, finishing current task...")
        self.running = False
    
    def _process_pending(self):
        """Обрабатывает pending issues"""
        pending = db.get_pending_issues(limit=1)
        
        if not pending:
            return
        
        issue_data = pending[0]
        doc_id = issue_data.get('doc_id')
        repo = issue_data.get('repo')
        issue_number = issue_data.get('issue_number')
        attempts = issue_data.get('attempts', 0)
        
        # Проверяем лимит попыток
        if attempts >= MAX_ATTEMPTS:
            print(f"⚠️ Issue #{issue_number} exceeded max attempts ({MAX_ATTEMPTS})")
            db.set_failed(doc_id, f"Max attempts ({MAX_ATTEMPTS}) exceeded")
            return
        
        print(f"\n{'='*60}")
        print(f"📋 Processing: {repo}#{issue_number} (attempt {attempts + 1}/{MAX_ATTEMPTS})")
        print(f"{'='*60}")
        
        # Увеличиваем счётчик попыток
        db.increment_attempts(doc_id)
        
        try:
            total = issue_data.get('total', 0)  # Assuming this is how total tasks are fetched
            done = issue_data.get('done', 0)    # Assuming this is how done tasks are fetched
            completion_rate = (done / total * 100) if total > 0 else 0  # Zero-check before division
            print(f"Completion Rate: {completion_rate}%")
            pr_number = process_issue_from_db(issue_data)
            
            if pr_number:
                self.processed_count += 1
                print(f"✅ Successfully created PR #{pr_number}")
            else:
                self.failed_count += 1
                print(f"⚠️ No changes made for issue #{issue_number}")
                
        except Exception as e:
            self.failed_count += 1
            print(f"❌ Failed to process issue #{issue_number}: {e}")
            db.set_failed(doc_id, str(e))
    
    def process_one(self):
        """Обрабатывает один pending issue и завершается"""
        pending = db.get_pending_issues(limit=1)
        
        if not pending:
            print("ℹ️ No pending issues")
            return None
        
        issue_data = pending[0]
        
        try:
            return process_issue_from_db(issue_data)
        except Exception as e:
            print(f"❌ Failed: {e}")
            return None


def run_worker():
    """Запуск воркера"""
    worker = Worker()
    worker.start()


def run_once():
    """Обработать один issue и завершиться"""
    worker = Worker()
    return worker.process_one()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Issue Solver Worker")
    parser.add_argument(
        "--once", 
        action="store_true",
        help="Process one issue and exit"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=WORKER_INTERVAL,
        help=f"Check interval in seconds (default: {WORKER_INTERVAL})"
    )
    
    args = parser.parse_args()
    
    if args.once:
        result = run_once()
        sys.exit(0 if result else 1)
    else:
        if args.interval:
            import worker
            worker.WORKER_INTERVAL = args.interval
        run_worker()


if __name__ == "__main__":
    main()