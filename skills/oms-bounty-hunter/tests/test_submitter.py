import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.submitter import BountySubmitter


class TestBountySubmitter:
    def test_init_default(self):
        submitter = BountySubmitter()
        assert submitter.token == "mock_token"
    
    def test_init_with_token(self):
        submitter = BountySubmitter(github_token="my_token")
        assert submitter.token == "my_token"
    
    def test_submit_pr(self):
        submitter = BountySubmitter()
        bounty = {
            "issue_number": 123,
            "title": "Fix bug"
        }
        proposal = "My solution"
        
        result = submitter.submit_pr("owner/repo", bounty, proposal)
        
        assert "pr_number" in result
        assert "url" in result
        assert result["status"] == "opened"
        assert "owner/repo" in result["url"]
    
    def test_submit_pr_invalid_repo(self):
        submitter = BountySubmitter()
        bounty = {"issue_number": 123}
        
        with pytest.raises(ValueError):
            submitter.submit_pr("invalid_repo", bounty, "proposal")
    
    def test_submit_pr_missing_issue(self):
        submitter = BountySubmitter()
        bounty = {}
        
        with pytest.raises(ValueError):
            submitter.submit_pr("owner/repo", bounty, "proposal")
    
    def test_check_eligibility_open(self):
        submitter = BountySubmitter()
        bounty = {
            "status": "open",
            "assignee": None,
            "eligibility": ["open"]
        }
        
        assert submitter.check_eligibility("owner/repo", bounty) is True
    
    def test_check_eligibility_not_open(self):
        submitter = BountySubmitter()
        bounty = {
            "status": "closed",
            "assignee": None
        }
        
        assert submitter.check_eligibility("owner/repo", bounty) is False
    
    def test_check_eligibility_assigned(self):
        submitter = BountySubmitter()
        bounty = {
            "status": "open",
            "assignee": "someone"
        }
        
        assert submitter.check_eligibility("owner/repo", bounty) is False
    
    def test_check_eligibility_expired(self):
        submitter = BountySubmitter()
        bounty = {
            "status": "open",
            "assignee": None,
            "deadline": datetime.now() - timedelta(days=1)
        }
        
        assert submitter.check_eligibility("owner/repo", bounty) is False
    
    def test_get_pr_status(self):
        submitter = BountySubmitter()
        result = submitter.get_pr_status("owner/repo", 123)
        
        assert result["pr_number"] == 123
        assert result["repo"] == "owner/repo"
        assert "status" in result
        assert "review_status" in result
    
    def test_claim_bounty(self):
        submitter = BountySubmitter()
        result = submitter.claim_bounty("owner/repo", 123)
        
        assert result["success"] is True
        assert result["repo"] == "owner/repo"
        assert result["issue_number"] == 123
    
    def test_withdraw_pr(self):
        submitter = BountySubmitter()
        result = submitter.withdraw_pr("owner/repo", 123)
        
        assert result["success"] is True
        assert result["pr_number"] == 123
    
    def test_check_reward_status(self):
        submitter = BountySubmitter()
        result = submitter.check_reward_status("owner/repo", 123)
        
        assert result["pr_number"] == 123
        assert result["reward_status"] == "pending"
    
    def test_validate_proposal_valid(self):
        submitter = BountySubmitter()
        proposal = """
Solution description here, longer than 100 characters to pass validation.
This is a solution for the bounty task.

Implementation approach:
1. Step one
2. Step two

- [x] Task 1
- [x] Task 2

Closes #123
"""
        result = submitter.validate_proposal(proposal)
        
        assert result["valid"] is True
        assert result["score"] > 0
    
    def test_validate_proposal_invalid(self):
        submitter = BountySubmitter()
        proposal = "Too short"
        
        result = submitter.validate_proposal(proposal)
        
        assert result["valid"] is False
        assert len(result["issues"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
