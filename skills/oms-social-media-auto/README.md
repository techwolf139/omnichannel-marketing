# 全平台社交媒体分发适配器

多平台社交媒体内容分发模块，支持知乎、微博、小红书、Twitter一键发布。通过统一内容模型自动适配各平台格式要求，实现内容跨平台同步与多账号管理。

## 功能特性

- **全平台分发**: 一键将内容发布到知乎、微博、小红书、Twitter
- **内容转换**: 自动适配各平台格式要求（长度限制、话题格式等）
- **多账号管理**: 支持多账号配置和切换
- **定时发布**: 支持定时/延迟发布
- **发布追踪**: 统一追踪各平台发布状态和链接
- **批量操作**: 支持批量删除和更新

## 目录结构

```
oms-social-media-auto/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── dispatcher.py     # 分发调度器
│   ├── transformer.py    # 内容转换器
│   └── platforms/
│       ├── __init__.py
│       ├── zhihu.py      # 知乎适配器
│       ├── weibo.py      # 微博适配器
│       ├── xhs.py        # 小红书适配器
│       └── twitter.py    # Twitter适配器
└── tests/
    ├── __init__.py
    └── test_*.py         # 单元测试
```

## 快速开始

### 1. 配置平台认证

```python
from scripts.platforms.zhihu import ZhihuAdapter
from scripts.platforms.weibo import WeiboAdapter
from scripts.platforms.xhs import XHSAdapter
from scripts.platforms.twitter import TwitterAdapter

# 初始化各平台适配器
zhihu = ZhihuAdapter(access_token="your_zhihu_token")
weibo = WeiboAdapter(access_token="your_weibo_token")
xhs = XHSAdapter(access_token="your_xhs_token")
twitter = TwitterAdapter(
    api_key="your_api_key",
    api_secret="your_api_secret",
    access_token="your_access_token"
)
```

### 2. 初始化分发器

```python
from scripts.dispatcher import SocialDispatcher

dispatcher = SocialDispatcher(
    platform_clients={
        "zhihu": zhihu,
        "weibo": weibo,
        "xhs": xhs,
        "twitter": twitter
    }
)
```

### 3. 创建内容并分发

```python
content = {
    "content_id": "content_001",
    "title": "全平台发布测试",
    "body": "这是一条测试内容，将自动适配各平台格式。",
    "media": ["/path/to/image.jpg"],
    "topics": ["测试", "社交媒体"]
}

# 分发到指定平台
results = dispatcher.dispatch(content, ["zhihu", "weibo", "xhs"])

# 或分发到所有平台
results = dispatcher.dispatch_all(content)
```

### 4. 处理发布结果

```python
for platform, result in results.items():
    if result["status"] == "success":
        print(f"{platform}: 发布成功 - {result['content_id']}")
    else:
        print(f"{platform}: 发布失败 - {result.get('error', 'Unknown error')}")
```

## 环境变量

| 变量 | 说明 |
|------|------|
| ZHIHU_ACCESS_TOKEN | 知乎访问令牌 |
| WEIBO_ACCESS_TOKEN | 微博访问令牌 |
| XHS_ACCESS_TOKEN | 小红书访问令牌 |
| TWITTER_API_KEY | Twitter API Key |
| TWITTER_API_SECRET | Twitter API Secret |
| TWITTER_ACCESS_TOKEN | Twitter Access Token |

## API限流

| 平台 | 限流 |
|------|------|
| 知乎 | 100次/分钟 |
| 微博 | 200次/小时 |
| 小红书 | 200次/分钟 |
| Twitter | 300次/15分钟 |

## OMS集成

| OMS技能 | 集成方式 |
|---------|----------|
| oms-xhs-integration | 小红书订单归因后自动发笔记 |
| oms-promotion-engine | 营销活动自动发布 |
| oms-one-id-merge | 多平台账号归一 |

## 测试

```bash
cd skills/oms-social-media-auto
python -m pytest tests/ -v
```
