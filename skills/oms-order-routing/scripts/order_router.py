#!/usr/bin/env python3
"""
订单路由脚本
计算最优履约路径，支持订单拆分/合并
"""

import json
import sys
from datetime import datetime
import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """计算两点间距离（公里）"""
    R = 6371  # 地球半径
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


def route_order(order: dict, warehouses: list, stores: list) -> dict:
    """订单路由 - 计算最优履约路径"""
    # 收货地址坐标（模拟）
    customer_lat = order.get("customer_lat", 31.2304)
    customer_lon = order.get("customer_lon", 121.4737)
    
    candidates = []
    
    # 计算仓库备选
    for wh in warehouses:
        distance = calculate_distance(
            wh["lat"], wh["lon"],
            customer_lat, customer_lon
        )
        candidates.append({
            "source_type": "WAREHOUSE",
            "source_id": wh["id"],
            "source_name": wh["name"],
            "distance": round(distance, 2),
            "shipping_cost": round(distance * 1.5 + 5, 2),
            "delivery_time": f"{int(distance * 0.5 + 1)}小时",
            "stock_available": True
        })
    
    # 计算门店备选
    for store in stores:
        distance = calculate_distance(
            store["lat"], store["lon"],
            customer_lat, customer_lon
        )
        # 门店配送需在5公里内
        if distance <= 5:
            candidates.append({
                "source_type": "STORE",
                "source_id": store["id"],
                "source_name": store["name"],
                "distance": round(distance, 2),
                "shipping_cost": 0,  # 门店配送免费
                "delivery_time": "1小时",
                "stock_available": True,
                "store_as_warehouse": True
            })
    
    # 按成本排序
    candidates.sort(key=lambda x: x["shipping_cost"])
    
    return {
        "order_id": order.get("order_id"),
        "routing_options": candidates,
        "recommended": candidates[0] if candidates else None,
        "can_split": len(candidates) > 1,
        "timestamp": datetime.now().isoformat()
    }


def split_order(order: dict, items: list, warehouses: list) -> dict:
    """订单拆分"""
    # 按仓库分组
    item_groups = {}
    for item in items:
        wh_id = item.get("preferred_warehouse", "WH001")
        if wh_id not in item_groups:
            item_groups[wh_id] = []
        item_groups[wh_id].append(item)
    
    sub_orders = []
    for wh_id, wh_items in item_groups.items():
        sub_order = {
            "sub_order_id": f"{order['order_id']}_S{len(sub_orders)+1}",
            "warehouse_id": wh_id,
            "items": wh_items,
            "status": "TO_FULFILL"
        }
        sub_orders.append(sub_order)
    
    return {
        "original_order_id": order["order_id"],
        "sub_orders": sub_orders,
        "split_count": len(sub_orders),
        "timestamp": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "route")
    result = {}
    
    if action == "route":
        result = route_order(
            input_data.get("order", {}),
            input_data.get("warehouses", []),
            input_data.get("stores", [])
        )
    elif action == "split":
        result = split_order(
            input_data.get("order", {}),
            input_data.get("items", []),
            input_data.get("warehouses", [])
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
