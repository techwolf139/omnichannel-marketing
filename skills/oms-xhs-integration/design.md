# 小红书开放平台集成 - 详细设计

## 1. API 接入

### 1.1 环境配置

| 环境 | Host | 说明 |
|------|------|------|
| 测试环境 | `http://flssandbox.xiaohongshu.com` | 沙箱环境，可自由调用 |
| 正式环境 | `https://ark.xiaohongshu.com` | 需审核权限 |

### 1.2 认证流程

OAuth 2.0 授权码流程：

1. 引导用户至授权页 `https://open.xiaohongshu.com`
2. 用户授权后获取 code（有效期10分钟）
3. 用 code 换取 accessToken
4. 定期刷新 accessToken（有效期2小时）

签名算法：MD5签名，规则为 `md5(app_secret + key1 + value1 + key2 + value2 + ... + app_secret)`，key按字典序排列。

### 1.3 API 限流

| 接口类型 | 默认限流 | 说明 |
|----------|----------|------|
| 公共API | 200次/分钟 | token刷新等 |
| 笔记数据API | 200次/分钟 | 曝光/互动数据 |
| KOL/蒲公英API | 100次/分钟 | 合作订单 |
| 订单API | 200次/分钟 | 薯店/小程序订单 |

## 2. 数据模型

### 2.1 XHSNoteExposure

| 字段 | 类型 | 说明 |
|------|------|------|
| note_id | str | 笔记唯一ID |
| title | str | 笔记标题 |
| exposure_count | int | 曝光次数 |
| like_count | int | 点赞数 |
| collect_count | int | 收藏数 |
| comment_count | int | 评论数 |
| share_count | int | 分享数 |
| publish_time | datetime | 发布时间 |

### 2.2 XHSKOLOrder

| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | str | 合作单ID |
| kol_name | str | KOL昵称 |
| kol_id | str | KOL ID |
| content_type | str | 内容形式: 图文/视频 |
| price | decimal | 合作价格 |
| status | str | 状态: pending/ongoing/completed/cancelled |
| publish_time | datetime | 发布预期时间 |

### 2.3 XHSOrder

| 字段 | 类型 | 说明 |
|------|------|------|
| xhs_order_id | str | 订单ID |
| order_type | str | SHU_DIAN / MINI_PROGRAM |
| order_state | int | 状态码 1-5 |
| buyer_nickname | str | 买家昵称 |
| receiver_name | str | 收货人姓名 |
| receiver_mobile | str | 收货人电话 |
| address_detail | str | 详细地址 |
| item_list | list | 商品列表 |
| total_amount | decimal | 订单总金额 |
| freight_amount | decimal | 运费 |
| pay_time | datetime | 支付时间 |
| ship_time | datetime | 发货时间 |

## 3. UTM 归因流程

### 3.1 归因链路

```
小红书笔记曝光/互动
    ↓ (带UTM参数)
落地页/小程序访问
    ↓ (openid/手机号)
One-ID 归一
    ↓
购买行为记录
    ↓
归因计算（30天窗口）
    ↓
分润记录 → profit_sharing
```

### 3.2 归因权重

| 触点 | 权重 |
|------|------|
| 小红书种草 (XHS_CONTENT) | 0.15 |

## 4. 模块设计

### 4.1 auth.py

OAuth 2.0 + MD5签名，负责token获取和刷新。

### 4.2 client.py

统一API客户端，所有endpoint入口，含限流处理。

### 4.3 note_adapter.py

笔记数据转换: XHS API → OMS标准格式，含互动率计算。

### 4.4 kol_adapter.py

KOL合作数据转换: 蒲公英API → OMS标准格式，含CPE/CPI计算。

### 4.5 order_adapter.py

订单转换: 薯店/小程序API → OMS标准订单格式，含状态映射。

## 5. OMS 集成点

| OMS技能 | 集成方式 |
|---------|----------|
| oms-one-id-merge | 用户身份归一（手机号/OpenID） |
| oms-promotion-engine | 归因后发券/积分触发 |
| oms-order-capture | 订单统一汇聚 |
| oms-profit-sharing | 归因分润计算 |

## 6. 错误处理

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 检查请求参数 |
| 1003 | token无效 | 刷新token |
| 1005 | 限流 | 等待后重试（指数退避） |
| 2001 | 权限不足 | 申请API权限 |
| 5000 | 系统错误 | 联系小红书技术支持 |

## 7. MVP 暂不实现

| 功能 | 原因 |
|------|------|
| 库存同步 | MVP阶段薯店/小程序库存由平台管理 |
| 物流追踪 | 小红书物流API暂不开放 |
| 退货退款 | 需对接售后API，MVP先不做 |
| 聚光广告投放 | 需商务合作，可后续迭代 |
| Webhook实时推送 | MVP先用轮询 |
