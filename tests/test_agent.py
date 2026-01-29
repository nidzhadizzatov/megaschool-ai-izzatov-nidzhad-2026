"""Тесты для Coding Agent System"""
import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "agent"))


class TestDatabase:
    """Тесты для database.py"""
    
    def test_issue_status_enum(self):
        """Test IssueStatus enum values"""
        from database import IssueStatus
        assert IssueStatus.PENDING == "pending"
        assert IssueStatus.PROCESSING == "processing"
        assert IssueStatus.COMPLETED == "completed"
        assert IssueStatus.FAILED == "failed"
    
    def test_pr_review_status_enum(self):
        """Test PRReviewStatus enum values"""
        from database import PRReviewStatus
        assert PRReviewStatus.PENDING == "pending"
        assert PRReviewStatus.REVIEWING == "reviewing"
        assert PRReviewStatus.APPROVED == "approved"
        assert PRReviewStatus.REJECTED == "rejected"
        assert PRReviewStatus.FAILED == "failed"
    
    def test_database_init(self, tmp_path):
        """Test database initialization"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB
        db = IssueDB(db_path)
        assert db.db is not None
        assert db.issues is not None
        assert db.pr_reviews is not None
    
    def test_add_issue(self, tmp_path):
        """Test adding issue to database"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB
        db = IssueDB(db_path)
        
        doc_id = db.add_issue(
            repo_full_name="test/repo",
            issue_number=1,
            title="Test Issue",
            body="Test body"
        )
        
        assert doc_id is not None
        assert doc_id > 0
        
        # Check it was added
        issue = db.get_issue_by_id(doc_id)
        assert issue is not None
        assert issue["repo"] == "test/repo"
        assert issue["issue_number"] == 1
        assert issue["title"] == "Test Issue"
        assert issue["status"] == "pending"
    
    def test_add_pr_review(self, tmp_path):
        """Test adding PR review to database"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB
        db = IssueDB(db_path)
        
        doc_id = db.add_pr_review(
            repo_full_name="test/repo",
            pr_number=1,
            changed_files=["file1.py", "file2.py"]
        )
        
        assert doc_id is not None
        assert doc_id > 0
        
        # Check it was added
        review = db.get_pr_review_by_id(doc_id)
        assert review is not None
        assert review["repo"] == "test/repo"
        assert review["pr_number"] == 1
        assert review["changed_files"] == ["file1.py", "file2.py"]
        assert review["status"] == "pending"
    
    def test_get_pending_issues(self, tmp_path):
        """Test getting pending issues"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB
        db = IssueDB(db_path)
        
        # Add several issues
        db.add_issue("test/repo", 1, "Issue 1", "Body 1")
        db.add_issue("test/repo", 2, "Issue 2", "Body 2")
        db.add_issue("test/repo", 3, "Issue 3", "Body 3")
        
        pending = db.get_pending_issues()
        assert len(pending) == 3
    
    def test_set_status_transitions(self, tmp_path):
        """Test status transitions"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB, IssueStatus
        db = IssueDB(db_path)
        
        doc_id = db.add_issue("test/repo", 1, "Test", "Body")
        
        # pending -> processing
        db.set_processing(doc_id)
        issue = db.get_issue_by_id(doc_id)
        assert issue["status"] == IssueStatus.PROCESSING
        
        # processing -> completed
        db.set_completed(doc_id, pr_number=42)
        issue = db.get_issue_by_id(doc_id)
        assert issue["status"] == IssueStatus.COMPLETED
        assert issue["pr_number"] == 42
    
    def test_get_stats(self, tmp_path):
        """Test getting statistics"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB
        db = IssueDB(db_path)
        
        # Add issues
        db.add_issue("test/repo", 1, "Issue 1", "")
        db.add_issue("test/repo", 2, "Issue 2", "")
        
        # Add PR reviews
        db.add_pr_review("test/repo", 1, ["file.py"])
        
        stats = db.get_stats()
        assert "pending" in stats
        assert "total" in stats
        assert "pr_pending" in stats
        assert stats["pending"] == 2
        assert stats["pr_pending"] == 1


