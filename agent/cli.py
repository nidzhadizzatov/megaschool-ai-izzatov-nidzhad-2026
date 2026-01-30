import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from issue_solver import IssueSolver
from pr_reviewer import review_pr_files

def process_issue(repo_full_name: str, issue_number: int):
    """Обрабатывает issue и создаёт PR.\n    \n    Args:\n        repo_full_name: owner/repo\n        issue_number: Номер issue\n    """
    print(f"🚀 Processing issue #{issue_number} from {repo_full_name}")
    
    try:
        solver = IssueSolver(repo_full_name)
        pr_number = solver.solve_issue(issue_number)
        
        if pr_number:
            print(f"✅ Successfully created PR #{pr_number}")
            return 0
        else:
            print("⚠️ No changes needed for this issue")
            return 0
    except Exception as e:
        print(f"❌ Error processing issue: {e}")
        return 1

def review_pr(repo_full_name: str, pr_number: int):
    """Выполняет AI review Pull Request.\n    \n    Args:\n        repo_full_name: owner/repo\n        pr_number: Номер PR\n    """
    print(f"🔍 Reviewing PR #{pr_number} from {repo_full_name}")
    
    try:
        result = review_pr_files(pr_number, repo_name=repo_full_name)
        
        if result.get("success"):
            if result.get("all_passed"):
                print("✅ All checks passed")
                return 0
            else:
                print("⚠️ Review found issues")
                return 0
        else:
            print(f"❌ Review failed: {result.get('error')}")
            return 1
    except Exception as e:
        print(f"❌ Error reviewing PR: {e}")
        return 1

def get_task_stats():
    # Placeholder for the actual logic to get task stats
    done = 0  # Example value
    total = 0  # Example value
    
    if total == 0:
        return 0  # Return 0 completion rate if no tasks exist
    completion_rate = (done / total) * 100  # Division by zero when total=0!
    return completion_rate


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Coding Agent CLI - автоматизация SDLC в GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Обработать issue
  python cli.py process-issue owner/repo 123
  
  # Сделать review PR
  python cli.py review-pr owner/repo 456
  
  # Использование в GitHub Actions
  python cli.py process-issue ${{ github.repository }} ${{ github.event.issue.number }}
"""
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда: process-issue
    process_parser = subparsers.add_parser(
        'process-issue',
        help='Обработать issue и создать PR'
    )
    process_parser.add_argument(
        'repo',
        help='Репозиторий в формате owner/repo'
    )
    process_parser.add_argument(
        'issue_number',
        type=int,
        help='Номер issue'
    )
    
    # Команда: review-pr
    review_parser = subparsers.add_parser(
        'review-pr',
        help='Выполнить AI review Pull Request'
    )
    review_parser.add_argument(
        'repo',
        help='Репозиторий в формате owner/repo'
    )
    review_parser.add_argument(
        'pr_number',
        type=int,
        help='Номер PR'
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Выполняем команду
    if args.command == 'process-issue':
        return process_issue(args.repo, args.issue_number)
    elif args.command == 'review-pr':
        return review_pr(args.repo, args.pr_number)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())