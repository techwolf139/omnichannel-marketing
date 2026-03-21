---
name: oms-returns-logistics
description: "Use when tracking return packages, performing quality inspections, or managing defect classification. Triggers: return package tracking issues, quality check delays, defect grading disputes, inventory recycling failures."
---

# 逆向物流与残次鉴定

## Overview

处理退货物流的回收、质检、残次鉴定和库存再流转。根据鉴定结果自动分流（就地销售/退回大仓/报废），降低退货损失。

## When to Use

- 追踪退货物流
- 提交质检结果
- 处理残次品
- 生成维修工单

**触发词**: "退货物流"、"质检鉴定"、"残次"、"库存再流转"、"逆向"、"退货追踪"

## Core Pattern

### 质检鉴定等级

| 等级 | 条件 | 库存去向 |
|------|------|----------|
| A | 全新，吊牌/包装完整 | 原渠道可售 |
| B | 已拆封，无损坏/污渍 | 本地门店可售 |
| C | 有轻微瑕疵（可修复） | 特卖/奥莱渠道 |
| D | 严重损坏/功能故障 | 维修或报废 |

### 库存再流转

```
质检完成 → 系统自动分流:
  ├── A级 → 返回原渠道库存
  ├── B级 → 门店就地销售库存
  ├── C级 → 标记特卖渠道
  └── D级 → 生成维修工单 或 报废处理
```

### 逆向物流状态机

```
PENDING_PICKUP → IN_TRANSIT → RECEIVED → 
QUALITY_CHECK → PROCESSING → COMPLETED
```

## Quick Reference

### 就地再销售优势

门店收到线上退货，鉴定为B级品：
- 系统自动标记为"门店可售"
- 即刻上架门店库存
- 无需寄回总仓
- 极大降低物流成本和库存折旧

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 质检超时 | 退款延迟 | 收货后24小时内完成 |
| 拍照留证不足 | 争议难处理 | 每退货件至少2张照片 |
| 维修工单延误 | 客户投诉 | 工单生成后7天内处理 |
