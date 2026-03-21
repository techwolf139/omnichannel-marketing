# 跨场景促销规则引擎 - 设计文档

## 1. 设计目标

构建灵活可配置的促销规则引擎，支持复杂的跨渠道营销玩法，实现"线上领券、线下核销"、"积分通兑"等场景。

## 2. 核心概念

### 2.1 促销规则结构

```
PromotionRule {
  rule_id: string,
  name: string,
  type: enum[cash|discount|coupon|points|gift],
  
  conditions: {
    channels: [string],        // 适用渠道
    categories: [string],      // 适用品类
    members: [string],         // 适用会员等级
    time_range: {start, end},  // 有效期
    thresholds: [{              // 门槛条件
      field: string,           // order_amount/category/...
      operator: string,        // gt/eq/between
      value: any
    }]
  },
  
  actions: {
    discount_type: string,     // 满减/折扣/赠品
    discount_value: decimal,
    points_multiplier: int,    // 积分倍数
    gift_sku: string           // 赠品SKU
  },
  
  cross_channel: {
    enabled: boolean,
    accumulate_channel: string,  // 积分累计渠道
    redeem_channel: string        // 积分兑换渠道
  }
}
```

### 2.2 规则匹配优先级

| 优先级 | 规则类型 | 说明 |
|--------|----------|------|
| 1 | 专属价/员工价 | 最高优先级 |
| 2 | 会员专享券 | 会员等级专属 |
| 3 | 渠道专享券 | 特定渠道领取 |
| 4 | 通用促销 | 全渠道适用 |
| 5 | 叠加优惠 | 可与其他优惠叠加 |

## 3. 核心能力

### 3.1 规则配置

- 支持可视化的规则配置界面
- 支持规则的测试环境验证
- 支持规则的草稿/发布/暂停/下线状态管理

### 3.2 券码发放

- 支持批量发放和实时发放
- 支持渠道限定（微信/短信/APP）
- 支持定向发放（导购指定用户）

### 3.3 积分联动

- 实时同步各渠道积分变动
- 支持积分抵扣订单金额
- 支持积分兑换礼品/服务

## 4. 能力边界

### 4.1 支持的操作

- `create_promotion`: 创建促销规则
- `match_promotion`: 查询用户可用的促销
- `issue_coupon`: 发放优惠券
- `calculate_discount`: 计算订单优惠
- `sync_points`: 同步积分变动

### 4.2 限制说明

- 促销规则最多嵌套3层条件
- 单次批量发放上限10000张券
- 积分同步延迟不超过1分钟

## 5. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| RULE_NOT_ACTIVE | 规则未激活 | 提示检查规则状态 |
| USER_NOT_ELIGIBLE | 用户不符合条件 | 返回不匹配原因 |
| COUPON_STOCK_EMPTY | 券库存不足 | 提示补货或结束活动 |
| CHANNEL_NOT_SUPPORTED | 渠道不支持 | 返回支持的渠道列表 |
