# OMS Skills 测试指南

## 概述

本测试框架用于自动化测试所有OMS技能脚本，支持单元测试和集成测试（技能链测试）。

## 快速开始

### 1. 运行所有测试

```bash
cd ~/git/oms/opencode-skills
python3 test_framework.py
```

### 2. 测试指定技能

```bash
python3 test_framework.py --skill inventory_realtime
python3 test_framework.py --skill order_capture
```

### 3. 运行示例流程

```bash
python3 test_framework.py --example
```

### 4. 运行技能链测试

```bash
python3 test_framework.py --chain test_chains.json
```

## 测试用例

### 单元测试

每个技能都有对应的测试用例，定义在 `test_framework.py` 的 `TEST_CASES` 字典中。

| 技能 | 测试用例 |
|------|----------|
| inventory_realtime | 查询库存、检查超卖、预扣库存、释放库存 |
| inventory_ringfence | 设置圈围、释放圈围、检查可用、门店检查 |
| order_capture | 订单标准化、黄牛检测、去重 |
| one_id_merge | 用户识别、身份合并、冲突解决、用户画像 |
| order_routing | 路由计算、订单拆分 |
| promotion_engine | 优惠计算、发放优惠券、积分计算 |
| profit_sharing | 佣金计算、利润分成、结算单生成 |
| reconciliation | 账单核对、凭证生成、报表导出 |
| returns_crosschannel | 资格检查、退款处理、换货处理 |
| returns_logistics | 物流追踪、质量检验、缺陷分类 |

### 集成测试（技能链）

定义在 `test_chains.json` 中，包含三个完整业务流程：

1. **订单创建到履约全流程**
   - 订单捕获 → 用户识别 → 库存检查 → 促销计算 → 订单路由 → 佣金计算

2. **退货处理全流程**
   - 资格检查 → 退款处理 → 物流追踪 → 质量检验 → 缺陷分类 → 库存检查

3. **对账全流程**
   - 账单核对 → 凭证生成 → 报表导出

## 输出示例

```
========================================================================
OMS Skills 自动化测试
========================================================================
开始时间: 2024-01-21 23:50:00

📦 测试技能: inventory_realtime
--------------------------------------------------
  query: ✅ PASS
  check_overselling: ✅ PASS
  pre_reserve: ✅ PASS
  release: ✅ PASS

📦 测试技能: inventory_ringfence
--------------------------------------------------
  set_ringfence: ✅ PASS
  release_ringfence: ✅ PASS
  check: ✅ PASS
  store_check: ✅ PASS
...

========================================================================
测试结果汇总
========================================================================
总测试数: 40
通过: 40
失败: 0
通过率: 100.0%
```

## 技能间数据传递

技能之间通过JSON进行数据传递，每个技能的输出可以作为下一个技能的输入。

### 示例：订单处理流程

```python
# Step 1: 订单标准化
result1 = run_skill("order_capture", "normalize", order_data)
# 输出: {"order_id": "...", "customer": {...}, "items": [...]}

# Step 2: 库存检查 (使用上一步的SKU)
result2 = run_skill("inventory_realtime", "check_overselling", {
    "sku_id": result1["items"][0]["sku_id"],
    "quantity": result1["items"][0]["quantity"]
})
# 输出: {"risk_level": "LOW", "can_fulfill": True, ...}

# Step 3: 促销计算
result3 = run_skill("promotion_engine", "calculate_discount", {
    "order": {"order_id": result1["order_id"], "goods_amount": ...},
    "promotions": [...]
})
```

## 扩展测试

### 添加新测试用例

在 `TEST_CASES` 字典中添加：

```python
TEST_CASES = {
    "your_skill": {
        "your_action": {
            "input_key": "input_value"
        }
    }
}
```

### 添加新技能链

在 `test_chains.json` 中添加：

```json
{
  "chain_test_x": {
    "name": "流程名称",
    "steps": [
      {"skill": "...", "action": "...", "input": {...}},
      {"skill": "...", "action": "...", "input": {...}}
    ]
  }
}
```

## 目录结构

```
opencode-skills/
├── test_framework.py      # 测试框架主程序
├── test_chains.json       # 技能链测试用例
├── README.md              # 本文件
├── inventory_realtime/
│   └── scripts/
│       └── inventory_query.py
├── order_capture/
│   └── scripts/
│       └── order_processor.py
└── ...
```
