# 京东开放平台对接设计方案

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现OMS系统与京东开放平台的全对接，支持订单获取、库存同步、物流追踪、退货处理等核心功能。

**Architecture:** 采用适配器模式，为京东平台创建独立的adapter层，将京东API响应转换为OMS标准模型。通过统一的消息队列处理订单事件，实现与现有skill的数据流通。

**Tech Stack:** Python 3.10+, requests库, Redis队列, MySQL

---

## 一、京东开放平台概述

### 1.1 平台特点

| 特点 | 说明 |
|------|------|
| 接入模式 | POP模式（京东开放平台）为主，部分自营 |
| 订单特点 | POP订单为主，物流履约由商家负责 |
| 隐私面单 | 部分加密，需申请解密权限 |
| API限流 | 500次/分钟（库存类），1000次/分钟（订单类） |

### 1.2 API规范

| 项目 | 规范 |
|------|------|
| 协议 | HTTPS RESTful API |
| 认证 | OAuth 2.0 (app_key + app_secret + access_token) |
| 签名 | MD5/SHA256签名验证 |
| 格式 | JSON |
| 编码 | UTF-8 |

---

## 二、京东API分类

### 2.1 订单类API

| API名称 | 方法 | 说明 | 限流 |
|---------|------|------|------|
| `jd.order.search` | POST | 订单搜索/查询 | 1000/分钟 |
| `jd.order.detail.get` | POST | 订单详情 | 1000/分钟 |
| `jd.order.track.search` | POST | 订单轨迹 | 500/分钟 |
| `jd.order.state` | POST | 订单状态更新 | 500/分钟 |

### 2.2 商品类API

| API名称 | 方法 | 说明 | 限流 |
|---------|------|------|------|
| `jd.product.ware.list` | POST | 商品列表 | 500/分钟 |
| `jd.product.ware.get` | POST | 商品详情 | 500/分钟 |
| `jd.product.sku.list` | POST | SKU列表 | 500/分钟 |
| `jd.product.sku.get` | POST | SKU详情 | 500/分钟 |

### 2.3 库存类API

| API名称 | 方法 | 说明 | 限流 |
|---------|------|------|------|
| `jd.ware.inventory.securable.update` | POST | 库存更新 | 500/分钟 |
| `jd.ware.inventory.remain.get` | POST | 库存查询 | 500/分钟 |

### 2.4 物流类API

| API名称 | 方法 | 说明 | 限流 |
|---------|------|------|------|
| `jd.delivery.order.create` | POST | 创建配送单 | 500/分钟 |
| `jd.delivery.order.search` | POST | 配送单查询 | 500/分钟 |
| `jd.logistics.order.search` | POST | 物流轨迹查询 | 500/分钟 |

### 2.5 退货退款API

| API名称 | 方法 | 说明 | 限流 |
|---------|------|------|------|
| `jd.returnorder.apply` | POST | 退货申请 | 500/分钟 |
| `jd.returnorder.vendor.process` | POST | 退货审核 | 500/分钟 |
| `jd.refund.order.info` | POST | 退款查询 | 500/分钟 |

---

## 三、认证与授权

### 3.1 授权流程

```
1. 商家在京东开放平台注册应用获取 app_key, app_secret
2. 通过 Authorization Code 模式获取 access_token
3. 调用API时携带 access_token
4. token过期时使用 refresh_token 刷新
```

### 3.2 认证配置

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

---

## 四、订单对接

### 4.1 订单状态映射

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

### 4.2 订单字段映射

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
'''

### 4.3 订单同步策略

| 同步方式 | 说明 | 延迟 |
|----------|------|------|
| 增量拉取 | 每5分钟拉取增量订单 | 5-10分钟 |
| 全量拉取 | 每日凌晨全量同步 | T+1 |
| Webhook推送 | 订单状态变更实时推送 | <1秒 |

---

## 五、库存对接

### 5.1 库存同步方向

```
OMS库存中心 → 京东可售库存

同步策略:
  1. OMS计算渠道可售库存 = Σ(各仓可售) - 渠道预占 - 渠道隔离
  2. 调用 jd.ware.inventory.securable.update 更新库存
  3. 记录同步日志
```

### 5.2 库存字段映射

```
OMS库存 → JD库存

sku_id → sku_id (SKU编号)
available_quantity → stock_num (可售库存)
locked_quantity → lock_stock_num (锁定库存)
```

---

## 六、物流对接

### 6.1 物流状态映射

| JD物流状态 | OMS状态 | 说明 |
|------------|---------|------|
| ARRANGE | SHIPPED | 已发货 |
| DELIVERING | IN_TRANSIT | 配送中 |
| SIGN | DELIVERED | 已签收 |

### 6.2 运单字段映射

```
JD运单 → OMS物流

express_no → tracking_number (运单号)
express_name → carrier_name (承运商)
state → logistics_status (物流状态)
delivery_time → shipped_at (发货时间)
sign_time → delivered_at (签收时间)
'''

