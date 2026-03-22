"""
小红书订单适配器
将薯店/小程序API响应转换为OMS标准订单格式
"""
from datetime import datetime
from typing import List, Optional


class XHSOrderAdapter:
    """
    薯店/小程序订单适配器
    
    负责:
    1. 薯店订单标准化
    2. 小程序订单标准化
    3. 订单类型区分 (SHU_DIAN / MINI_PROGRAM)
    4. 状态映射
    """
    
    # 小红书订单状态映射
    STATUS_MAP = {
        1: "CREATED",    # 待支付
        2: "PAID",       # 已支付
        3: "SHIPPED",    # 已发货
        4: "DELIVERED",  # 已完成
        5: "CANCELLED",  # 已取消
    }
    
    def to_standard_order(self, raw: dict, order_type: str) -> dict:
        """
        将小红书原始订单转换为标准格式
        
        Args:
            raw: 小红书API返回的原始订单数据
            order_type: 订单类型 "SHU_DIAN" 或 "MINI_PROGRAM"
        
        Returns:
            标准订单数据
        """
        raw_state = int(raw.get("order_state", 1))
        
        return {
            "platform_order_id": raw.get("order_id", ""),
            "platform": "XHS",
            "order_type": order_type,
            "status": self.STATUS_MAP.get(raw_state, "UNKNOWN"),
            "status_code": raw_state,
            "buyer_nickname": raw.get("buyer_nickname", ""),
            "receiver_name": raw.get("receiver_name", ""),
            "receiver_mobile": raw.get("receiver_mobile", ""),
            "address_detail": raw.get("address_detail", ""),
            "items": self._normalize_items(raw.get("item_list", [])),
            "total_amount": float(raw.get("total_amount", 0)),
            "freight_amount": float(raw.get("freight_amount", 0)),
            "pay_time": self._parse_time(raw.get("pay_time")),
            "ship_time": self._parse_time(raw.get("ship_time")),
            "create_time": self._parse_time(raw.get("create_time")),
            # UTM归因字段
            "utm_source": raw.get("utm_source", ""),
            "utm_medium": raw.get("utm_medium", ""),
            "utm_campaign": raw.get("utm_campaign", ""),
            # 归因权重（固定值，后续归因计算时使用）
            "attribution_weight": 0.15
        }
    
    def _normalize_items(self, items: List[dict]) -> List[dict]:
        """
        标准化商品列表
        
        Args:
            items: 原始商品列表
        
        Returns:
            标准商品列表
        """
        normalized = []
        for item in items:
            normalized.append({
                "sku_id": item.get("sku_id", ""),
                "sku_name": item.get("sku_name", ""),
                "quantity": int(item.get("quantity", 1)),
                "unit_price": float(item.get("unit_price", 0)),
                "total_price": float(item.get("total_price", 0)),
                "image_url": item.get("image_url", "")
            })
        return normalized
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """解析时间字符串"""
        if not time_str:
            return None
        try:
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def is_shudan_order(self, raw: dict) -> bool:
        """判断是否为薯店订单"""
        return raw.get("order_source", "").upper() == "SHU_DIAN"
    
    def is_mini_program_order(self, raw: dict) -> bool:
        """判断是否为小程序订单"""
        return raw.get("order_source", "").upper() == "MINI_PROGRAM"
