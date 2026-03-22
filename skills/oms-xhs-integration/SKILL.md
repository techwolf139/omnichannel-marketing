---
name: oms-xhs-integration
description: "Use when integrating with Xiaohongshu (小红书) platform, tracking note exposure data, managing KOL collaborations, synchronizing 薯店/shuxidian orders, or processing 小程序/wechat mini-program orders."
---

# 小红书开放平台集成适配器

## Overview

小红书（Xiaohongshu）开放平台对接适配器，实现笔记曝光数据、KOL合作管理、薯店订单同步、小程序订单同步四大核心功能。采用适配器模式，将小红书API响应转换为OMS标准模型。

## When to Use

- 查询小红书笔记曝光/互动数据
- 管理KOL合作（蒲公英平台）
- 同步薯店订单状态
- 同步小程序订单状态
- 归因分析（种草 → 转化）

**触发词**: "小红书"、"XHS"、"薯店"、"蒲公英"、"KOL"

## Core Pattern

### 小红书API分类

| 类别 | 核心API | 说明 |
|------|---------|------|
| 笔记数据 | `note.exposure.get`, `note.interaction.get` | 笔记曝光/互动数据 |
| KOL合作 | `pugongyin.order.list`, `pugongyin.order.detail` | 蒲公英合作订单 |
| 薯店订单 | `order.search`, `order.detail.get` | 薯店电商订单 |
| 小程序订单 | `mini.order.list`, `mini.order.detail` | 微信小程序订单 |

### 认证方式

OAuth 2.0 + MD5签名验证

## Implementation

### 数据模型

**XHSAuthConfig**:
```python
{
    "app_id": str,
    "app_secret": str,
    "access_token": str,
    "refresh_token": str,
    "token_expires_at": datetime
}
```

**XHSNoteExposure** (笔记曝光数据):
```python
{
    "note_id": str,
    "title": str,
    "exposure_count": int,
    "like_count": int,
    "collect_count": int,
    "comment_count": int,
    "share_count": int,
    "publish_time": datetime
}
```

**XHSOrder** (薯店/小程序原始订单):
```python
{
    "xhs_order_id": str,
    "order_type": str,        # "SHU_DIAN" | "MINI_PROGRAM"
    "order_state": int,       # 1-待支付, 2-已支付, 3-已发货, 4-已完成, 5-已取消
    "buyer_nickname": str,
    "receiver_name": str,
    "receiver_mobile": str,
    "address_detail": str,
    "item_list": [...],
    "total_amount": decimal,
    "pay_time": datetime
}
```

### 状态映射

**薯店/小程序订单状态**:
| XHS状态码 | OMS状态 |
|-----------|---------|
| 1 | CREATED |
| 2 | PAID |
| 3 | SHIPPED |
| 4 | DELIVERED |
| 5 | CANCELLED |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 笔记曝光查询 | `note_exposure_get()` | 200/分钟 |
| 笔记互动查询 | `note_interaction_get()` | 200/分钟 |
| KOL订单列表 | `kol_order_list()` | 100/分钟 |
| 薯店订单搜索 | `order_search()` | 200/分钟 |
| 小程序订单搜索 | `mini_order_search()` | 200/分钟 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| token过期未刷新 | API调用失败 | 定期检查并自动刷新 |
| 签名算法错误 | 签名校验失败 | 使用小红书标准MD5签名 |
| 限流未处理 | 请求被拒 | 实现指数退避重试 |
| 归因窗口遗漏 | 归因数据不完整 | 订单前30天触点都计入 |
