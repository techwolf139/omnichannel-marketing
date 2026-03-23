"""小红书自动化工具集

提供热点话题采集、笔记自动发布、数据统计分析功能。
"""

from .trending_fetcher import TrendingFetcher
from .note_publisher import NotePublisher
from .stats_fetcher import StatsFetcher

__version__ = "1.0.0"
__all__ = ["TrendingFetcher", "NotePublisher", "StatsFetcher"]
