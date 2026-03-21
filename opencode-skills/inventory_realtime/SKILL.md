---
name: oms-inventory-realtime
description: "Use when checking stock levels, preventing overselling, or managing inventory across warehouses. Triggers: overselling incidents, stock level discrepancies, reservation failures, inventory sync delays."
---

# 库存水位实时映射与防超卖

## Overview

统揽全网库存水位（中央大仓、区域前置仓、门店库存、在途库存），实时向各销售渠道发布可售库存。采用预扣减机制防止超卖，支撑高并发场景。

## When to Use

- 查询SKU可售库存
- 监控各渠道可售情况
- 大促前检查库存准备
- 处理库存预占/释放

**触发词**: "查库存"、"可售数量"、"库存预占"、"超卖"、"防超卖"、"库存不准"

## Core Pattern

### 库存类型

| 类型 | 代码 | 说明 |
|------|------|------|
| 总库存 | TOTAL | 仓库中所有库存 |
| 可售库存 | AVAILABLE | 减去预占/隔离后的可卖数量 |
| 预占库存 | RESERVED | 已下单未支付 |
| 隔离库存 | RINGFENCED | 渠道专属库存 |
| 在途库存 | IN_TRANSIT | 调拨中 |

### 库存计算公式

```
渠道可售 = Σ(各仓可售) - 渠道预占 - 渠道隔离

单仓可售 = max(0, 总库存 - 预占 - 隔离)
```

### 防超卖 - 预扣减策略

```
用户下单 → 预扣库存 → 返回"库存锁定" → 
  ├── 支付成功 → 确认预扣 → 库存出库
  └── 超时未支付 → 释放预扣 → 库存可售
```

## Quick Reference

### 多层级库存映射

```
全国总仓 (RDC)
    ↓ 区域调拨
区域前置仓 (FDC)
    ↓ 铺货
线下门店 (STORE)
    ↓ 在途
在途库存 (IN_TRANSIT)
```

## Implementation

### 高并发场景（直播间秒杀）

10万用户同时抢购1000件商品：
- 下单瞬间预扣库存
- 15分钟未支付自动释放
- 绝对杜绝超卖

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 预占超时未释放 | 库存僵死 | 15分钟自动释放机制 |
| 原子性未保证 | 超卖 | 乐观锁+重试机制 |
| 多层级缓存不一致 | 数据不准 | 实时队列同步 |
