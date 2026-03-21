#!/usr/bin/env python3
"""
OMS 技能间数据传递示例
演示如何通过 JSON 在各技能之间传递数据
"""

import json
import sys
import subprocess
from pathlib import Path


# 技能脚本路径
SCRIPTS_DIR = Path(__file__).parent


def run_skill_script(skill_name: str, action: str, input_data: dict) -> dict:
    """运行指定技能的脚本并返回JSON结果"""
    
    script_map = {
        "inventory_realtime": "inventory_query.py",
        "inventory_ringfence": "ringfence_manager.py",
        "order_capture": "order_processor.py",
        "one_id_merge": "one_id_manager.py",
        "order_routing": "order_router.py",
        "promotion_engine": "promotion_calculator.py",
        "profit_sharing": "profit_calculator.py",
        "reconciliation": "reconciliation.py",
        "returns_crosschannel": "return_handler.py",
        "returns_logistics": "return_logistics.py"
    }
    
    script_path = SCRIPTS_DIR / skill_name / "scripts" / script_map.get(skill_name)
    
    if not script_path.exists():
        return {"error": f"Script not found: {script_path}"}
    
    # 写入临时输入文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"action": action, **input_data}, f)
        input_file = f.name
    
    try:
        result = subprocess.run(
            ["python3", str(script_path), input_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr}
    finally:
        import os
        os.unlink(input_file)


def example_order_to_delivery_flow():
    """
    示例：订单从创建到履约的完整流程
    展示技能间数据传递
    """
    print("=" * 60)
    print("示例：订单履约全流程（技能间数据传递）")
    print("=" * 60)
    
    # Step 1: 订单捕获 -> 订单标准化
    print("\n[Step 1] 订单捕获与标准化...")
    order_data = {
        "order_id": "ORD20240120001",
        "source_order_id": "TB123456789",
        "channel": "taobao",
        "phone": "13800138000",
        "receiver_address": "上海市浦东新区张江路100号",
        "items": [{"sku_code": "SKU001", "num": 2, "price": 99.00}],
        "goods_amount": 198.00,
        "shipping_fee": 10.00,
        "discount_amount": 20.00,
        "total_amount": 188.00,
        "created_time": "2024-01-20T10:00:00"
    }
    
    result1 = run_skill_script("order_capture", "normalize", {"order": order_data})
    print(f"标准化订单: {result1.get('order_id')}")
    
    # Step 2: OneID 匹配 -> 获取用户画像
    print("\n[Step 2] 用户身份识别...")
    result2 = run_skill_script("one_id_merge", "identify", {
        "identifier": {"type": "phone", "value": "13800138000"}
    })
    print(f"用户ID: {result2.get('matches', [{}])[0].get('one_id')}")
    
    # Step 3: 库存预扣检查
    print("\n[Step 3] 库存检查与预扣...")
    sku_id = result1.get("items", [{}])[0].get("sku_id")
    result3 = run_skill_script("inventory_realtime", "check_overselling", {
        "sku_id": sku_id,
        "quantity": 2
    })
    print(f"超卖风险: {result3.get('risk_level')}")
    
    # Step 4: 促销计算
    print("\n[Step 4] 促销优惠计算...")
    promotions = [
        {"promo_id": "P001", "type": "COUPON", "discount_type": "FIXED",
         "discount_value": 20, "min_amount": 100, "start_time": "2024-01-01",
         "end_time": "2024-12-31", "remaining_quota": 1000}
    ]
    result4 = run_skill_script("promotion_engine", "calculate_discount", {
        "order": {"order_id": "ORD20240120001", "goods_amount": 198.00, "items": result1.get("items", [])},
        "promotions": promotions
    })
    print(f"优惠金额: {result4.get('total_discount')}, 最终金额: {result4.get('final_amount')}")
    
    # Step 5: 订单路由
    print("\n[Step 5] 计算最优履约路径...")
    warehouses = [
        {"id": "WH001", "name": "上海仓", "lat": 31.2304, "lon": 121.4737},
        {"id": "WH002", "name": "武汉仓", "lat": 30.5928, "lon": 114.3055}
    ]
    stores = [
        {"id": "STORE001", "name": "上海浦东店", "lat": 31.2304, "lon": 121.4737}
    ]
    result5 = run_skill_script("order_routing", "route", {
        "order": {"order_id": "ORD20240120001", "customer_lat": 31.2304, "customer_lon": 121.4737},
        "warehouses": warehouses,
        "stores": stores
    })
    print(f"推荐仓库: {result5.get('recommended', {}).get('source_name')}")
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("流程执行完成！")
    print("=" * 60)
    
    return {
        "order": result1,
        "customer": result2,
        "inventory": result3,
        "promotion": result4,
        "routing": result5
    }


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--example":
        example_order_to_delivery_flow()
    else:
        # 技能调用接口
        if len(sys.argv) > 1:
            with open(sys.argv[1], 'r') as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)
        
        result = run_skill_script(
            data.get("skill"),
            data.get("action"),
            data.get("input", {})
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
