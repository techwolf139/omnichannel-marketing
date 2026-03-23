"""Tests for TrendingMatcher"""

import pytest
from scripts.trending import TrendingMatcher


class TestTrendingMatcher:
    """Test cases for TrendingMatcher"""
    
    @pytest.fixture
    def matcher(self):
        return TrendingMatcher()
    
    def test_match_trending_topics_returns_list(self, matcher):
        """Test match_trending_topics returns a list"""
        content = "秋冬护肤保湿补水推荐"
        result = matcher.match_trending_topics(content)
        assert isinstance(result, list)
    
    def test_match_trending_topics_structure(self, matcher):
        """Test result has correct structure"""
        content = "双十一护肤品推荐"
        result = matcher.match_trending_topics(content)
        
        for topic in result:
            assert "id" in topic
            assert "topic" in topic
            assert "category" in topic
            assert "heat_score" in topic
            assert "relevance_score" in topic
            assert isinstance(topic["heat_score"], (int, float))
            assert isinstance(topic["relevance_score"], (int, float))
    
    def test_match_trending_topics_relevance_score_range(self, matcher):
        """Test relevance scores are within valid range"""
        content = "护肤美妆产品"
        result = matcher.match_trending_topics(content)
        
        for topic in result:
            assert 0 <= topic["relevance_score"] <= 1
            assert 0 <= topic["heat_score"] <= 1
    
    def test_match_trending_topics_sorted_by_combined_score(self, matcher):
        """Test results are sorted by combined score"""
        content = "护肤产品推荐"
        result = matcher.match_trending_topics(content, top_n=5)
        
        if len(result) >= 2:
            for i in range(len(result) - 1):
                score_i = result[i]["heat_score"] * result[i]["relevance_score"]
                score_j = result[i + 1]["heat_score"] * result[i + 1]["relevance_score"]
                assert score_i >= score_j
    
    def test_match_trending_topics_respects_top_n(self, matcher):
        """Test top_n parameter is respected"""
        content = "护肤美妆健康购物"
        result = matcher.match_trending_topics(content, top_n=3)
        assert len(result) <= 3
    
    def test_fetch_platform_trending_returns_list(self, matcher):
        """Test fetch_platform_trending returns a list"""
        result = matcher.fetch_platform_trending("weibo")
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_fetch_platform_trending_structure(self, matcher):
        """Test trending data has correct structure"""
        result = matcher.fetch_platform_trending("weibo")
        
        for topic in result:
            assert "id" in topic
            assert "name" in topic
            assert "category" in topic
            assert "heat_score" in topic
            assert "platform" in topic
            assert topic["platform"] == "weibo"
    
    def test_fetch_platform_trending_sorted_by_heat(self, matcher):
        """Test trending topics are sorted by heat score"""
        result = matcher.fetch_platform_trending("weibo")
        
        if len(result) >= 2:
            for i in range(len(result) - 1):
                assert result[i]["heat_score"] >= result[i + 1]["heat_score"]
    
    def test_fetch_platform_trending_filter_by_category(self, matcher):
        """Test category filter works"""
        result = matcher.fetch_platform_trending("weibo", category="美妆")
        
        for topic in result:
            assert topic["category"] == "美妆"
    
    def test_extract_keywords(self, matcher):
        """Test keyword extraction"""
        content = "护肤精华推荐美妆产品"
        keywords = matcher._extract_keywords(content)
        
        assert isinstance(keywords, list)
        # Should extract Chinese words
        assert all(isinstance(k, str) for k in keywords)
    
    def test_calculate_relevance(self, matcher):
        """Test relevance calculation"""
        content = "双十一护肤品"
        topic = {"name": "双十一攻略", "category": "购物"}
        
        relevance = matcher._calculate_relevance(content, topic)
        assert isinstance(relevance, float)
        assert 0 <= relevance <= 1
    
    def test_calculate_relevance_with_matching_topic(self, matcher):
        """Test higher relevance when topic matches content"""
        topic = {"name": "秋冬护肤", "category": "美妆"}
        
        content_with_match = "秋冬护肤保湿很重要"
        content_without_match = "科技数码产品推荐"
        
        relevance_with = matcher._calculate_relevance(content_with_match, topic)
        relevance_without = matcher._calculate_relevance(content_without_match, topic)
        
        assert relevance_with > relevance_without