---

## 七、退货退款对接

### 7.1 退货状态映射

| OMS状态 | JD状态 | 说明 |
|---------|--------|------|
| RETURN_REQUEST | APPLIED | 买家申请退货 |
| RETURN_APPROVED | APPROVED | 审核通过 |
| RETURN_SHIPPED | SHIPPED | 买家已退货 |
| RETURN_RECEIVED | RECEIVED | 京东收货 |
| REFUNDED | REFUNDED | 退款完成 |

### 7.2 退货流程

```
OMS退货申请 → jd.returnorder.apply → 京东审核 → 买家退货 → 京东收货 → 退款
```

---

## 八、项目结构

```
docs/plans/2026-03-22-jd-integration.md  # 本设计文档

skills/oms-jd-integration/               # 京东集成适配器
├── SKILL.md                            # Skill定义
├── README.md                           # 使用说明
├── design.md                           # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── auth.py                         # 认证模块
│   ├── client.py                       # API客户端
│   ├── order_adapter.py                # 订单适配器
│   ├── inventory_adapter.py            # 库存适配器
│   ├── logistics_adapter.py            # 物流适配器
│   ├── return_adapter.py               # 退货适配器
│   └── webhook_handler.py              # Webhook处理
└── tests/
    ├── test_auth.py
    ├── test_order.py
    └── test_integration.py
```

---

## 九、实现任务

### Task 1: 创建JD集成适配器目录结构

**Files:**
- Create: `skills/oms-jd-integration/SKILL.md`
- Create: `skills/oms-jd-integration/README.md`
- Create: `skills/oms-jd-integration/design.md`
- Create: `skills/oms-jd-integration/scripts/__init__.py`
- Create: `skills/oms-jd-integration/tests/__init__.py`

### Task 2: 实现认证模块

**Files:**
- Create: `skills/oms-jd-integration/scripts/auth.py`

**Step 1: 编写认证测试**

```python
def test_token_refresh():
    auth = JDAuth(app_key="test_key", app_secret="test_secret")
    result = auth.get_access_token()
    assert result.get("code") == 0
    assert "access_token" in result
```

**Step 2: 运行测试验证失败**

Run: `pytest skills/oms-jd-integration/tests/test_auth.py::test_token_refresh -v`
Expected: FAIL - module not found

**Step 3: 实现认证模块**

```python
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta

class JDAuth:
    def __init__(self, app_key: str, app_secret: str, 
                 access_token: str = "", refresh_token: str = "",
                 token_expires_at: str = ""):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.server_url = "https://api.jd.com/routerjson"
    
    def is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return True
        expires = datetime.strptime(self.token_expires_at, "%Y-%m-%dT%H:%M:%SZ")
        return datetime.utcnow() >= expires - timedelta(minutes=10)
    
    def get_access_token(self) -> Dict:
        # 实现token获取逻辑
        pass
```

**Step 4: 运行测试验证通过**

Run: `pytest skills/oms-jd-integration/tests/test_auth.py -v`
Expected: PASS

### Task 3: 实现API客户端

**Files:**
- Create: `skills/oms-jd-integration/scripts/client.py`

**Step 1: 编写客户端测试**

```python
def test_order_search():
    client = JDClient(auth=auth)
    result = client.order_search(page=1, page_size=100)
    assert result.get("code") == 0
```

**Step 2: 运行测试验证失败**

Run: `pytest skills/oms-jd-integration/tests/test_client.py::test_order_search -v`
Expected: FAIL

**Step 3: 实现API客户端**

```python
import hashlib
import time
from typing import Dict, Any

class JDClient:
    def __init__(self, auth: JDAuth):
        self.auth = auth
        self.server_url = "https://api.jd.com/routerjson"
    
    def order_search(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        params = {
            "method": "jd.order.search",
            "page": page,
            "page_size": page_size,
            "access_token": self.auth.access_token,
            "app_key": self.auth.app_key,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "v": "2.0",
            "sign_method": "md5"
        }
        # 签名逻辑
        params["sign"] = self._generate_sign(params)
        # 发送请求
        response = requests.post(self.server_url, data=params, timeout=30)
        return response.json()
```

