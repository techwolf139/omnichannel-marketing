"""
微信公众号内容排版器

将Markdown格式内容转换为微信公众号图文格式。
"""

import re
from typing import Optional


class ContentFormatter:
    """
    微信公众号内容排版器

    将Markdown转换为适配微信公众号的HTML格式，
    支持多种排版主题。

    Attributes:
        THEMES: 支持的排版主题列表
    """

    THEMES = ["default", "minimal", "modern"]

    # 主题CSS样式
    THEME_STYLES = {
        "default": {
            "font_size": "16px",
            "line_height": "1.75",
            "color": "#333333",
            "heading_color": "#000000",
            "link_color": "#576b95",
            "background": "#ffffff",
            "padding": "20px",
        },
        "minimal": {
            "font_size": "18px",
            "line_height": "1.8",
            "color": "#444444",
            "heading_color": "#222222",
            "link_color": "#576b95",
            "background": "#fafafa",
            "padding": "30px",
        },
        "modern": {
            "font_size": "16px",
            "line_height": "1.75",
            "color": "#333333",
            "heading_color": "#1a1a1a",
            "link_color": "#07c160",
            "background": "#ffffff",
            "padding": "20px",
        },
    }

    def __init__(self):
        """初始化内容排版器"""
        pass

    def format_content(self, markdown: str, theme: str = "default") -> str:
        """
        格式化内容

        将Markdown转换为微信公众号HTML格式。

        Args:
            markdown: Markdown格式内容
            theme: 排版主题，可选值：default/minimal/modern

        Returns:
            微信公众号HTML格式内容

        Raises:
            ValueError: 不支持的theme参数

        Example:
            >>> formatter = ContentFormatter()
            >>> html = formatter.format_content(
            ...     markdown="# 标题\\n\\n正文内容",
            ...     theme="minimal"
            ... )
        """
        if theme not in self.THEMES:
            raise ValueError(f"Unsupported theme: {theme}. "
                           f"Supported: {', '.join(self.THEMES)}")

        html = self._markdown_to_html(markdown)
        styled_html = self._apply_theme(html, theme)
        return styled_html

    def _markdown_to_html(self, markdown: str) -> str:
        """
        Markdown转HTML

        将基础Markdown语法转换为HTML标签。
        """
        html = markdown

        # 标题转换
        html = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        html = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 代码块（先处理，避免内容被其他规则干扰）
        html = re.sub(r'```(\w+)?\n(.*?)```', 
                     r'<pre style="background:#f6f8fa;padding:16px;overflow-x:auto;"><code>\2</code></pre>', 
                     html, flags=re.DOTALL)

        # 图片（必须在链接之前处理）
        html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', 
                     r'<img src="\2" alt="\1" style="max-width:100%;"/>', html)

        # 链接
        html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

        # 粗体和斜体
        html = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', html)
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)

        # 代码块
        html = re.sub(r'```(\w+)?\n(.*?)```', 
                     r'<pre style="background:#f6f8fa;padding:16px;overflow-x:auto;"><code>\2</code></pre>', 
                     html, flags=re.DOTALL)

        # 行内代码
        html = re.sub(r'`([^`]+)`', r'<code style="background:#f6f8fa;padding:2px 4px;">\1</code>', html)

        # 无序列表
        html = re.sub(r'^[\*\-\+] (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # 有序列表
        html = re.sub(r'^\d+\. (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # 引用
        html = re.sub(r'^> (.*?)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)

        # 水平线
        html = re.sub(r'^---+$', r'<hr/>', html, flags=re.MULTILINE)

        # 段落处理（简单处理）
        paragraphs = html.split('\n\n')
        new_paragraphs = []
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<') and not p.endswith('>'):
                p = f'<p>{p}</p>'
            new_paragraphs.append(p)
        html = '\n\n'.join(new_paragraphs)

        return html

    def _apply_theme(self, html: str, theme: str) -> str:
        """
        应用主题样式

        将HTML包裹在主题样式容器中。
        """
        styles = self.THEME_STYLES[theme]

        css = f"""
        .wechat-article-{theme} {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
            font-size: {styles['font_size']};
            line-height: {styles['line_height']};
            color: {styles['color']};
            background: {styles['background']};
            padding: {styles['padding']};
            max-width: 677px;
            margin: 0 auto;
        }}
        .wechat-article-{theme} h1 {{
            font-size: 1.5em;
            color: {styles['heading_color']};
            margin: 1.5em 0 0.8em;
            font-weight: 600;
        }}
        .wechat-article-{theme} h2 {{
            font-size: 1.3em;
            color: {styles['heading_color']};
            margin: 1.5em 0 0.8em;
            font-weight: 600;
        }}
        .wechat-article-{theme} h3 {{
            font-size: 1.15em;
            color: {styles['heading_color']};
            margin: 1.3em 0 0.6em;
            font-weight: 600;
        }}
        .wechat-article-{theme} p {{
            margin: 1em 0;
        }}
        .wechat-article-{theme} a {{
            color: {styles['link_color']};
            text-decoration: none;
        }}
        .wechat-article-{theme} img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1em auto;
        }}
        .wechat-article-{theme} blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 16px;
            margin: 1em 0;
            color: #666;
        }}
        .wechat-article-{theme} pre {{
            background: #f6f8fa;
            padding: 16px;
            overflow-x: auto;
            border-radius: 4px;
        }}
        .wechat-article-{theme} code {{
            background: #f6f8fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'SFMono-Regular', Consolas, monospace;
        }}
        """

        return f"""<style>{css}</style>
<div class="wechat-article-{theme}">
{html}
</div>"""

    def extract_summary(self, markdown: str, max_length: int = 120) -> str:
        """
        提取摘要

        从Markdown内容中提取纯文本摘要。

        Args:
            markdown: Markdown内容
            max_length: 摘要最大长度

        Returns:
            纯文本摘要
        """
        # 移除Markdown标记
        text = re.sub(r'#+ ', '', markdown)  # 标题
        text = re.sub(r'\*\*|\*|__|_', '', text)  # 强调
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # 图片
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # 链接
        text = re.sub(r'`', '', text)  # 代码
        text = re.sub(r'> ', '', text)  # 引用

        # 清理空白
        text = ' '.join(text.split())

        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(' ', 1)[0] + '...'
