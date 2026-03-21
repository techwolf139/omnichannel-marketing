#!/usr/bin/env python3
"""
库存圈围脚本
渠道专属库存隔离，支持与 inventory_realtime 对接
"""

import json
import sys
from datetime import datetime


def set_ringfence(sku_id: str, channel: str, quantity: int, reason: str = "") -> dict:
    """设置渠道圈围"""
    return {
        "ringfence_id": f"RF_{sku_id}_{channel}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "sku_id": sku_id,
        "channel": channel,
        "quantity": quantity,
        "reason": reason,
        "status": "ACTIVE",
        "created_at": datetime.now().isoformat()
    }


def release_ringfence(ringfence_id: str) -> dict:
    """释放圈围"""
    return {
        "ringfence_id": ringfence_id,
        "status": "RELEASED",
        "released_at": datetime.now().isoformat()
    }


def check_ringfence_availability(sku_id: str, channel: str, requested_qty: int) -> dict:
    """检查圈围后可用库存"""
    # 模拟数据，实际应调用 inventory_realtime 接口
    # 假设从 inventory_realtime 获取的基础库存
    base_inventory = {
        "TOTAL": 1000,
        "AVAILABLE": 800,
        "RESERVED": 100,
        "OTHER_RINGFENCED": 100
    }
    
    # 获取该渠道圈围量
    current_ringfence = 50  # 模拟
    
    # 计算该渠道可用
    channel_available = max(0, base_inventory["AVAILABLE"] - current_ringfence)
    
    return {
        "sku_id": sku_id,
        "channel": channel,
        "requested_quantity": requested_qty,
        "ringfence_quantity": current_ringfence,
        "channel_available": channel_available,
        "can_fulfill": requested_qty <= channel_available,
        "conflict_with": []  # 可能冲突的渠道
    }


def store_as_warehouse_check(store_id: str, sku_id: str, shipping_distance: float) -> dict:
    """门店作为仓库能力检查"""
    return {
        "store_id": store_id,
        "sku_id": sku_id,
        "shipping_distance": shipping_distance,
        "fulfillment_capability": "YES" if shipping_distance < 5 else "CONDITIONAL",
        "estimated_shipping_cost": shipping_distance * 2.5,
        "estimated_delivery_time": f"{int(shipping_distance * 0.5)}小时"
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "check")
    result = {}
    
    if action == "set_ringfence":
        result = set_ringfence(
            input_data.get("sku_id"),
            input_data.get("channel"),
            input_data.get("quantity"),
            input_data.get("reason", "")
        )
    elif action == "release_ringfence":
        result = release_ringfence(input_data.get("ringfence_id"))
    elif action == "check":
        result = check_ringfence_availability(
            input_data.get("sku_id"),
            input_data.get("channel"),
            input_data.get("quantity", 1)
        )
    elif action == "store_check":
        result = store_as_warehouse_check(
            input_data.get("store_id"),
            input_data.get("sku_id"),
            input_data.get("distance", 0)
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
