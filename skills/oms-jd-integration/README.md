# 京东开放平台集成适配器

京东（JD.com）开放平台对接模块，支持订单同步、库存管理、物流追踪、退货处理。

## 功能特性

- **订单同步**: 支持京东POP订单拉取、状态同步、订单详情查询
- **库存管理**: 京东可售库存同步、库存预占与释放
- **物流追踪**: 京东运单轨迹查询、物流状态更新
- **退货处理**: 京东退货申请、退款查询、退货状态同步

## 目录结构

```
oms-jd-integration/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── auth.py           # 认证模块
│   ├── client.py         # API客户端
│   ├── order_adapter.py  # 订单适配器
│   ├── inventory_adapter.py  # 库存适配器
│   ├── logistics_adapter.py  # 物流适配器
│   └── return_adapter.py # 退货适配器
└── tests/
    ├── __init__.py
    └── test_*.py         # 单元测试
```

## 快速开始

### 1. 配置认证信息

```python
from scripts.auth import JDAuth

auth = JDAuth(
    app_key="your_app_key",
    app_secret="your_app_secret"
)
auth.get_access_token()
```

### 2. 初始化客户端

```python
from scripts.client import JDClient

client = JDClient(auth)
```

### 3. 查询订单

```python
# 搜索订单
result = client.order_search(
    start_date="2024-01-01",
    end_date="2024-01-31",
    page=1,
    page_size=100
)

# 获取订单详情
detail = client.order_detail_get(jd_order_id="JD123456789")
```

### 4. 同步库存

```python
from scripts.inventory_adapter import InventoryAdapter

adapter = InventoryAdapter(client)
adapter.sync_inventory(sku_id="SKU001", quantity=100)
```

## 环境变量

| 变量 | 说明 |
|------|------|
| JD_APP_KEY | 京东应用Key |
| JD_APP_SECRET | 京东应用密钥 |
| JD_ACCESS_TOKEN | 访问令牌 |
| JD_REFRESH_TOKEN | 刷新令牌 |

## API限流

| API类型 | 限流 |
|---------|------|
| 订单类 | 1000次/分钟 |
| 库存类 | 500次/分钟 |
| 物流类 | 500次/分钟 |

## 错误处理

```python
try:
    result = client.order_search(...)
except JDAPIError as e:
    if e.code == 1003:  # token无效
        auth.refresh_token()
        result = client.order_search(...)
    elif e.code == 1005:  # 限流
        time.sleep(60)  # 等待后重试
```

## 测试

```bash
cd skills/oms-jd-integration
python -m pytest tests/ -v
```
