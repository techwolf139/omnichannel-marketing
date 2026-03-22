"""
小红书笔记数据适配器
将小红书笔记API响应转换为OMS标准格式
"""
from datetime import datetime
from typing import List, Optional


class XHSNoteAdapter:
    """
    笔记数据适配器
    
    负责:
    1. 笔记曝光数据标准化
    2. 笔记互动数据标准化
    3. 批量数据聚合
    """
    
    def to_standard_exposure(self, raw: dict) -> dict:
        """
        将小红书原始曝光数据转换为标准格式
        
        Args:
            raw: 小红书API返回的原始数据
        
        Returns:
            标准曝光数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "title": raw.get("title", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "publish_time": self._parse_time(raw.get("publish_time")),
            "platform": "XHS"
        }
    
    def to_standard_interaction(self, raw: dict) -> dict:
        """
        将小红书原始互动数据转换为标准格式
        
        Args:
            raw: 小红书API返回的原始数据
        
        Returns:
            标准互动数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "interaction_rate": self._calc_interaction_rate(raw),
            "platform": "XHS"
        }
    
    def to_standard_note(self, raw: dict) -> dict:
        """
        将小红书笔记完整数据转换为标准格式（合并曝光+互动）
        
        Args:
            raw: 原始笔记数据（包含exposure和interaction）
        
        Returns:
            标准笔记数据
        """
        return {
            "note_id": raw.get("note_id", ""),
            "title": raw.get("title", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "interaction_rate": self._calc_interaction_rate(raw),
            "publish_time": self._parse_time(raw.get("publish_time")),
            "platform": "XHS"
        }
    
    def _calc_interaction_rate(self, raw: dict) -> float:
        """
        计算互动率 = (点赞+收藏+评论+分享) / 曝光量
        """
        exposure = int(raw.get("exposure_count", 0))
        if exposure == 0:
            return 0.0
        
        interactions = (
            int(raw.get("like_count", 0)) +
            int(raw.get("collect_count", 0)) +
            int(raw.get("comment_count", 0)) +
            int(raw.get("share_count", 0))
        )
        return round(interactions / exposure, 4)
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