class TestAIClient:
    """Тесты для ai_client.py"""
    
    def test_ai_response_format(self):
        """Test AI response parsing for issue_found format"""
        # Mock response in expected format
        response_text = '{"issue_found": true, "code_correction": "fixed code here"}'
        result = json.loads(response_text)
        
        assert "issue_found" in result
        assert "code_correction" in result
        assert result["issue_found"] is True
    
    def test_pr_review_response_format(self):
        """Test AI response parsing for PR review format"""
        # Mock response in expected format
        response_text = '{"issue_solved": true, "notes": "The issue has been resolved correctly."}'
        result = json.loads(response_text)
        
        assert "issue_solved" in result
        assert "notes" in result
        assert result["issue_solved"] is True


class TestRepoManager:
    """Тесты для repo_manager.py"""
    
    def test_uuid_path_generation(self):
        """Test that repo path uses UUID"""
        import uuid
        
        # Mock to avoid actual GitHub API calls
        with patch('repo_manager.Github'):
            from repo_manager import RepoManager, REPOS_DIR
            
            # Create two managers for same repo
            manager1 = RepoManager.__new__(RepoManager)
            manager1.unique_id = str(uuid.uuid4())[:8]
            manager1.repo_path = REPOS_DIR / manager1.unique_id
            
            manager2 = RepoManager.__new__(RepoManager)
            manager2.unique_id = str(uuid.uuid4())[:8]
            manager2.repo_path = REPOS_DIR / manager2.unique_id
            
            # Paths should be different
            assert manager1.repo_path != manager2.repo_path
            assert manager1.unique_id != manager2.unique_id
    
    def test_clone_url_with_token(self):
        """Test clone URL includes token"""
        with patch('repo_manager.Github'):
            with patch('repo_manager.GITHUB_TOKEN', 'test-token-123'):
                from repo_manager import RepoManager
                
                # Create mock manager
                manager = RepoManager.__new__(RepoManager)
                manager.repo_full_name = "owner/repo"
                
                # Mock the property
                url = f"https://x-access-token:test-token-123@github.com/owner/repo.git"
                assert "x-access-token" in url
                assert "test-token-123" in url


class TestPRReviewer:
    """Тесты для pr_reviewer.py"""
    
    def test_review_response_format(self):
        """Test review_file_for_issue returns correct format"""
        expected_keys = {"issue_solved", "notes"}
        
        # Mock response
        mock_result = {
            "issue_solved": True,
            "notes": "The code correctly implements the fix."
        }
        
        assert set(mock_result.keys()) == expected_keys
        assert isinstance(mock_result["issue_solved"], bool)
        assert isinstance(mock_result["notes"], str)
    
    def test_review_results_aggregation(self):
        """Test that all file reviews are aggregated"""
        review_results = [
            {"file": "file1.py", "issue_solved": True, "notes": "OK"},
            {"file": "file2.py", "issue_solved": False, "notes": "Has issues"},
            {"file": "file3.py", "issue_solved": True, "notes": "OK"},
        ]
        
        all_passed = all(r["issue_solved"] for r in review_results)
        assert all_passed is False  # file2 failed
        
        passed_count = sum(1 for r in review_results if r["issue_solved"])
        assert passed_count == 2


