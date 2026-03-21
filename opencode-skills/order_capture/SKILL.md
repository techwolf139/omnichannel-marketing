---
name: oms-order-capture
description: "Use when querying orders from multiple channels, reconciling platform bills, or identifying abnormal orders. Triggers: check orders by channel, sync orders, identify suspicious orders, order query by date/customer."
---

# 全渠道订单汇聚与清洗

## Overview

统一接入全网订单来源（淘系、京东、抖店、微信小程序、美团/饿了么），标准化清洗后汇聚到统一订单池。自动识别黄牛、地址异常等风险订单。

## When to Use

- 查询各平台订单
- 对账各渠道账单
- 识别异常/黄牛订单
- 订单数据标准化

**触发词**: "查订单"、"同步订单"、"渠道订单"、"异常订单"、"对账"

## Core Pattern

### 订单来源接入

| 平台类型 | 接入方式 | 订单特点 |
|----------|----------|----------|
| 淘系(天猫/淘宝) | API拉取 | 隐私面单，需解密 |
| 京东 | API拉取 | POP模式为主 |
| 拼多多 | API拉取 | 社交订单居多 |
| 抖音/快手 | 抖店API | 直播订单高并发 |
| 微信小程序 | 自主商城 | 品牌私域订单 |
| 美团/饿了么 | O2O平台API | 即时配送为主 |

### 黄牛识别规则

| 识别维度 | 规则 | 处理方式 |
|----------|------|----------|
| 手机号段 | 170/171号段高风险 | 标记待审核 |
| 收货地址 | 同一地址高频下单 | 标记风控 |
| 购买行为 | 同SKU大量购买 | 限购提示 |
| 设备指纹 | 同一设备多账号 | 合并风控 |

## Quick Reference

### 订单清洗规则

**收货地址标准化**: 省市区街道拆解、敏感信息脱敏、地址有效性校验

**商品信息标准化**: SKU编码映射、规格属性统一、售价/优惠价/券后价区分

## Implementation

### 订单标准化模型

```
StandardOrder {
  order_id: string,
  source_order_id: string,
  source_channel: enum,
  
  customer: {
    one_id: string,
    phone: string,
    member_level: string
  },
  
  items: [{
    sku_id: string,
    quantity: int,
    unit_price: decimal,
    final_price: decimal
  }],
  
  amounts: {
    goods_amount: decimal,
    shipping_fee: decimal,
    discount_amount: decimal,
    order_amount: decimal
  },
  
  status: enum,
  created_at: datetime
}
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 订单状态流转错误 | 履约异常 | 严格遵循状态机 |
| 隐私面单未解密 | 无法联系客户 | 标记待处理 |
| 去重逻辑遗漏 | 重复发货 | source_order_id + channel 联合去重 |
