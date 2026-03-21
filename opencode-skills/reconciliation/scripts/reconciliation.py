#!/usr/bin/env python3
"""
对账脚本
多渠道账单核对
"""

import json
import sys
from datetime import datetime


def reconcile_bills(platform_bills: list, system_bills: list) -> dict:
    """账单核对"""
    # 按渠道和订单ID建立索引
    platform_index = {
        (bill.get("channel"), bill.get("order_id")): bill
        for bill in platform_bills
    }
    
    matched = []
    unmatched_platform = []
    unmatched_system = []
    
    for sys_bill in system_bills:
        key = (sys_bill.get("channel"), sys_bill.get("order_id"))
        
        if key in platform_index:
            pf_bill = platform_index[key]
            
            # 比对金额
            pf_amount = pf_bill.get("amount", 0)
            sys_amount = sys_bill.get("amount", 0)
            
            is_match = abs(pf_amount - sys_amount) < 0.01
            
            matched.append({
                "order_id": sys_bill.get("order_id"),
                "channel": sys_bill.get("channel"),
                "platform_amount": pf_amount,
                "system_amount": sys_amount,
                "difference": round(pf_amount - sys_amount, 2),
                "match": is_match
            })
            
            if not is_match:
                unmatched_platform.append(pf_bill)
                unmatched_system.append(sys_bill)
        else:
            unmatched_system.append(sys_bill)
    
    # 检查平台有多出的账单
    for pf_bill in platform_bills:
        key = (pf_bill.get("channel"), pf_bill.get("order_id"))
        if key not in {(s.get("channel"), s.get("order_id")) for s in system_bills}:
            unmatched_platform.append(pf_bill)
    
    return {
        "summary": {
            "total_platform_bills": len(platform_bills),
            "total_system_bills": len(system_bills),
            "matched_count": len(matched),
            "unmatched_count": len(unmatched_platform) + len(unmatched_system)
        },
        "matched": matched,
        "unmatched_platform": unmatched_platform,
        "unmatched_system": unmatched_system,
        "reconciliation_rate": round(len(matched) / max(len(platform_bills), 1) * 100, 2),
        "timestamp": datetime.now().isoformat()
    }


def generate_voucher(bill: dict, voucher_type: str = "INCOME") -> dict:
    """生成会计凭证"""
    voucher_id = f"VCH_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if voucher_type == "INCOME":
        debit_account = "应收账款"
        credit_account = "主营业务收入"
    else:  # EXPENSE
        debit_account = "管理费用"
        credit_account = "应付账款"
    
    return {
        "voucher_id": voucher_id,
        "voucher_type": voucher_type,
        "order_id": bill.get("order_id"),
        "channel": bill.get("channel"),
        "amount": bill.get("amount"),
        "entries": [
            {"account": debit_account, "debit": bill.get("amount"), "credit": 0},
            {"account": credit_account, "debit": 0, "credit": bill.get("amount")}
        ],
        "status": "GENERATED",
        "created_at": datetime.now().isoformat()
    }


def export_accounting_report(bills: list, period: dict) -> dict:
    """导出会计报表"""
    total_income = sum(b.get("amount", 0) for b in bills if b.get("type") == "INCOME")
    total_expense = sum(b.get("amount", 0) for b in bills if b.get("type") == "EXPENSE")
    
    # 按渠道汇总
    channel_summary = {}
    for bill in bills:
        channel = bill.get("channel", "UNKNOWN")
        if channel not in channel_summary:
            channel_summary[channel] = {"income": 0, "expense": 0, "count": 0}
        
        amount = bill.get("amount", 0)
        if bill.get("type") == "INCOME":
            channel_summary[channel]["income"] += amount
        else:
            channel_summary[channel]["expense"] += amount
        channel_summary[channel]["count"] += 1
    
    return {
        "report_id": f"RPT_{period.get('start_date')}_{period.get('end_date')}",
        "period": period,
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_profit": round(total_income - total_expense, 2),
        "channel_summary": channel_summary,
        "generated_at": datetime.now().isoformat()
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            input_data = json.load(f)
    else:
        input_data = json.load(sys.stdin)
    
    action = input_data.get("action", "reconcile")
    result = {}
    
    if action == "reconcile":
        result = reconcile_bills(
            input_data.get("platform_bills", []),
            input_data.get("system_bills", [])
        )
    elif action == "generate_voucher":
        result = generate_voucher(
            input_data.get("bill", {}),
            input_data.get("voucher_type", "INCOME")
        )
    elif action == "export_report":
        result = export_accounting_report(
            input_data.get("bills", []),
            input_data.get("period", {})
        )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
