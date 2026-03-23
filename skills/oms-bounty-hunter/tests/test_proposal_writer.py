import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.proposal_writer import ProposalWriter


class TestProposalWriter:
    def test_init(self):
        writer = ProposalWriter()
        assert writer is not None
    
    def test_write_proposal(self):
        writer = ProposalWriter()
        bounty = {
            "repo": "owner/repo",
            "issue_number": 123,
            "title": "Fix bug",
            "platform": "github",
            "labels": ["bug"],
            "skills_required": ["Python"]
        }
        solution = "This is my solution"
        
        proposal = writer.write_proposal(bounty, solution)
        
        assert "解决方案" in proposal
        assert "实现思路" in proposal
        assert solution in proposal
        assert "123" in proposal
    
    def test_generate_pr_description(self):
        writer = ProposalWriter()
        bounty = {
            "repo": "owner/repo",
            "issue_number": 456,
            "title": "Add feature",
            "platform": "github",
            "labels": ["enhancement"]
        }
        solution = "Feature implementation"
        
        description = writer.generate_pr_description(bounty, solution)
        assert solution in description
        assert "456" in description
    
    def test_generate_implementation_plan(self):
        writer = ProposalWriter()
        bounty = {
            "title": "Test Task",
            "skills_required": ["Python", "React"]
        }
        
        plan = writer.generate_implementation_plan(bounty)
        assert "实施计划" in plan
        assert "Python" in plan
        assert "React" in plan
        assert "Phase 1" in plan
    
    def test_estimate_effort_easy(self):
        writer = ProposalWriter()
        bounty = {
            "labels": ["good first issue"],
            "title": "Simple task"
        }
        
        effort = writer.estimate_effort(bounty)
        assert effort["difficulty"] == "easy"
        assert effort["skill_level"] == "beginner"
    
    def test_estimate_effort_hard(self):
        writer = ProposalWriter()
        bounty = {
            "labels": ["complex"],
            "title": "Hard task"
        }
        
        effort = writer.estimate_effort(bounty)
        assert effort["difficulty"] == "hard"
        assert effort["skill_level"] == "advanced"
    
    def test_estimate_effort_documentation(self):
        writer = ProposalWriter()
        bounty = {
            "labels": ["documentation"],
            "title": "Update docs"
        }
        
        effort = writer.estimate_effort(bounty)
        assert effort["estimated_days"] < 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
