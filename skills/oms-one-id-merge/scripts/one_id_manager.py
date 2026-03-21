#!/usr/bin/env python3
"""
OneID 合并脚本
跨渠道用户身份识别与合并
"""

import json
import sys
from datetime import datetime


def identify_customer(identifier: dict) -> dict:
    """根据标识查找用户"""
    id_type = identifier.get("type")  # phone, openid, unionid, one_id
    id_value = identifier.get("value")
    
    # 模拟查询 - 实际应调用OneID服务
    mock_results = {
        "phone": [
            {"one_id": "OID001", "phone": "138****1234", "channels": ["taobao", "jd"]}
        ],
        "openid": [
            {"one_id": "OID002", "openid": "oXXXX", "channel": "douyin"}
        ],
        "unionid": [
            {"one_id": "OID003", "unionid": "uXXXX", "channels": ["wechat", "jd"]}
        ]
    }
    
    results = mock_results.get(id_type, [])
    
    return {
        "query": identifier,
        "found": len(results) > 0,
        "matches": results,
        "timestamp": datetime.now().isoformat()
    }


def merge_identities(source_one_id: str, target_one_id: str, reason: str = "") -> dict:
    """合并用户身份"""
    return {
        "merge_id": f"MERGE_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "source_one_id": source_one_id,
        "target_one_id": target_one_id,
        "reason": reason,
        "status": "PENDING_VERIFICATION",
        "created_at": datetime.now().isoformat()
    }


def resolve_conflict(merge_request: dict, resolution: str) -> dict:
    """解决合并冲突"""
    # resolution: "KEEP_A", "KEEP_B", "MERGE_BOTH"
    
    return {
        "merge_id": merge_request.get("merge_id"),
        "resolution": resolution,
        "resolved_at": datetime.now().isoformat(),
        "status": "COMPLETED" if resolution else "REJECTED"
    }


def build_customer_profile(one_id: str) -> dict:
    """构建用户画像"""
    # 模拟数据
    return {
        "one_id": one_id,
        "profile": {
            "total_orders": 156,
            "total_spent": 28560.00,
            "avg_order_value": 183.08,
            "member_level": "GOLD",
            "first_order_date": "2023-03-15",
            "last_order_date": "2024-01-20",
            "preferred_channels": ["taobao", "jd"],
            "preferred_payment": ["alipay", "wechat"]
        },
        "channel_accounts": [
            {"channel": "taobao", "account": "tb_***", "绑定时间": "2023-01-01"},
            {"channel": "jd", "account": "jd_***", "绑定时间": "2023-03-15"},
            {"channel": "douyin", "account": "dy_***", "绑定时间": "2023-06-20"}
        ],
        "purchase_history": {
            "categories": ["电子产品", "服装", "家居"],
            "brands": ["Apple", "华为", "小米"],
            "tags": ["数码爱好者", "性价比敏感"]
        }
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "identify")
    result = {}
    
    if action == "identify":
        result = identify_customer(input_data.get("identifier", {}))
    elif action == "merge":
        result = merge_identities(
            input_data.get("source_one_id"),
            input_data.get("target_one_id"),
            input_data.get("reason", "")
        )
    elif action == "resolve_conflict":
        result = resolve_conflict(
            input_data.get("merge_request", {}),
            input_data.get("resolution")
        )
    elif action == "build_profile":
        result = build_customer_profile(input_data.get("one_id"))
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
