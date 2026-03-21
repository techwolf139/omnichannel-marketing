#!/usr/bin/env python3
"""
跨渠道退货脚本
处理退货、退款、换货请求
"""

import json
import sys
from datetime import datetime


def check_return_eligibility(order: dict, return_request: dict) -> dict:
    """检查退货资格"""
    order_date = datetime.fromisoformat(order.get("created_at", "2024-01-01"))
    days_since_order = (datetime.now() - order_date).days
    
    # 检查是否在退货期限内
    max_return_days = order.get("max_return_days", 7)
    is_within_period = days_since_order <= max_return_days
    
    # 检查商品是否支持退货
    item = order.get("items", [{}])[0]
    returnable = item.get("returnable", True)
    
    # 检查是否已退货
    if order.get("return_status") == "COMPLETED":
        return {
            "eligible": False,
            "reason": "订单已完成退货",
            "can_apply": False
        }
    
    eligible = is_within_period and returnable
    
    return {
        "order_id": order.get("order_id"),
        "eligible": eligible,
        "reason": "" if eligible else "超过退货期限或商品不支持退货",
        "days_since_order": days_since_order,
        "max_return_days": max_return_days,
        "refund_amount": item.get("final_price", 0) if eligible else 0,
        "timestamp": datetime.now().isoformat()
    }


def process_refund(return_request: dict, order: dict) -> dict:
    """处理退款"""
    refund_id = f"REF_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 计算退款金额
    item = order.get("items", [{}])[0]
    refund_amount = item.get("final_price", 0)
    
    # 是否退回运费
    if return_request.get("include_shipping", False):
        refund_amount += order.get("shipping_fee", 0)
    
    # 优惠券是否退还
    coupon_returned = return_request.get("coupon_returned", True)
    
    return {
        "refund_id": refund_id,
        "order_id": order.get("order_id"),
        "refund_amount": refund_amount,
        "refund_method": return_request.get("refund_method", "ORIGINAL"),  # ORIGINAL, WALLET
        "coupon_returned": coupon_returned,
        "status": "PROCESSING",
        "estimated_arrival": "3-5个工作日",
        "created_at": datetime.now().isoformat()
    }


def process_exchange(return_request: dict, order: dict) -> dict:
    """处理换货"""
    exchange_id = f"EXC_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 检查库存
    target_sku = return_request.get("target_sku")
    available = True  # 模拟检查
    
    return {
        "exchange_id": exchange_id,
        "original_order_id": order.get("order_id"),
        "original_sku": order.get("items", [{}])[0].get("sku_id"),
        "target_sku": target_sku,
        "price_difference": return_request.get("price_difference", 0),
        "stock_available": available,
        "status": "PENDING_INBOUND" if available else "OUT_OF_STOCK",
        "inbound_tracking": f"RTN{return_request.get('return_id', '')}",
        "created_at": datetime.now().isoformat()
    }


def handle_crosschannel_return(return_request: dict, warehouses: list) -> dict:
    """跨渠道退货处理"""
    original_channel = return_request.get("original_channel")
    return_channel = return_request.get("return_channel")
    
    # 找到最近的可用仓库
    customer_location = return_request.get("customer_location", {})
    
    return_warehouse = warehouses[0]  # 模拟选择第一个
    
    return {
        "return_id": return_request.get("return_id"),
        "original_channel": original_channel,
        "return_channel": return_channel,
        "assigned_warehouse": return_warehouse.get("id"),
        "shipping_method": "CROSS_CHANNEL_RETURN",
        "estimated_processing_days": 3,
        "can_partial_return": True,
        "created_at": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "check_eligibility")
    result = {}
    
    if action == "check_eligibility":
        result = check_return_eligibility(
            input_data.get("order", {}),
            input_data.get("return_request", {})
        )
    elif action == "process_refund":
        result = process_refund(
            input_data.get("return_request", {}),
            input_data.get("order", {})
        )
    elif action == "process_exchange":
        result = process_exchange(
            input_data.get("return_request", {}),
            input_data.get("order", {})
        )
    elif action == "crosschannel_return":
        result = handle_crosschannel_return(
            input_data.get("return_request", {}),
            input_data.get("warehouses", [])
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
