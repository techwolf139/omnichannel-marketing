"""Tests for ContentRewriter"""

import pytest
from scripts.rewriter import ContentRewriter


class TestContentRewriter:
    """Test cases for ContentRewriter"""
    
    @pytest.fixture
    def rewriter(self):
        return ContentRewriter()
    
    @pytest.fixture
    def sample_content(self):
        return "这是一个测试内容，用于展示产品特点。这款产品质量非常好，性价比很高，强烈推荐给大家。"
    
    def test_rewrite_returns_string(self, rewriter, sample_content):
        """Test rewrite_for_platform returns a string"""
        result = rewriter.rewrite_for_platform(sample_content, "wechat")
        assert isinstance(result, str)
    
    def test_rewrite_respects_limits(self, rewriter):
        """Test content is truncated to platform limits"""
        long_content = "这是测试内容。" * 1000  # Very long content
        
        for platform, limit in rewriter.PLATFORM_LIMITS.items():
            result = rewriter.rewrite_for_platform(long_content, platform)
            assert len(result) <= limit + 10  # Allow small margin for "..."
    
    def test_rewrite_xiaohongshu_adds_emoji(self, rewriter, sample_content):
        """Test xiaohongshu rewrite adds emoji"""
        result = rewriter.rewrite_for_platform(sample_content, "xiaohongshu")
        # Should contain some emoji
        assert any(emoji in result for emoji in ["👍", "❤️", "⭐", "✅"])
    
    def test_rewrite_xiaohongshu_adds_tags(self, rewriter, sample_content):
        """Test xiaohongshu rewrite adds hashtags"""
        result = rewriter.rewrite_for_platform(sample_content, "xiaohongshu")
        assert "#" in result
    
    def test_rewrite_weibo_adds_tags(self, rewriter, sample_content):
        """Test weibo rewrite adds hashtags"""
        result = rewriter.rewrite_for_platform(sample_content, "weibo")
        assert "#" in result
    
    def test_rewrite_zhihu_no_emoji(self, rewriter, sample_content):
        """Test zhihu rewrite doesn't add emoji"""
        result = rewriter.rewrite_for_platform(sample_content, "zhihu")
        config = rewriter.PLATFORM_CONFIG["zhihu"]
        if not config.get("emoji"):
            # Should not have typical emoji
            assert "👍" not in result
            assert "❤️" not in result
    
    def test_get_platform_info(self, rewriter):
        """Test get_platform_info returns correct structure"""
        for platform in rewriter.PLATFORM_LIMITS.keys():
            info = rewriter.get_platform_info(platform)
            assert "name" in info
            assert "limit" in info
            assert "config" in info
            assert info["name"] == platform
            assert info["limit"] == rewriter.PLATFORM_LIMITS[platform]
    
    def test_rewrite_invalid_platform_returns_content(self, rewriter, sample_content):
        """Test rewrite with invalid platform returns truncated content"""
        result = rewriter.rewrite_for_platform(sample_content, "invalid_platform")
        assert isinstance(result, str)
        # Should use default limit
        assert len(result) <= 1010
    
    def test_truncate_content_with_sentence_end(self, rewriter):
        """Test truncation preserves sentence end if possible"""
        content = "第一句。第二句。第三句很长很长的内容。"
        limit = 10
        result = rewriter._truncate_content(content, limit)
        # Should end with a sentence terminator if one exists within reasonable range
        assert result.endswith(("。", "！", "？", ".", "..."))
