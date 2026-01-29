#!/usr/bin/env python3
"""CLI - Command Line Interface для Coding Agent"""
import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()


def cmd_start_server(args):
    """Запуск webhook сервера"""
    from server import run_server
    run_server()


def cmd_start_worker(args):
    """Запуск issue воркера"""
    from worker import run_worker, WORKER_INTERVAL
    
    if args.interval:
        import worker
        worker.WORKER_INTERVAL = args.interval
    
    run_worker()


def cmd_start_pr_worker(args):
    """Запуск PR review воркера"""
    from pr_review_worker import PRReviewWorker
    
    worker = PRReviewWorker()
    worker.start()


def cmd_process_issue(args):
    """Обработка конкретного issue"""
    from issue_solver import IssueSolver
    
    solver = IssueSolver(args.repo)
    pr_number = solver.solve_issue(args.issue_number)
    
    if pr_number:
        print(f"\n🎉 Created PR #{pr_number}")
        return 0
    else:
        print("\n⚠️ No changes made")
        return 1


def cmd_review_pr(args):
    """Ревью PR"""
    from pr_reviewer import review_pr
    
    result = review_pr(args.pr_number, args.repo)
    
    if result["approved"]:
        print("✅ PR approved")
        return 0
    else:
        print("❌ PR needs changes")
        return 1


def cmd_fix_pr(args):
    """Исправление PR на основе ревью"""
    print(f"🔧 Fixing PR #{args.pr_number} in {args.repo}")
    print("⚠️ Not implemented yet")
    return 1


def cmd_list_issues(args):
    """Список issues в очереди"""
    from database import db
    
    stats = db.get_stats()
    issues = db.get_all()
    
    print("\n📊 Statistics:")
    print(f"   Pending:    {stats['pending']}")
    print(f"   Processing: {stats['processing']}")
    print(f"   Completed:  {stats['completed']}")
    print(f"   Failed:     {stats['failed']}")
    print(f"   Total:      {stats['total']}")
    
    if issues:
        print("\n📋 Issues:")
        for issue in issues:
            status_emoji = {
                "pending": "⏳",
                "processing": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(issue.get("status"), "❓")
            
            print(f"   {status_emoji} {issue.get('repo')}#{issue.get('issue_number')} - {issue.get('title', 'No title')[:50]}")
            if issue.get("pr_number"):
                print(f"      └─ PR #{issue.get('pr_number')}")
            if issue.get("error"):
                print(f"      └─ Error: {issue.get('error')[:50]}")
    
    return 0


def cmd_add_issue(args):
    """Добавить issue в очередь вручную"""
    from database import db
    
    doc_id = db.add_issue(
        repo_full_name=args.repo,
        issue_number=args.issue_number,
        title=args.title or f"Issue #{args.issue_number}",
        body=args.body or ""
    )
    
    print(f"✅ Added issue #{args.issue_number} to queue (doc_id: {doc_id})")
    return 0


def cmd_run_all(args):
    """Запуск сервера и обоих воркеров вместе"""
    import threading
    from server import run_server
    from worker import run_worker
    from pr_review_worker import PRReviewWorker
    
    # Запускаем issue воркер в отдельном потоке
    issue_worker_thread = threading.Thread(target=run_worker, daemon=True, name="IssueWorker")
    issue_worker_thread.start()
    
    # Запускаем PR review воркер в отдельном потоке
    def run_pr_worker():
        pr_worker = PRReviewWorker()
        pr_worker.start()
    
    pr_worker_thread = threading.Thread(target=run_pr_worker, daemon=True, name="PRReviewWorker")
    pr_worker_thread.start()
    
    # Запускаем сервер в основном потоке
    print("🚀 Starting all services:")
    print("   - Webhook server")
    print("   - Issue solver worker")
    print("   - PR review worker\n")
    run_server()


def main():
    parser = argparse.ArgumentParser(
        description="🤖 Coding Agent CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start webhook server
  python cli.py start-server
  
  # Start worker (checks every 5 seconds)
  python cli.py start-worker
  
  # Process specific issue
  python cli.py process-issue myuser/myrepo 1
  
  # Review a PR
  python cli.py review-pr myuser/myrepo 1
  
  # List queued issues
  python cli.py list-issues
  
  # Add issue to queue manually
  python cli.py add-issue myuser/myrepo 1 --title "Fix bug"
  
  # Run server and worker together
  python cli.py run
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # start-server
    p_server = subparsers.add_parser("start-server", help="Start webhook server")
    p_server.set_defaults(func=cmd_start_server)
    
    # start-worker
    p_worker = subparsers.add_parser("start-worker", help="Start issue solver worker")
    p_worker.add_argument("--interval", type=int, help="Check interval in seconds")
    p_worker.set_defaults(func=cmd_start_worker)
    
    # start-pr-worker
    p_pr_worker = subparsers.add_parser("start-pr-worker", help="Start PR review worker")
    p_pr_worker.set_defaults(func=cmd_start_pr_worker)
    
    # process-issue
    p_process = subparsers.add_parser("process-issue", help="Process a specific issue")
    p_process.add_argument("repo", help="Repository (owner/repo)")
    p_process.add_argument("issue_number", type=int, help="Issue number")
    p_process.set_defaults(func=cmd_process_issue)
    
    # review-pr
    p_review = subparsers.add_parser("review-pr", help="Review a pull request")
    p_review.add_argument("repo", help="Repository (owner/repo)")
    p_review.add_argument("pr_number", type=int, help="PR number")
    p_review.set_defaults(func=cmd_review_pr)
    
    # fix-pr
    p_fix = subparsers.add_parser("fix-pr", help="Fix PR based on review")
    p_fix.add_argument("repo", help="Repository (owner/repo)")
    p_fix.add_argument("pr_number", type=int, help="PR number")
    p_fix.set_defaults(func=cmd_fix_pr)
    
    # list-issues
    p_list = subparsers.add_parser("list-issues", help="List queued issues")
    p_list.set_defaults(func=cmd_list_issues)
    
    # add-issue
    p_add = subparsers.add_parser("add-issue", help="Add issue to queue manually")
    p_add.add_argument("repo", help="Repository (owner/repo)")
    p_add.add_argument("issue_number", type=int, help="Issue number")
    p_add.add_argument("--title", help="Issue title")
    p_add.add_argument("--body", help="Issue body")
    p_add.set_defaults(func=cmd_add_issue)
    
    # run (server + worker)
    p_run = subparsers.add_parser("run", help="Run server and worker together")
    p_run.set_defaults(func=cmd_run_all)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
