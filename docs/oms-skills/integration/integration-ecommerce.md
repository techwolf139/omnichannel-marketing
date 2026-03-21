# 商品销售系统对接规范

本文档定义 OMS 系统与主流电商平台的对接规范，涵盖订单获取、商品同步、库存同步、退货处理等核心功能。

## 1. 平台概览

| 平台 | 平台代码 | API规范 | 订单特点 | 隐私面单 |
|------|----------|---------|----------|----------|
| 天猫/淘宝 | TMALL | 阿里开放平台 | 订单量大、退货率高 | 需要解密 |
| 京东 | JD | JD API | POP模式为主 | 部分加密 |
| 拼多多 | PDD | 拼多多开放平台 | 社交订单、团购多 | 需要手机号绑定 |
| 抖音电商 | DOUYIN | 抖音电商API | 直播订单高并发 | 需要解密 |
| 快手电商 | KUAISHOU | 快手开放平台 | 直播为主 | 需要解密 |

## 2. 订单获取对接

### 2.1 接入模式

| 模式 | 说明 | 适用场景 | 延迟 |
|------|------|----------|------|
| API拉取 | 定时调用平台API获取订单 | 日常订单同步 | 5-30分钟 |
| Webhook推送 | 平台主动推送订单事件 | 高时效要求场景 | <1秒 |
| 混合模式 | 两者结合，Webhook为主 | 核心业务（推荐） | <1秒 |

### 2.2 订单标准化映射

```
平台原始订单 → OMS标准订单模型

TMALL订单字段映射:
  tid → source_order_id
  buyer_nick → customer.nickname (脱敏)
  receiver_name → shipping.receiver_name (解密后)
  receiver_mobile → shipping.phone (解密后)
  orders.title → items[].sku_name
  orders.num_iid → items[].sku_id (需映射到内部SKU)
  payment → amounts.order_amount
```

### 2.3 平台特定处理

#### 天猫/淘宝

```python
# 隐私面单解密
TmallPrivacyAPI.decrypt(logistics_no, phone_no) → {receiver_name, address, phone}

# 订单状态映射
taobao_trade_status → OMS_order_status:
  "TRADE_NO_CREATE_PAY" → CREATED
  "WAIT_BUYER_PAY" → CREATED
  "WAIT_SELLER_SEND_GOODS" → PAID
  "SELLER_CONSIGNED_PART" → PICKING
  "TRADE_BUYER_SIGNED" → DELIVERED
```

#### 京东

```python
# 京东订单状态映射
jd_order_state → OMS_order_status:
  1 → CREATED      # 待支付
  2 → PAID         # 已支付
  3 → ALLOCATED    # 配货中
  4 → PICKING      # 打包中
  5 → SHIPPED      # 已发货
  6 → DELIVERED    # 妥投
  7 → CANCELLED    # 取消
```

#### 抖音电商

```python
# 抖音订单特性处理
DOUYIN_order:
  - 高并发场景：需要防超卖机制
  - 直播订单：需要关联直播间ID
  - 预售订单：需要处理发货时间预告
```

## 3. 商品同步对接

### 3.1 同步内容

| 同步项 | 说明 | 同步频率 |
|--------|------|----------|
| 商品基本信息 | SKU编码、名称、规格 | 每日全量 |
| 价格信息 | 售价、优惠价、会员价 | 每小时增量 |
| 库存信息 | 各渠道可售库存 | 实时 |
| 上下架状态 | 商品在平台的上架状态 | 实时 |

### 3.2 SKU映射规则

```
OMS内部SKU ← 平台SKU映射表 ← 平台商品

映射层级:
  OMS_SKU
    ├── TMALL_SKU (item_id, sku_id)
    ├── JD_SKU (sku_id)
    ├── PDD_SKU (goods_id, sku_id)
    └── DOUYIN_SKU (product_id, sku_id)
```

## 4. 库存同步对接

### 4.1 同步方向

```
OMS库存中心 → 平台可售库存

同步策略:
  1. OMS计算渠道可售库存
  2. 调用平台API更新库存
  3. 平台返回确认
  4. 记录同步日志
```

### 4.2 平台库存回写

| 平台 | API | 限流 | 备注 |
|------|-----|------|------|
| 天猫 | taobao.inventory.occupy.apply | 1000/分钟 | 需要申请权限 |
| 京东 | jd.ware.inventory.securable.update | 500/分钟 | |
| 拼多多 | pdd.goods.inventory.update | 300/分钟 | |
| 抖音 | goods/stock_update | 1000/分钟 | |

## 5. 退货处理对接

### 5.1 逆向流程

```
OMS退货申请 → 平台退货API → 平台审核 → 退货物流 → 退款

各平台退货API:
  天猫: taobao.refund.list.get / taobao.logistics.red.return.create
  京东: jd.returnorder.apply / jd.returnorder.vendor.process
  拼多多: pdd.refund.list.get / pdd.logistics.online.create
  抖音: aftersale.list / aftersale.create
```

### 5.2 退货状态回传

```
OMS退货状态 → 平台退货状态

状态映射:
  RETURN_REQUEST → 买家申请退款
  RETURN_SHIPPED → 买家已退货
  RECEIVED → 平台已收货
  REFUNDED → 退款完成
```

## 6. 错误处理与重试

### 6.1 错误分类

| 错误类型 | 处理策略 | 重试次数 |
|----------|----------|----------|
| 网络超时 | 指数退避重试 | 3次 |
| API限流 | 等待后重试 | 5次 |
| 授权失效 | 刷新Token | 1次 |
| 数据异常 | 人工处理 | 0次 |

### 6.2 降级策略

```
正常 → API限流降级 → 拉取间隔增大
                → 推送优先，拉取兜底
```

## 7. 安全规范

| 安全项 | 要求 |
|--------|------|
| 授权Token | 加密存储，定期轮换 |
| 敏感数据 | 不得明文日志记录 |
| 隐私面单 | 仅用于履约必要操作 |
| IP白名单 | 平台API调用必须白名单 |
