---
name: oms-promotion-engine
description: "Use when configuring marketing promotions, issuing coupons, calculating discounts, or managing loyalty points. Triggers: send coupon, create promotion, calculate discount, points redemption, cross-channel marketing rules."
---

# 跨场景促销规则引擎

## Overview

配置和执行打通线上线下的复杂营销玩法，支持积分、优惠券、赠品等多种促销形式。实现"线上领券线下核销"、"积分通兑"等跨渠道联动。

## When to Use

- 创建促销活动（满减、折扣、赠品）
- 向用户发放定向优惠券
- 计算订单优惠金额
- 管理会员积分
- 配置跨渠道营销规则

**触发词**: "发优惠券"、"创建促销"、"计算折扣"、"积分"、"满减"

## Core Pattern

### 促销类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 满减券 | 满额减金额 | 满300减50 |
| 折扣券 | 指定折扣 | 秋冬装8折 |
| 积分翻倍 | 指定品类积分加倍 | 母婴类2倍积分 |
| 赠品 | 满额赠礼 | 买一送一 |
| 专属价 | 会员/导购专属价 | 内部员工价 |

### 规则匹配优先级

| 优先级 | 规则类型 | 说明 |
|--------|----------|------|
| 1 | 专属价/员工价 | 最高优先级 |
| 2 | 会员专享券 | 会员等级专属 |
| 3 | 渠道专享券 | 特定渠道领取 |
| 4 | 通用促销 | 全渠道适用 |

## Quick Reference

### 跨渠道联动场景

**场景A**: "线上下单累积积分，线下兑换"
- 用户在天猫下单，获得积分
- 积分同步至品牌会员账户
- 用户前往门店，出示积分兑换体验服务

**场景B**: "线下试穿缺码，线上优惠券引导"
- 门店缺码，导购发送专属优惠券
- 用户通过券链接跳转小程序下单
- 订单归属关联导购业绩

## Implementation

### 促销规则结构

```
PromotionRule {
  rule_id: string,
  name: string,
  type: enum[cash|discount|coupon|points|gift],
  
  conditions: {
    channels: [string],
    categories: [string],
    time_range: {start, end}
  },
  
  actions: {
    discount_value: decimal,
    points_multiplier: int,
    gift_sku: string
  }
}
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 促销规则嵌套过深 | 难以维护 | 最多3层条件 |
| 批量发放超限 | 系统压力 | 单次不超过10000张 |
| 忽略积分同步延迟 | 用户体验差 | 延迟不超过1分钟 |
