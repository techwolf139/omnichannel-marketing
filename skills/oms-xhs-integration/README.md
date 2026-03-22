# 小红书开放平台集成适配器

小红书（Xiaohongshu）开放平台对接模块，支持笔记曝光数据、KOL合作管理、薯店订单同步、小程序订单同步。

## 功能特性

- **笔记数据**: 笔记曝光/互动数据查询，效果评估
- **KOL合作**: 蒲公英平台合作订单管理，投放效果追踪
- **薯店订单**: 薯店电商订单同步，状态映射
- **小程序订单**: 微信小程序订单同步，UTM归因
- **归因计算**: 基于UTM参数的30天归因窗口，权重0.15

## 目录结构

```
oms-xhs-integration/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── auth.py           # OAuth 2.0 认证
│   ├── client.py         # API客户端
│   ├── note_adapter.py   # 笔记数据适配器
│   ├── kol_adapter.py    # KOL适配器
│   └── order_adapter.py  # 订单适配器
└── tests/
    ├── __init__.py
    └── test_*.py          # 单元测试
```

## 快速开始

### 1. 配置认证信息

```python
from scripts.auth import XHSAuth

auth = XHSAuth(
    app_id="your_app_id",
    app_secret="your_app_secret",
    use_sandbox=True  # 生产环境设为False
)
auth.get_access_token("your_oauth_code")
```

### 2. 初始化客户端

```python
from scripts.client import XHSClient

client = XHSClient(auth)
```

### 3. 查询笔记曝光

```python
from scripts.note_adapter import XHSNoteAdapter

adapter = XHSNoteAdapter()
raw_data = client.note_exposure_get("note_xxx")
exposure = adapter.to_standard_exposure(raw_data)
```

### 4. 同步薯店订单

```python
from scripts.order_adapter import XHSOrderAdapter

adapter = XHSOrderAdapter()
orders = client.shu_dian_order_search(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
standard_orders = [
    adapter.to_standard_order(order, "SHU_DIAN") 
    for order in orders.get("order_list", [])
]
```

### 5. UTM归因计算

```python
# 订单归因 = 订单金额 × 归因权重(0.15)
for order in standard_orders:
    attributed_value = order["total_amount"] * order["attribution_weight"]
    print(f"订单{order['platform_order_id']}归因值: {attributed_value}")
```

## 环境变量

| 变量 | 说明 |
|------|------|
| XHS_APP_ID | 小红书应用ID |
| XHS_APP_SECRET | 小红书应用密钥 |
| XHS_ACCESS_TOKEN | 访问令牌 |
| XHS_REFRESH_TOKEN | 刷新令牌 |

## API限流

| 接口类型 | 限流 |
|---------|------|
| 笔记数据API | 200次/分钟 |
| KOL/蒲公英API | 100次/分钟 |
| 订单API | 200次/分钟 |

## OMS集成

| OMS技能 | 集成方式 |
|---------|----------|
| oms-one-id-merge | 用户身份归一（手机号/OpenID） |
| oms-promotion-engine | 归因后发券/积分触发 |
| oms-order-capture | 订单统一汇聚 |
| oms-profit-sharing | 归因分润计算 |

## 测试

```bash
cd skills/oms-xhs-integration
python -m pytest tests/ -v
```
