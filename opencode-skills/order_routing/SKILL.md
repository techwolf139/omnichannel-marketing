---
name: oms-order-routing
description: "Use when determining fulfillment path, splitting/merging orders, or calculating optimal delivery route. Triggers: order allocation, route calculation, split order, merge orders, fulfillment path query."
---

# 智能订单路由与拆合单

## Overview

基于算法决定订单最优履约路径，综合成本、时效、距离多维度因素自动计算。支持订单智能拆分与合并，系统自动评估最优方案。

## When to Use

- 确定订单由哪个仓库/门店发货
- 计算最优履约路径
- 拆单或合单决策
- 查询订单履约状态

**触发词**: "路由订单"、"拆分订单"、"合并订单"、"履约路径"、"发货方"

## Core Pattern

### 路由策略

| 策略类型 | 触发条件 | 路由结果 |
|----------|----------|----------|
| 就近履约 | 收货地址5公里内有门店有货 | 门店发货+同城骑手 |
| 成本最优 | 门店无货 | 区域仓快递 |
| 时效优先 | 顾客选择极速达 | 就近门店优先 |
| 利润最优 | 高价值订单 | 优先利润空间大的履约方 |

### 成本-时效加权模型

```
Score = α × Cost + β × Time + γ × Distance

α: 成本权重（默认0.4）
β: 时效权重（默认0.4）
γ: 距离权重（默认0.2）
```

## Quick Reference

### 拆合单场景

**拆分**: 顾客购买的衣服在A仓，鞋在B仓 → 系统评估拆成两个包裹 vs 调拨合并发货，选择成本更低/时效更快方案

**合单**: 同一顾客短时间内多笔订单 → 系统自动合并为一个包裹发货

## Implementation

### 履约网络结构

```
FulfillmentNetwork {
  warehouses: [
    {id, name, type: rdc|cdc|fdc, location}
  ],
  stores: [
    {id, name, location, capability: pickup|deliver}
  ],
  delivery_partners: [
    {id, name, type: sf|jt|mt|ele, coverage}
  ]
}
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 路由计算超时 | 订单积压 | 3秒内必须返回，降级成本优先 |
| 拆分条件不满足 | 客户体验差 | 返回不可拆原因 |
| 已发货订单合单 | 物流混乱 | 已发货不允许合单 |
