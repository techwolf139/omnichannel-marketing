#!/usr/bin/env python3
"""
利润分成脚本
佣金计算与结算
"""

import json
import sys
from datetime import datetime


def calculate_commission(order: dict, commission_rules: dict) -> dict:
    """计算订单佣金"""
    order_amount = order.get("order_amount", 0)
    channel = order.get("source_channel")
    category = order.get("category", "GENERAL")
    
    # 获取对应渠道和类目规则
    channel_rules = commission_rules.get("channels", {}).get(channel, {})
    category_rules = channel_rules.get("categories", {}).get(category, {})
    
    # 计算佣金
    commission_rate = category_rules.get("commission_rate", 0.05)
    commission = order_amount * commission_rate
    
    # 平台服务费
    platform_fee_rate = category_rules.get("platform_fee_rate", 0.02)
    platform_fee = order_amount * platform_fee_rate
    
    # 商家实际收入
    merchant_revenue = order_amount - commission - platform_fee
    
    return {
        "order_id": order.get("order_id"),
        "channel": channel,
        "category": category,
        "order_amount": order_amount,
        "commission_rate": commission_rate,
        "commission": round(commission, 2),
        "platform_fee_rate": platform_fee_rate,
        "platform_fee": round(platform_fee, 2),
        "merchant_revenue": round(merchant_revenue, 2),
        "timestamp": datetime.now().isoformat()
    }


def distribute_profit(order: dict, participants: list) -> dict:
    """利润分配"""
    total_profit = order.get("profit_amount", 0)
    
    distributions = []
    for participant in participants:
        share_type = participant.get("share_type")  # FIXED, PERCENT
        share_value = participant.get("share_value")
        
        if share_type == "FIXED":
            amount = share_value
        else:  # PERCENT
            amount = total_profit * share_value / 100
        
        distributions.append({
            "participant_id": participant.get("participant_id"),
            "participant_name": participant.get("name"),
            "share_type": share_type,
            "share_value": share_value,
            "amount": round(amount, 2)
        })
    
    return {
        "order_id": order.get("order_id"),
        "total_profit": total_profit,
        "distributions": distributions,
        "timestamp": datetime.now().isoformat()
    }


def generate_settlement(commissions: list, period: dict) -> dict:
    """生成结算单"""
    total_commission = sum(c.get("commission", 0) for c in commissions)
    total_platform_fee = sum(c.get("platform_fee", 0) for c in commissions)
    total_merchant_revenue = sum(c.get("merchant_revenue", 0) for c in commissions)
    
    return {
        "settlement_id": f"STL_{datetime.now().strftime('%Y%m%d')}",
        "period_start": period.get("start_date"),
        "period_end": period.get("end_date"),
        "order_count": len(commissions),
        "summary": {
            "total_commission": round(total_commission, 2),
            "total_platform_fee": round(total_platform_fee, 2),
            "total_merchant_revenue": round(total_merchant_revenue, 2)
        },
        "status": "PENDING_SETTLEMENT",
        "created_at": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "calculate_commission")
    result = {}
    
    if action == "calculate_commission":
        result = calculate_commission(
            input_data.get("order", {}),
            input_data.get("commission_rules", {})
        )
    elif action == "distribute_profit":
        result = distribute_profit(
            input_data.get("order", {}),
            input_data.get("participants", [])
        )
    elif action == "generate_settlement":
        result = generate_settlement(
            input_data.get("commissions", []),
            input_data.get("period", {})
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
