---
name: oms-reconciliation
description: "Use when reconciling multi-channel bills, generating financial vouchers, or exporting accounting reports. Triggers: generate reconciliation report, create voucher, sync bills, export financial statements."
---

# 全渠道对账与财务凭证

## Overview

统一处理全渠道账单对账，自动核对订单流水与平台账单，发现差异自动标记。根据对账结果生成标准财务凭证，对接金蝶/用友等财务ERP。

## When to Use

- 生成对账报表
- 核对各平台账单
- 生成财务凭证
- 导出财务报表

**触发词**: "对账"、"财务报表"、"凭证生成"、"账单核对"、"业财一体"

## Core Pattern

### 对账类型

| 类型 | 说明 | 频率 |
|------|------|------|
| 日对账 | 每日核对前一日流水 | T+1 |
| 周对账 | 按周汇总核对 | 周一 |
| 月对账 | 月末结账前全面核对 | 月底 |

### 账单差异类型

| 类型 | 代码 | 说明 |
|------|------|------|
| 金额差异 | AMT_DIFF | 订单金额与账单不符 |
| 平台扣点差 | FEE_DIFF | 平台扣点与预估不符 |
| 退款未达 | REFUND_MISS | 退款未在账单体现 |
| 隐藏优惠 | HIDDEN_DISC | 平台额外优惠未记录 |

### 业财一体化流程

```
OMS订单 → 收入确认 → 分润计算 → 凭证生成 → 推送ERP
```

## Quick Reference

### 凭证分录示例

**收入确认凭证**:
```
借: 应收账款-平台  100
贷: 商品销售收入   85
贷: 应交增值税     15
```

**退款凭证**:
```
借: 商品销售收入   (退款金额，红字)
贷: 应收账款-平台  (退款金额)
```

**分润凭证**:
```
借: 销售费用-佣金  (分润金额)
贷: 应付账款-门店  (应付门店)
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 对账期间超限 | 性能问题 | 最多90天 |
| 凭证分录超限 | 处理失败 | 单次最多100条 |
| 已过账修改 | 合规风险 | 不允许，支持冲红 |
