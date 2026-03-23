"""
测试ContentFormatter内容排版器模块
"""

import pytest
from scripts.formatter import ContentFormatter


class TestContentFormatter:
    """测试ContentFormatter类"""
    
    def test_init(self):
        """测试初始化"""
        formatter = ContentFormatter()
        assert "default" in formatter.THEMES
        assert "minimal" in formatter.THEMES
        assert "modern" in formatter.THEMES
    
    def test_format_content_default_theme(self):
        """测试默认主题"""
        formatter = ContentFormatter()
        markdown = "# 标题\n\n正文内容"
        html = formatter.format_content(markdown, theme="default")
        
        assert isinstance(html, str)
        assert "<h1>" in html
        assert "<p>" in html
        assert "wechat-article-default" in html
    
    def test_format_content_minimal_theme(self):
        """测试minimal主题"""
        formatter = ContentFormatter()
        markdown = "# 标题\n\n正文内容"
        html = formatter.format_content(markdown, theme="minimal")
        
        assert "wechat-article-minimal" in html
    
    def test_format_content_invalid_theme(self):
        """测试无效主题抛出异常"""
        formatter = ContentFormatter()
        
        with pytest.raises(ValueError) as exc_info:
            formatter.format_content("# 标题", theme="invalid")
        
        assert "Unsupported theme" in str(exc_info.value)
    
    def test_markdown_to_html_heading(self):
        """测试标题转换"""
        formatter = ContentFormatter()
        markdown = "# 一级标题\n## 二级标题\n### 三级标题"
        html = formatter._markdown_to_html(markdown)
        
        assert "<h1>一级标题</h1>" in html
        assert "<h2>二级标题</h2>" in html
        assert "<h3>三级标题</h3>" in html
    
    def test_markdown_to_html_bold_italic(self):
        """测试粗体和斜体"""
        formatter = ContentFormatter()
        markdown = "**粗体** *斜体*"
        html = formatter._markdown_to_html(markdown)
        
        assert "<strong>粗体</strong>" in html
        assert "<em>斜体</em>" in html
    
    def test_markdown_to_html_link(self):
        """测试链接转换"""
        formatter = ContentFormatter()
        markdown = "[链接文字](https://example.com)"
        html = formatter._markdown_to_html(markdown)
        
        assert '<a href="https://example.com">链接文字</a>' in html
    
    def test_markdown_to_html_image(self):
        """测试图片转换"""
        formatter = ContentFormatter()
        markdown = "![图片描述](https://example.com/image.jpg)"
        html = formatter._markdown_to_html(markdown)
        
        assert '<img src="https://example.com/image.jpg" alt="图片描述"' in html
    
    def test_markdown_to_html_code_inline(self):
        """测试行内代码"""
        formatter = ContentFormatter()
        markdown = "`code`"
        html = formatter._markdown_to_html(markdown)
        
        assert "<code" in html
        assert "code" in html
    
    def test_markdown_to_html_blockquote(self):
        """测试引用"""
        formatter = ContentFormatter()
        markdown = "> 引用内容"
        html = formatter._markdown_to_html(markdown)
        
        assert "<blockquote>引用内容</blockquote>" in html
    
    def test_extract_summary(self):
        """测试摘要提取"""
        formatter = ContentFormatter()
        markdown = "# 标题\n\n这是正文内容，包含**粗体**和[链接](https://example.com)。"
        summary = formatter.extract_summary(markdown)
        
        assert isinstance(summary, str)
        assert "标题" in summary
        assert "这是正文内容" in summary
        # Markdown标记应该被移除
        assert "**" not in summary
        assert "[" not in summary
    
    def test_extract_summary_truncate(self):
        """测试摘要截断"""
        formatter = ContentFormatter()
        markdown = "这是一段很长的内容，" * 20
        summary = formatter.extract_summary(markdown, max_length=50)
        
        assert len(summary) <= 53  # 50 + "..."
        assert summary.endswith("...")
