"""Tests for stats_fetcher module."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.stats_fetcher import StatsFetcher


class TestStatsFetcher:
    """Test cases for StatsFetcher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.fetcher = StatsFetcher()
    
    def test_get_note_stats_success(self):
        """Test getting note stats successfully."""
        stats = self.fetcher.get_note_stats("note_123456")
        
        assert isinstance(stats, dict)
        assert stats["note_id"] == "note_123456"
        assert "exposure" in stats
        assert "read" in stats
        assert "like" in stats
        assert "collect" in stats
        assert "comment" in stats
        assert "share" in stats
        assert "updated_at" in stats
    
    def test_get_note_stats_invalid_id(self):
        """Test getting stats with invalid note_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            self.fetcher.get_note_stats("")
        
        assert "Invalid note_id" in str(exc_info.value)
    
    def test_get_batch_stats_success(self):
        """Test batch stats fetch."""
        note_ids = ["note_1", "note_2", "note_3"]
        stats_list = self.fetcher.get_batch_stats(note_ids)
        
        assert isinstance(stats_list, list)
        assert len(stats_list) == 3
        
        for i, stats in enumerate(stats_list):
            assert stats["note_id"] == note_ids[i]
    
    def test_get_batch_stats_too_many(self):
        """Test batch stats with too many IDs raises error."""
        note_ids = [f"note_{i}" for i in range(60)]
        
        with pytest.raises(ValueError) as exc_info:
            self.fetcher.get_batch_stats(note_ids)
        
        assert "Max 50" in str(exc_info.value)
    
    def test_get_stats_trend(self):
        """Test getting stats trend."""
        trend = self.fetcher.get_stats_trend("note_123", days=7)
        
        assert isinstance(trend, list)
        assert len(trend) == 7
        
        for day_data in trend:
            assert "date" in day_data
            assert "exposure" in day_data
            assert "like" in day_data
            assert "comment" in day_data
    
    def test_get_stats_trend_bounds(self):
        """Test trend days parameter bounds."""
        # Test days < 1
        trend = self.fetcher.get_stats_trend("note_123", days=0)
        assert len(trend) >= 1
        
        # Test days > 30
        trend = self.fetcher.get_stats_trend("note_123", days=40)
        assert len(trend) <= 30
    
    def test_get_account_stats(self):
        """Test getting account stats."""
        stats = self.fetcher.get_account_stats()
        
        assert isinstance(stats, dict)
        assert "account_id" in stats
        assert "followers" in stats
        assert "total_notes" in stats
        assert "total_exposure" in stats
        assert "total_likes" in stats
        assert "engagement_rate" in stats
    
    def test_get_account_stats_with_id(self):
        """Test getting account stats with specific ID."""
        stats = self.fetcher.get_account_stats("custom_account_id")
        
        assert stats["account_id"] == "custom_account_id"
    
    def test_calculate_engagement_rate(self):
        """Test engagement rate calculation."""
        stats = {
            "exposure": 10000,
            "like": 500,
            "collect": 200,
            "comment": 50
        }
        
        rate = self.fetcher.calculate_engagement_rate(stats)
        
        # (500 + 200 + 50) / 10000 = 0.075
        assert rate == 0.075
    
    def test_calculate_engagement_rate_zero_exposure(self):
        """Test engagement rate with zero exposure."""
        stats = {
            "exposure": 0,
            "like": 100,
            "collect": 50,
            "comment": 20
        }
        
        rate = self.fetcher.calculate_engagement_rate(stats)
        assert rate == 0.0
