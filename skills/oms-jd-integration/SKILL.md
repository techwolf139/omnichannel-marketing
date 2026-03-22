---
name: oms-jd-integration
description: "Use when integrating with JD.com (京东) Open Platform, synchronizing JD orders, managing JD inventory, tracking JD logistics, or processing JD returns and refunds."
---

# 京东开放平台集成适配器

## Overview

京东开放平台（JD Open Platform）对接适配器，实现订单获取、库存同步、物流追踪、退货处理等核心功能。采用适配器模式，将京东API响应转换为OMS标准模型。

## When to Use

- 从京东平台同步订单
- 查询京东订单状态
- 同步京东商品库存
- 追踪京东物流轨迹
- 处理京东退货退款

**触发词**: "京东订单"、"京东库存"、"京东物流"、"京东退货"、"JD"

## Core Pattern

### 京东API分类

| 类别 | 核心API | 说明 |
|------|---------|------|
| 订单 | `jd.order.search`, `jd.order.detail.get` | 订单查询与详情 |
| 商品 | `jd.product.ware.list`, `jd.product.sku.list` | 商品SKU查询 |
| 库存 | `jd.ware.inventory.securable.update` | 库存更新 |
| 物流 | `jd.logistics.order.search` | 物流轨迹 |
| 退货 | `jd.returnorder.apply`, `jd.refund.order.info` | 退货退款 |

### 认证方式

OAuth 2.0 + MD5签名验证

## Implementation

### 数据模型

**JDAuthConfig**:
```python
{
    "app_key": str,
    "app_secret": str,
    "access_token": str,
    "refresh_token": str,
    "token_expires_at": datetime
}
```

**JDOrder** (京东原始订单):
```python
{
    "jd_order_id": str,
    "order_state": int,      # 1-待支付, 2-已支付, 3-等待发货...
    "consignee_name": str,
    "consignee_mobile": str,
    "address_detail": str,
    "item_info_list": [...],
    "order_payment": decimal,
    "freight_price": decimal,
    "order_start_time": datetime
}
```

### 状态映射

**订单状态**:
| JD状态码 | OMS状态 |
|----------|---------|
| 1 | CREATED |
| 2 | PAID |
| 3 | ALLOCATED |
| 4 | PICKING |
| 5 | SHIPPED |
| 6 | DELIVERED |
| 7/99 | CANCELLED |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 订单搜索 | `order_search()` | 1000/分钟 |
| 订单详情 | `order_detail_get()` | 1000/分钟 |
| 库存更新 | `inventory_update()` | 500/分钟 |
| 物流查询 | `logistics_search()` | 500/分钟 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| token过期未刷新 | API调用失败 | 定期检查并自动刷新 |
| 签名算法错误 | 签名校验失败 | 使用京东标准MD5签名 |
| 限流未处理 | 请求被拒 | 实现指数退避重试 |
| 订单状态映射错误 | 状态不一致 | 严格按映射表转换 |
