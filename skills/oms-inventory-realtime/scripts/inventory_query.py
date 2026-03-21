#!/usr/bin/env python3
"""
库存实时查询脚本
支持通过 JSON 输入/输出与其他技能对接
"""

import json
import sys
from datetime import datetime


def calculate_available_inventory(total: int, reserved: int, ringfenced: int) -> int:
    """计算可售库存"""
    return max(0, total - reserved - ringfenced)


def query_inventory(sku_id: str, warehouse: str = "ALL") -> dict:
    """查询SKU库存"""
    # 模拟数据，实际应调用OMS API
    inventory_data = {
        "sku_id": sku_id,
        "warehouse": warehouse,
        "timestamp": datetime.now().isoformat(),
        "inventory": {
            "TOTAL": 1000,
            "AVAILABLE": 850,
            "RESERVED": 100,
            "RINGFENCED": 50,
            "IN_TRANSIT": 200
        },
        "channel_available": {
            "taobao": 300,
            "jd": 250,
            "douyin": 200,
            "store": 100
        }
    }
    return inventory_data


def check_overselling_risk(sku_id: str, quantity: int) -> dict:
    """检查超卖风险"""
    inventory = query_inventory(sku_id)
    available = inventory["inventory"]["AVAILABLE"]
    
    risk_level = "LOW"
    if quantity > available:
        risk_level = "CRITICAL"
    elif quantity > available * 0.8:
        risk_level = "HIGH"
    elif quantity > available * 0.5:
        risk_level = "MEDIUM"
    
    return {
        "sku_id": sku_id,
        "requested_quantity": quantity,
        "available": available,
        "can_fulfill": quantity <= available,
        "risk_level": risk_level,
        "suggested_action": "BLOCK" if quantity > available else "PRE_RESERVE"
    }


def pre_reserve(sku_id: str, quantity: int, order_id: str, timeout_minutes: int = 15) -> dict:
    """预扣库存"""
    # 模拟预扣逻辑
    reservation = {
        "reservation_id": f"RES_{order_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sku_id": sku_id,
        "quantity": quantity,
        "order_id": order_id,
        "status": "LOCKED",
        "locked_at": datetime.now().isoformat(),
        "expires_at": datetime.now().timestamp() + timeout_minutes * 60
    }
    return reservation


def release_reservation(reservation_id: str) -> dict:
    """释放预扣"""
    return {
        "reservation_id": reservation_id,
        "status": "RELEASED",
        "released_at": datetime.now().isoformat()
    }


def main():
    """主入口 - 读取JSON输入"""
    if len(sys.argv) > 1:
        # 从文件读取输入
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        # 从stdin读取
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "query")
    result = {}
    
    if action == "query":
        result = query_inventory(
            input_data.get("sku_id"),
            input_data.get("warehouse", "ALL")
        )
    elif action == "check_overselling":
        result = check_overselling_risk(
            input_data.get("sku_id"),
            input_data.get("quantity", 1)
        )
    elif action == "pre_reserve":
        result = pre_reserve(
            input_data.get("sku_id"),
            input_data.get("quantity", 1),
            input_data.get("order_id"),
            input_data.get("timeout_minutes", 15)
        )
    elif action == "release":
        result = release_reservation(input_data.get("reservation_id"))
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
