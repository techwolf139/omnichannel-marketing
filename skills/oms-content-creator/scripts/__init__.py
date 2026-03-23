"""
OMS Content Creator - 爆款文案生成引擎

提供内容生成、改写和热点匹配功能。
"""

from .generator import ContentGenerator
from .rewriter import ContentRewriter
from .trending import TrendingMatcher

__version__ = "1.0.0"
__all__ = ["ContentGenerator", "ContentRewriter", "TrendingMatcher"]
