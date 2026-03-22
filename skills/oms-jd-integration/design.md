# 京东开放平台对接设计方案

## 1. 设计目标

实现OMS系统与京东开放平台的全对接，支持订单获取、库存同步、物流追踪、退货处理等核心功能。

## 2. 平台特点

| 特点 | 说明 |
|------|------|
| 接入模式 | POP模式（京东开放平台）为主，部分自营 |
| 订单特点 | POP订单为主，物流履约由商家负责 |
| 隐私面单 | 部分加密，需申请解密权限 |
| API限流 | 500次/分钟（库存类），1000次/分钟（订单类） |

## 3. API规范

| 项目 | 规范 |
|------|------|
| 协议 | HTTPS RESTful API |
| 认证 | OAuth 2.0 (app_key + app_secret + access_token) |
| 签名 | MD5签名验证 |
| 格式 | JSON |
| 编码 | UTF-8 |

## 4. 认证模块

### 4.1 授权流程

```
1. 商家在京东开放平台注册应用获取 app_key, app_secret
2. 通过 Authorization Code 模式获取 access_token
3. 调用API时携带 access_token
4. token过期时使用 refresh_token 刷新
```

### 4.2 认证配置

```python
JD_AUTH_CONFIG = {
    "app_key": "your_app_key",
    "app_secret": "your_app_secret",
    "access_token": "your_access_token",
    "refresh_token": "your_refresh_token",
    "token_expires_at": "2024-01-01T00:00:00Z",
    "server_url": "https://api.jd.com/routerjson"
}
```

## 5. 订单对接

### 5.1 订单状态映射

| JD状态码 | JD状态名 | OMS状态 | 说明 |
|----------|----------|---------|------|
| 1 | WAIT_PAY | CREATED | 待支付 |
| 2 | PAID | PAID | 已支付 |
| 3 | WAIT_SEND | ALLOCATED | 等待发货 |
| 4 | SEND | PICKING | 打包中 |
| 5 | ARRANGE | SHIPPED | 已发货 |
| 6 | SIGN | DELIVERED | 签收 |
| 7 | CANCEL | CANCELLED | 取消 |
| 99 | INVALID | CANCELLED | 无效 |

### 5.2 订单字段映射

```
JD订单字段 → OMS标准模型

order_id → order_id (内部订单号)
jd_order_id → source_order_id (京东订单号)
customer_id → one_id (归一ID)
vender_id → merchant_id (商家ID)
order_state → status (订单状态)
pay_type → payment_method (支付方式)
consignee_name → shipping.receiver_name (收货人)
consignee_mobile → shipping.phone (手机号)
address_detail → shipping.address (详细地址)
item_info_list[].sku_id → items[].sku_id (SKU)
item_info_list[].ware_name → items[].sku_name (商品名称)
item_info_list[].num → items[].quantity (数量)
item_info_list[].price → items[].unit_price (单价)
order_payment → amounts.order_amount (订单金额)
freight_price → amounts.shipping_fee (运费)
coupon_payment → amounts.coupon_amount (优惠金额)
order_start_time → created_at (下单时间)
pay_time → paid_at (支付时间)
```

### 5.3 订单同步策略

| 同步方式 | 说明 | 延迟 |
|----------|------|------|
| 增量拉取 | 每5分钟拉取增量订单 | 5-10分钟 |
| 全量拉取 | 每日凌晨全量同步 | T+1 |
| Webhook推送 | 订单状态变更实时推送 | <1秒 |

## 6. 库存对接

### 6.1 库存同步方向

```
OMS库存中心 → 京东可售库存

同步策略:
  1. OMS计算渠道可售库存 = Σ(各仓可售) - 渠道预占 - 渠道隔离
  2. 调用 jd.ware.inventory.securable.update 更新库存
  3. 记录同步日志
```

### 6.2 库存字段映射

```
OMS库存 → JD库存

sku_id → sku_id (SKU编号)
available_quantity → stock_num (可售库存)
locked_quantity → lock_stock_num (锁定库存)
```

## 7. 物流对接

### 7.1 物流状态映射

| JD物流状态 | OMS状态 | 说明 |
|------------|---------|------|
| ARRANGE | SHIPPED | 已发货 |
| DELIVERING | IN_TRANSIT | 配送中 |
| SIGN | DELIVERED | 已签收 |

### 7.2 运单字段映射

```
JD运单 → OMS物流

express_no → tracking_number (运单号)
express_name → carrier_name (承运商)
state → logistics_status (物流状态)
delivery_time → shipped_at (发货时间)
sign_time → delivered_at (签收时间)
```

## 8. 退货退款对接

### 8.1 退货状态映射

| OMS状态 | JD状态 | 说明 |
|---------|--------|------|
| RETURN_REQUEST | APPLIED | 买家申请退货 |
| RETURN_APPROVED | APPROVED | 审核通过 |
| RETURN_SHIPPED | SHIPPED | 买家已退货 |
| RETURN_RECEIVED | RECEIVED | 京东收货 |
| REFUNDED | REFUNDED | 退款完成 |

### 8.2 退货流程

```
OMS退货申请 → jd.returnorder.apply → 京东审核 → 买家退货 → 京东收货 → 退款
```

## 9. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 检查请求参数 |
| 1002 | 签名错误 | 检查签名算法 |
| 1003 | token无效 | 刷新token |
| 1004 | 权限不足 | 检查应用权限 |
| 1005 | 限流 | 指数退避重试 |
| 1006 | 服务忙 | 等待后重试 |
| 2001 | 订单不存在 | 返回空 |
| 3001 | 库存不足 | 标记并告警 |

## 10. 监控告警

| 监控项 | 阈值 | 告警方式 |
|--------|------|----------|
| API成功率 | <99% | 短信/邮件 |
| 同步延迟 | >10分钟 | 邮件 |
| 限流触发次数 | >10次/小时 | 邮件 |
| token刷新失败 | >3次 | 短信 |
