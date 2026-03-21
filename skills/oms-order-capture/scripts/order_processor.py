#!/usr/bin/env python3
"""
全渠道订单汇聚与清洗脚本
支持订单标准化、黄牛识别
"""

import json
import sys
from datetime import datetime
import hashlib


def normalize_order(raw_order: dict) -> dict:
    """标准化订单"""
    # 地址脱敏
    address = raw_order.get("receiver_address", "")
    masked_address = mask_address(address)
    
    # 标准化商品信息
    items = []
    for item in raw_order.get("items", []):
        items.append({
            "sku_id": item.get("sku_code"),
            "quantity": item.get("num"),
            "unit_price": float(item.get("price", 0)),
            "final_price": float(item.get("final_price", item.get("price", 0)))
        })
    
    return {
        "order_id": raw_order.get("order_id"),
        "source_order_id": raw_order.get("source_order_id"),
        "source_channel": raw_order.get("channel"),
        "customer": {
            "one_id": raw_order.get("one_id", ""),
            "phone": mask_phone(raw_order.get("phone", "")),
            "member_level": raw_order.get("member_level", "NORMAL")
        },
        "items": items,
        "amounts": {
            "goods_amount": float(raw_order.get("goods_amount", 0)),
            "shipping_fee": float(raw_order.get("shipping_fee", 0)),
            "discount_amount": float(raw_order.get("discount_amount", 0)),
            "order_amount": float(raw_order.get("total_amount", 0))
        },
        "receiver_address": masked_address,
        "status": raw_order.get("order_status", "PENDING"),
        "created_at": raw_order.get("created_time")
    }


def mask_phone(phone: str) -> str:
    """手机号脱敏"""
    if len(phone) == 11:
        return phone[:3] + "****" + phone[7:]
    return "****"


def mask_address(address: str) -> str:
    """地址脱敏 - 保留省市区，隐藏详细地址"""
    parts = address.split()
    if len(parts) >= 3:
        return " ".join(parts[:3]) + " ***"
    return address


def detect_scalper(order: dict) -> dict:
    """黄牛订单识别"""
    risk_signals = []
    risk_score = 0
    
    phone = order.get("customer", {}).get("phone", "")
    
    # 检查风险号段
    risk_prefixes = ["170", "171", "178", "170"]
    for prefix in risk_prefixes:
        if phone.startswith(prefix):
            risk_signals.append("高风险号段")
            risk_score += 30
    
    # 检查同一地址高频下单 - 需要跨订单分析
    address = order.get("receiver_address", "")
    if "***" in address:
        risk_signals.append("地址信息不完整")
        risk_score += 10
    
    # 检查购买行为
    items = order.get("items", [])
    if items and items[0].get("quantity", 1) > 5:
        risk_signals.append("大批量购买")
        risk_score += 20
    
    return {
        "order_id": order.get("order_id"),
        "risk_score": min(100, risk_score),
        "risk_level": "HIGH" if risk_score >= 50 else "MEDIUM" if risk_score >= 20 else "LOW",
        "risk_signals": risk_signals,
        "suggested_action": "REVIEW" if risk_score >= 20 else "PASS"
    }


def deduplicate_orders(orders: list) -> list:
    """订单去重"""
    seen = set()
    unique_orders = []
    
    for order in orders:
        key = f"{order.get('source_channel')}_{order.get('source_order_id')}"
        if key not in seen:
            seen.add(key)
            unique_orders.append(order)
    
    return unique_orders


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "normalize")
    result = {}
    
    if action == "normalize":
        result = normalize_order(input_data.get("order", {}))
    elif action == "detect_scalper":
        result = detect_scalper(input_data.get("order", {}))
    elif action == "deduplicate":
        result = {
            "unique_orders": deduplicate_orders(input_data.get("orders", [])),
            "total_count": len(input_data.get("orders", []))
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
