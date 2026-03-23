"""
测试CoverGenerator封面生成器模块
"""

import pytest
from scripts.cover_generator import CoverGenerator


class TestCoverGenerator:
    """测试CoverGenerator类"""
    
    def test_init(self):
        """测试初始化"""
        generator = CoverGenerator()
        assert isinstance(generator.SUPPORTED_STYLES, list)
        assert "default" in generator.SUPPORTED_STYLES
        assert "modern" in generator.SUPPORTED_STYLES
    
    def test_generate_cover_default(self):
        """测试默认风格封面生成"""
        generator = CoverGenerator()
        url = generator.generate_cover("AI技术发展趋势")
        
        assert isinstance(url, str)
        assert url.startswith("https://example.com/cover_")
        assert "default" in url
    
    def test_generate_cover_modern(self):
        """测试modern风格封面生成"""
        generator = CoverGenerator()
        url = generator.generate_cover("AI技术发展趋势", style="modern")
        
        assert "modern" in url
    
    def test_generate_cover_invalid_style(self):
        """测试无效风格抛出异常"""
        generator = CoverGenerator()
        
        with pytest.raises(ValueError) as exc_info:
            generator.generate_cover("测试", style="invalid")
        
        assert "Unsupported style" in str(exc_info.value)
    
    def test_generate_batch_covers(self):
        """测试批量生成封面"""
        generator = CoverGenerator()
        topics = ["AI趋势", "区块链", "元宇宙"]
        urls = generator.generate_batch_covers(topics, style="tech")
        
        assert len(urls) == 3
        assert all(isinstance(url, str) for url in urls)
    
    def test_get_style_suggestions_tech(self):
        """测试科技主题风格建议"""
        generator = CoverGenerator()
        suggestions = generator.get_style_suggestions("AI人工智能")
        
        assert "tech" in suggestions
        assert "modern" in suggestions
    
    def test_get_style_suggestions_business(self):
        """测试商业主题风格建议"""
        generator = CoverGenerator()
        suggestions = generator.get_style_suggestions("商业管理")
        
        assert "business" in suggestions
    
    def test_get_style_suggestions_lifestyle(self):
        """测试生活主题风格建议"""
        generator = CoverGenerator()
        suggestions = generator.get_style_suggestions("生活文艺")
        
        assert "minimal" in suggestions
