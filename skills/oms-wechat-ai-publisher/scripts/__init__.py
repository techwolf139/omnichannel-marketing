"""
微信公众号AI发布适配器

提供微信公众号文章草稿管理、AI封面生成、内容排版等功能。
"""

__version__ = "0.1.0"
__author__ = "OMS Team"

from .auth import WeChatAuth
from .client import WeChatClient
from .cover_generator import CoverGenerator
from .formatter import ContentFormatter

__all__ = [
    "WeChatAuth",
    "WeChatClient",
    "CoverGenerator",
    "ContentFormatter",
]
