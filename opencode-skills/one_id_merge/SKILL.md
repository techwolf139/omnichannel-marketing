---
name: oms-one-id-merge
description: "Use when needing to identify customers across channels, merge fragmented consumer identities, or query unified customer profiles. Triggers: customer lookup by phone/OpenID/UnionID, cross-channel purchase history, consumer profile queries."
---

# One-ID 归一与消费者画像融合

## Overview

将分散在多个渠道的消费者身份碎片合并为唯一超级ID，沉淀全渠道消费行为。通过置信度评分算法自动或手动合并重复身份，构建完整的单客视图。

## When to Use

- 查询用户在各渠道的购买记录
- 识别跨渠道的同一消费者
- 合并碎片化的消费者画像
- 构建精准营销人群包

**触发词**: "查一下这个用户"、"消费者画像"、"全渠道"、"One-ID"、"合并身份"

## Core Pattern

**归一算法 - 置信度评分**:

| 匹配因素 | 权重 | 说明 |
|----------|------|------|
| 手机号完全匹配 | 40% | 最高置信度 |
| 设备ID匹配 | 25% | 同一手机登录 |
| 收货地址重叠 | 20% | 相同收货人地址 |
| 行为特征相似 | 15% | 浏览/购买品类重叠 |

**归一决策**:
- 置信度 ≥ 90%: 自动归一
- 置信度 60%-90%: 需人工确认
- 置信度 < 60%: 不归一

## Quick Reference

### 支持的身份标识

| 渠道类型 | 身份标识 |
|----------|----------|
| 线下门店 | 手机号、会员卡、扫码OpenID |
| 天猫/京东 | 平台OpenID + 手机号绑定 |
| 抖音/快手 | 抖音OpenID、快手OpenID |
| 微信生态 | UnionID、小程序OpenID、企业微信会员ID |
| 品牌小程序 | 自主注册手机号、会员体系 |

### 隐私合规

- 手机号需脱敏展示（138****8888）
- 不存储未经授权的身份信息

## Implementation

### 数据模型

```
Consumer {
  one_id: string,           // 超级ID，UUID格式
  primary_identifier: {      // 主标识
    type: string,           // phone/openid/unionid
    value: string
  },
  identities: [{             // 所有关联身份
    channel: string,
    id_type: string,
    id_value: string,
    confidence: float,
    merged_at: datetime
  }],
  profile: {
    tags: [string],         // 偏好标签
    total_orders: int,
    total_amount: decimal
  }
}
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 直接暴露完整手机号 | 隐私合规风险 | 脱敏展示 138****8888 |
| 置信度60%直接归一 | 错误合并 | 必须人工确认 |
| 忽略渠道API异常 | 数据不完整 | 标记异常，返回已归一数据 |
