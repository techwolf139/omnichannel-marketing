#!/usr/bin/env python3
"""
促销引擎脚本
优惠券、折扣、积分计算
"""

import json
import sys
from datetime import datetime, timedelta


def calculate_discount(order: dict, promotions: list) -> dict:
    """计算订单优惠"""
    goods_amount = order.get("goods_amount", 0)
    applicable_promotions = []
    total_discount = 0
    
    for promo in promotions:
        if not is_promo_valid(promo):
            continue
        
        discount = 0
        promo_type = promo.get("type")
        
        if promo_type == "COUPON":
            # 优惠券
            if goods_amount >= promo.get("min_amount", 0):
                if promo.get("discount_type") == "FIXED":
                    discount = promo.get("discount_value", 0)
                elif promo.get("discount_type") == "PERCENT":
                    discount = goods_amount * promo.get("discount_value", 0) / 100
        
        elif promo_type == "FULL_REDUCE":
            # 满减
            if goods_amount >= promo.get("min_amount", 0):
                discount = promo.get("reduce_value", 0)
        
        elif promo_type == "SECOND_ITEM_DISCOUNT":
            # 第二件折扣
            items = order.get("items", [])
            if len(items) >= 2:
                sorted_items = sorted(items, key=lambda x: x.get("price", 0))
                discount = sorted_items[1].get("price", 0) * (1 - promo.get("discount_percent", 50) / 100)
        
        if discount > 0:
            applicable_promotions.append({
                "promo_id": promo.get("promo_id"),
                "promo_name": promo.get("name"),
                "discount": round(discount, 2)
            })
            total_discount += discount
    
    return {
        "order_id": order.get("order_id"),
        "original_amount": goods_amount,
        "applicable_promotions": applicable_promotions,
        "total_discount": round(total_discount, 2),
        "final_amount": round(goods_amount - total_discount, 2),
        "timestamp": datetime.now().isoformat()
    }


def is_promo_valid(promo: dict) -> bool:
    """检查促销是否有效"""
    now = datetime.now()
    
    start_time = datetime.fromisoformat(promo.get("start_time", "2020-01-01"))
    end_time = datetime.fromisoformat(promo.get("end_time", "2030-12-31"))
    
    if not (start_time <= now <= end_time):
        return False
    
    if promo.get("remaining_quota", 999) <= 0:
        return False
    
    return True


def issue_coupon(user_id: str, coupon_template: dict) -> dict:
    """发放优惠券"""
    coupon_id = f"CPN_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "coupon_id": coupon_id,
        "user_id": user_id,
        "coupon_template_id": coupon_template.get("template_id"),
        "coupon_name": coupon_template.get("name"),
        "discount_type": coupon_template.get("discount_type"),
        "discount_value": coupon_template.get("discount_value"),
        "min_amount": coupon_template.get("min_amount"),
        "valid_from": datetime.now().isoformat(),
        "valid_until": (datetime.now() + timedelta(days=coupon_template.get("valid_days", 30))).isoformat(),
        "status": "ACTIVE"
    }


def calculate_points(order: dict, rules: dict) -> dict:
    """计算积分"""
    goods_amount = order.get("goods_amount", 0)
    points_rate = rules.get("points_rate", 1)  # 每消费1元得1分
    
    earned_points = int(goods_amount * points_rate)
    
    # 会员等级加成
    member_level = order.get("member_level", "NORMAL")
    level_bonus = {
        "NORMAL": 1.0,
        "SILVER": 1.2,
        "GOLD": 1.5,
        "PLATINUM": 2.0
    }
    
    final_points = int(earned_points * level_bonus.get(member_level, 1.0))
    
    return {
        "order_id": order.get("order_id"),
        "user_id": order.get("user_id"),
        "goods_amount": goods_amount,
        "base_points": earned_points,
        "level_bonus": level_bonus.get(member_level, 1.0),
        "earned_points": final_points,
        "timestamp": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "calculate_discount")
    result = {}
    
    if action == "calculate_discount":
        result = calculate_discount(
            input_data.get("order", {}),
            input_data.get("promotions", [])
        )
    elif action == "issue_coupon":
        result = issue_coupon(
            input_data.get("user_id"),
            input_data.get("coupon_template", {})
        )
    elif action == "calculate_points":
        result = calculate_points(
            input_data.get("order", {}),
            input_data.get("rules", {})
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