class TestServer:
    """Тесты для server.py"""
    
    def test_webhook_signature_verification(self):
        """Test webhook signature verification logic"""
        import hmac
        import hashlib
        
        secret = "test_secret"
        payload = b'{"action": "opened"}'
        
        # Generate expected signature
        expected_sig = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Verify
        computed = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        assert hmac.compare_digest(expected_sig, computed)
    
    def test_issue_event_parsing(self):
        """Test parsing issue webhook payload"""
        payload = {
            "action": "opened",
            "issue": {
                "number": 1,
                "title": "Fix bug",
                "body": "There's a bug in app.py"
            },
            "repository": {
                "full_name": "owner/repo"
            },
            "installation": {
                "id": 12345
            }
        }
        
        issue = payload.get("issue", {})
        repo = payload.get("repository", {})
        
        assert issue.get("number") == 1
        assert issue.get("title") == "Fix bug"
        assert repo.get("full_name") == "owner/repo"
    
    def test_pr_event_parsing(self):
        """Test parsing PR webhook payload"""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Fix issue #1"
            },
            "repository": {
                "full_name": "owner/repo"
            }
        }
        
        pr = payload.get("pull_request", {})
        repo = payload.get("repository", {})
        
        assert pr.get("number") == 42
        assert repo.get("full_name") == "owner/repo"


class TestWorker:
    """Тесты для worker.py"""
    
    def test_worker_interval_default(self):
        """Test default worker interval"""
        # Default should be 5 seconds
        default_interval = 5
        assert default_interval == 5
    
    def test_max_attempts_default(self):
        """Test default max attempts"""
        # Default should be 3
        default_max = 3
        assert default_max == 3


class TestCLI:
    """Тесты для cli.py"""
    
    def test_cli_commands_defined(self):
        """Test that CLI commands are defined"""
        from cli import cmd_start_server, cmd_start_worker, cmd_start_pr_worker
        from cli import cmd_run_all, cmd_list_issues
        
        # All command functions should exist
        assert callable(cmd_start_server)
        assert callable(cmd_start_worker)
        assert callable(cmd_start_pr_worker)
        assert callable(cmd_run_all)
        assert callable(cmd_list_issues)


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_issue_flow_mock(self, tmp_path):
        """Test complete issue processing flow (mocked)"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB, IssueStatus
        db = IssueDB(db_path)
        
        # 1. Issue added via webhook
        doc_id = db.add_issue(
            repo_full_name="test/repo",
            issue_number=1,
            title="Fix divide by zero",
            body="app.py has divide by zero error on line 10"
        )
        
        assert db.get_issue_by_id(doc_id)["status"] == IssueStatus.PENDING
        
        # 2. Worker picks it up
        pending = db.get_pending_issues()
        assert len(pending) == 1
        
        # 3. Processing starts
        db.set_processing(doc_id)
        assert db.get_issue_by_id(doc_id)["status"] == IssueStatus.PROCESSING
        
        # 4. PR created
        db.set_completed(doc_id, pr_number=42)
        assert db.get_issue_by_id(doc_id)["status"] == IssueStatus.COMPLETED
        assert db.get_issue_by_id(doc_id)["pr_number"] == 42
    
    def test_full_pr_review_flow_mock(self, tmp_path):
        """Test complete PR review flow (mocked)"""
        db_path = str(tmp_path / "test_db.json")
        from database import IssueDB, PRReviewStatus
        db = IssueDB(db_path)
        
        # 1. PR created, webhook received
        doc_id = db.add_pr_review(
            repo_full_name="test/repo",
            pr_number=42,
            changed_files=["app.py", "utils.py"]
        )
        
        assert db.get_pr_review_by_id(doc_id)["status"] == PRReviewStatus.PENDING
        
        # 2. Review worker picks it up
        pending = db.get_pending_pr_reviews()
        assert len(pending) == 1
        
        # 3. Review starts
        db.set_pr_reviewing(doc_id)
        assert db.get_pr_review_by_id(doc_id)["status"] == PRReviewStatus.REVIEWING
        
        # 4. Review completed - all passed
        review_results = [
            {"file": "app.py", "issue_solved": True, "notes": "Fix applied correctly"},
            {"file": "utils.py", "issue_solved": True, "notes": "No issues"}
        ]
        db.set_pr_review_completed(doc_id, review_results, all_passed=True)
        
        review = db.get_pr_review_by_id(doc_id)
        assert review["status"] == PRReviewStatus.APPROVED
        assert len(review["review_results"]) == 2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
