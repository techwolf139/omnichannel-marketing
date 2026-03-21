# 全渠道订单汇聚与清洗 - 设计文档

## 1. 设计目标

构建统一的订单接入层，将分散在各平台的订单汇聚到中央订单池，消除数据孤岛，为后续订单路由和履约提供标准化的数据基础。

## 2. 核心概念

### 2.1 订单生命周期

```
订单状态流转:
CREATED →PAID → ALLOCATED → PICKING → SHIPPED → DELIVERED
                ↓
            CANCELLED

退换货逆向:
DELIVERED → RETURN_REQUEST → RETURNED → REFUNDED
```

### 2.2 订单标准化模型

```
StandardOrder {
  order_id: string,                    // 内部订单号
  source_order_id: string,              // 平台原始订单号
  source_channel: enum,                 // 订单来源平台
  
  customer: {
    one_id: string,                    // One-ID归一
    phone: string,                     // 脱敏手机号
    member_level: string
  },
  
  items: [{
    sku_id: string,                    // 内部SKU
    sku_name: string,
    quantity: int,
    unit_price: decimal,
    discount: decimal,
    final_price: decimal
  }],
  
  shipping: {
    receiver_name: string,
    phone: string,
    province: string,
    city: string,
    district: string,
    address: string,
    postal_code: string
  },
  
  amounts: {
    goods_amount: decimal,             // 商品总额
    shipping_fee: decimal,             // 运费
    discount_amount: decimal,           // 优惠金额
    coupon_amount: decimal,            // 券抵扣
    points_deduction: decimal,         // 积分抵扣
    order_amount: decimal              // 订单实付
  },
  
  status: enum,
  created_at: datetime,
  paid_at: datetime
}
```

## 3. 核心能力

### 3.1 订单接入

- 支持API拉取和WebSocket推送两种模式
- 定时拉取间隔：主流平台5分钟，即时配送平台1分钟
- 订单去重：基于source_order_id + source_channel联合去重

### 3.2 黄牛识别

| 识别维度 | 规则 | 处理方式 |
|----------|------|----------|
| 手机号段 | 170/171号段高风险 | 标记待审核 |
| 收货地址 | 同一地址高频下单 | 标记风控 |
| 购买行为 | 同SKU大量购买 | 限购提示 |
| 设备指纹 | 同一设备多账号 | 合并风控 |

### 3.3 数据清洗

- 隐私面单解密（需用户授权）
- 地址智能补全与纠错
- 商品SKU自动映射

## 4. 能力边界

### 4.1 支持的操作

- `query_orders`: 多条件查询订单
- `get_order_detail`: 查询订单详情
- `sync_order_status`: 同步订单状态
- `flag_suspicious`: 标记异常订单

### 4.2 限制说明

- 单次查询最多返回1000条记录
- 历史订单查询范围不超过90天
- 订单数据保留期限：3年

## 5. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| CHANNEL_API_ERROR | 平台API异常 | 降级拉取，重试3次 |
| ORDER_NOT_FOUND | 订单不存在 | 返回空结果 |
| SYNC_DELAY | 同步延迟 | 返回最近可用数据 |
| DECRYPT_FAILED | 隐私面单解密失败 | 标记，待人工处理 |
