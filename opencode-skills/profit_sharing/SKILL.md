---
name: oms-profit-sharing
description: "Use when calculating profit distribution, querying commission details, or managing settlement rules. Triggers: query profit distribution, calculate commission, configure sharing rules, settlement query."
---

# O2O利益分配与自动分润

## Overview

解决"线上卖得好，线下加盟商觉得被抢了生意"的利益冲突。根据流量来源、导购引流、发货方等多维度自动计算分润。

## When to Use

- 查询订单分润明细
- 配置分润规则
- 生成结算单
- 查询结算状态

**触发词**: "分润"、"佣金结算"、"业绩归属"、"利润分配"、"导购提成"

## Core Pattern

### 参与方角色

| 角色 | 代码 | 说明 |
|------|------|------|
| 品牌商 | BRAND | 品牌总部 |
| 电商部门 | ECOM | 线上运营团队 |
| 加盟商 | FRANCHISEE | 加盟门店 |
| 直营店 | DIRECT | 直营门店 |
| 导购 | GUIDE | 销售人员 |

### 分润场景

**场景A - 门店发货**:
- 天猫订单分配给加盟店发货
- 分润规则：按吊牌价40%作为发货佣金

**场景B - 导购引流**:
- 顾客被A门店导购添加企业微信
- 两个月后该顾客在小程序下单
- 分润规则：10%算A门店业绩，5%算导购提成

**场景C - 跨店履约**:
- 顾客在A门店试穿，B门店发货
- 分润规则：试穿门店30%，发货门店70%

### 分润因子结构

```
allocation {
  party: string,           // 参与方代码
  role: enum,            // 角色类型
  base: enum,            // 计算基数
  rate: decimal,        // 分润比例
  amount: decimal        // 计算后的分润金额
}
```

## Quick Reference

### 分润规则优先级

| 优先级 | 规则类型 | 说明 |
|--------|----------|------|
| 1 | 导购专属码 | 有导购引流的订单优先 |
| 2 | 门店归属 | 顾客归属门店优先 |
| 3 | 发货方 | 谁发货谁拿履约佣金 |
| 4 | 默认分润 | 适用默认规则 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 比例超过100% | 规则无效 | 配置时校验 |
| 多规则冲突 | 分润错误 | 按优先级执行 |
| 历史订单修改 | 财务差错 | 冲红重算，不直接修改 |
