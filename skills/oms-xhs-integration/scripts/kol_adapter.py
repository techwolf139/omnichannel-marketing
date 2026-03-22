"""
小红书KOL/蒲公英平台适配器
将蒲公英合作API响应转换为OMS标准格式
"""
from datetime import datetime
from typing import List, Optional


class XHSKOLAdapter:
    """
    KOL合作数据适配器
    
    负责:
    1. KOL合作订单标准化
    2. 合作状态映射
    3. 投放效果数据标准化
    """
    
    # 蒲公英订单状态映射
    KOL_STATUS_MAP = {
        "pending": "待发布",
        "ongoing": "执行中",
        "completed": "已完成",
        "cancelled": "已取消"
    }
    
    # OMS标准状态
    KOL_OMS_STATUS = {
        "pending": "CREATED",
        "ongoing": "IN_PROGRESS",
        "completed": "COMPLETED",
        "cancelled": "CANCELLED"
    }
    
    def to_standard_kol_order(self, raw: dict) -> dict:
        """
        将蒲公英原始订单转换为标准格式
        
        Args:
            raw: 蒲公英API返回的原始数据
        
        Returns:
            标准KOL订单数据
        """
        raw_status = raw.get("status", "pending")
        
        return {
            "order_id": raw.get("order_id", ""),
            "kol_name": raw.get("kol_name", ""),
            "kol_id": raw.get("kol_id", ""),
            "content_type": raw.get("content_type", ""),
            "price": float(raw.get("price", 0)),
            "status": self.KOL_OMS_STATUS.get(raw_status, "UNKNOWN"),
            "status_text": self.KOL_STATUS_MAP.get(raw_status, "未知"),
            "expected_publish_time": self._parse_time(raw.get("expected_publish_time")),
            "actual_publish_time": self._parse_time(raw.get("actual_publish_time")),
            "note_url": raw.get("note_url", ""),
            "platform": "XHS_KOL"
        }
    
    def to_standard_kol_performance(self, raw: dict) -> dict:
        """
        将蒲公英投放效果数据转换为标准格式
        
        Args:
            raw: 蒲公英API返回的投放效果数据
        
        Returns:
            标准KOL效果数据
        """
        return {
            "order_id": raw.get("order_id", ""),
            "note_id": raw.get("note_id", ""),
            "exposure_count": int(raw.get("exposure_count", 0)),
            "like_count": int(raw.get("like_count", 0)),
            "collect_count": int(raw.get("collect_count", 0)),
            "comment_count": int(raw.get("comment_count", 0)),
            "share_count": int(raw.get("share_count", 0)),
            "click_count": int(raw.get("click_count", 0)),
            "cost_per_exposure": self._calc_cpe(raw),
            "cost_per_interaction": self._calc_cpi(raw),
            "platform": "XHS_KOL"
        }
    
    def _calc_cpe(self, raw: dict) -> float:
        """计算千次曝光成本"""
        exposure = int(raw.get("exposure_count", 0))
        price = float(raw.get("price", 0))
        if exposure == 0:
            return 0.0
        return round(price / exposure * 1000, 2)
    
    def _calc_cpi(self, raw: dict) -> float:
        """计算互动成本"""
        interactions = (
            int(raw.get("like_count", 0)) +
            int(raw.get("collect_count", 0)) +
            int(raw.get("comment_count", 0)) +
            int(raw.get("share_count", 0))
        )
        price = float(raw.get("price", 0))
        if interactions == 0:
            return 0.0
        return round(price / interactions, 2)
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
