import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.bounty_finder import BountyFinder


class TestBountyFinder:
    def test_init_default(self):
        finder = BountyFinder()
        assert finder.github_token == ""
    
    def test_init_with_token(self):
        finder = BountyFinder(github_token="test_token")
        assert finder.github_token == "test_token"
    
    def test_find_bounties_returns_list(self):
        finder = BountyFinder()
        bounties = finder.find_bounties()
        assert isinstance(bounties, list)
        assert len(bounties) > 0
    
    def test_find_bounties_with_keywords(self):
        finder = BountyFinder()
        bounties = finder.find_bounties(keywords=["python"])
        assert isinstance(bounties, list)
    
    def test_find_bounties_with_reward_range(self):
        finder = BountyFinder()
        bounties = finder.find_bounties(
            reward_range={"min": 50, "max": 500, "currency": "USD"}
        )
        assert isinstance(bounties, list)
    
    def test_get_bounty_details(self):
        finder = BountyFinder()
        details = finder.get_bounty_details("owner/repo", 123)
        
        assert details["repo"] == "owner/repo"
        assert details["issue_number"] == 123
        assert "title" in details
        assert "description" in details
        assert "reward" in details
        assert "eligibility" in details
        assert "status" in details
    
    def test_parse_amount_usd(self):
        finder = BountyFinder()
        assert finder._parse_amount("$100") == 100.0
        assert finder._parse_amount("$1,000.50") == 1000.5
        assert finder._parse_amount("$0") == 0.0
    
    def test_parse_amount_eth(self):
        finder = BountyFinder()
        assert finder._parse_amount("0.5 ETH") == 0.5
        assert finder._parse_amount("1.25 BTC") == 1.25
    
    def test_parse_amount_invalid(self):
        finder = BountyFinder()
        assert finder._parse_amount("") == 0.0
        assert finder._parse_amount("abc") == 0.0
    
    def test_convert_currency(self):
        finder = BountyFinder()
        result = finder._convert_currency(1.0, "ETH", "USD")
        assert result == 3000.0
        
        result = finder._convert_currency(60000.0, "USD", "BTC")
        assert result == 1.0
    
    def test_build_search_query(self):
        finder = BountyFinder()
        query = finder._build_search_query(["python", "flask"])
        assert "python" in query
        assert "flask" in query
        assert "bounty" in query
    
    def test_build_search_query_empty(self):
        finder = BountyFinder()
        query = finder._build_search_query()
        assert "bounty" in query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