**Step 4: 运行测试验证通过**

Run: `pytest skills/oms-jd-integration/tests/test_client.py -v`
Expected: PASS

### Task 4: 实现订单适配器

**Files:**
- Create: `skills/oms-jd-integration/scripts/order_adapter.py`

**Step 1: 编写订单适配器测试**

```python
def test_jd_order_to_standard():
    adapter = OrderAdapter()
    jd_order = {...}  # JD订单格式
    standard = adapter.to_standard_order(jd_order)
    assert standard["source_channel"] == "JD"
    assert "order_id" in standard
```

**Step 2: 运行测试验证失败**

Run: `pytest skills/oms-jd-integration/tests/test_order.py::test_jd_order_to_standard -v`
Expected: FAIL

**Step 3: 实现订单适配器**

```python
class OrderAdapter:
    # JD订单状态 → OMS状态映射
    STATUS_MAP = {
        1: "CREATED",    # 待支付
        2: "PAID",       # 已支付
        3: "ALLOCATED",  # 配货中
        4: "PICKING",    # 打包中
        5: "SHIPPED",    # 已发货
        6: "DELIVERED",  # 妥投
        7: "CANCELLED",  # 取消
        99: "CANCELLED"  # 无效
    }
    
    def to_standard_order(self, jd_order: dict) -> dict:
        return {
            "order_id": jd_order.get("order_id"),
            "source_order_id": str(jd_order.get("jd_order_id", "")),
            "source_channel": "JD",
            "customer": {
                "one_id": jd_order.get("customer_id", ""),
                "phone": self._mask_phone(jd_order.get("consignee_mobile", "")),
            },
            "items": self._parse_items(jd_order.get("item_info_list", [])),
            "amounts": {
                "goods_amount": float(jd_order.get("order_payment", 0)),
                "shipping_fee": float(jd_order.get("freight_price", 0)),
                "discount_amount": float(jd_order.get("coupon_payment", 0)),
                "order_amount": float(jd_order.get("order_payment", 0))
            },
            "shipping": {
                "receiver_name": jd_order.get("consignee_name", ""),
                "phone": jd_order.get("consignee_mobile", ""),
                "address": jd_order.get("address_detail", "")
            },
            "status": self.STATUS_MAP.get(jd_order.get("order_state", 0), "UNKNOWN"),
            "created_at": jd_order.get("order_start_time", "")
        }
```

**Step 4: 运行测试验证通过**

Run: `pytest skills/oms-jd-integration/tests/test_order.py -v`
Expected: PASS

### Task 5: 实现库存适配器

**Files:**
- Create: `skills/oms-jd-integration/scripts/inventory_adapter.py`

### Task 6: 实现物流适配器

**Files:**
- Create: `skills/oms-jd-integration/scripts/logistics_adapter.py`

### Task 7: 实现退货适配器

**Files:**
- Create: `skills/oms-jd-integration/scripts/return_adapter.py`

### Task 8: 实现Webhook处理器

**Files:**
- Create: `skills/oms-jd-integration/scripts/webhook_handler.py`

### Task 9: 更新integration_helper.py

**Files:**
- Modify: `skills/integration_helper.py:20-31`

### Task 10: 编写集成测试

**Files:**
- Create: `skills/oms-jd-integration/tests/test_integration.py`

---

## 十、部署配置

### 10.1 环境变量

```bash
JD_APP_KEY=your_app_key
JD_APP_SECRET=your_app_secret
JD_ACCESS_TOKEN=your_access_token
JD_REFRESH_TOKEN=your_refresh_token
JD_SERVER_URL=https://api.jd.com/routerjson
```

### 10.2 IP白名单

京东API调用需要将服务器IP加入白名单，在京东开放平台设置。

---

## 十一、错误处理

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

---

## 十二、监控告警

| 监控项 | 阈值 | 告警方式 |
|--------|------|----------|
| API成功率 | <99% | 短信/邮件 |
| 同步延迟 | >10分钟 | 邮件 |
| 限流触发次数 | >10次/小时 | 邮件 |
| token刷新失败 | >3次 | 短信 |
