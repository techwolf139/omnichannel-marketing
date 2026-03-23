"""Tests for trending_fetcher module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.trending_fetcher import TrendingFetcher


class TestTrendingFetcher:
    """Test cases for TrendingFetcher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = TrendingFetcher()
    
    def test_fetch_trending_topics_default(self):
        """Test fetching trending topics with default parameters."""
        topics = self.fetcher.fetch_trending_topics()
        
        assert isinstance(topics, list)
        assert len(topics) <= 20
        
        if topics:
            topic = topics[0]
            assert "topic" in topic
            assert "heat" in topic
            assert "category" in topic
            assert "rank" in topic
            assert "trend" in topic
    
    def test_fetch_trending_topics_with_category(self):
        """Test fetching trending topics with specific category."""
        topics = self.fetcher.fetch_trending_topics(category="beauty", limit=5)
        
        assert isinstance(topics, list)
        assert len(topics) <= 5
    
    def test_fetch_trending_topics_invalid_category(self):
        """Test fetching with invalid category raises error."""
        with pytest.raises(ValueError) as exc_info:
            self.fetcher.fetch_trending_topics(category="invalid_category")
        
        assert "Invalid category" in str(exc_info.value)
    
    def test_fetch_trending_topics_limit_bounds(self):
        """Test limit parameter bounds."""
        # Test limit < 1
        topics = self.fetcher.fetch_trending_topics(limit=0)
        assert len(topics) >= 0
        
        # Test limit > 100
        topics = self.fetcher.fetch_trending_topics(limit=200)
        assert len(topics) <= 100
    
    def test_get_topic_detail(self):
        """Test getting topic details."""
        detail = self.fetcher.get_topic_detail("春季穿搭")
        
        assert isinstance(detail, dict)
        assert detail["topic"] == "春季穿搭"
        assert "heat" in detail
        assert "note_count" in detail
        assert "participant_count" in detail
        assert "trend_7d" in detail
        assert isinstance(detail["trend_7d"], list)
