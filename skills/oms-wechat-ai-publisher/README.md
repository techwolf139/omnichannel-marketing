# 微信公众号AI发布适配器

微信公众号内容发布模块，支持文章草稿管理、AI封面生成、内容排版、定时发布。

## 功能特性

- **草稿管理**: 创建、更新、删除公众号文章草稿
- **封面生成**: AI自动生成文章封面图
- **内容排版**: Markdown转微信公众号图文格式
- **定时发布**: 支持定时发布文章
- **多主题支持**: default、minimal、modern三种排版风格

## 目录结构

```
oms-wechat-ai-publisher/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── auth.py           # 认证模块
│   ├── client.py         # API客户端
│   ├── cover_generator.py # 封面生成器
│   └── formatter.py      # 内容排版器
└── tests/
    ├── __init__.py
    └── test_*.py         # 单元测试
```

## 快速开始

### 1. 配置认证信息

```python
from scripts.auth import WeChatAuth

auth = WeChatAuth(
    app_id="your_app_id",
    app_secret="your_app_secret"
)
token = auth.get_access_token()
```

### 2. 初始化客户端

```python
from scripts.client import WeChatClient

client = WeChatClient(auth)
```

### 3. 创建草稿

```python
# 创建草稿
draft_id = client.create_draft(
    title="文章标题",
    body="<p>文章内容</p>",
    cover_url="https://example.com/cover.jpg"
)
```

### 4. 生成封面

```python
from scripts.cover_generator import CoverGenerator

generator = CoverGenerator()
cover_url = generator.generate_cover(
    topic="AI技术发展趋势",
    style="modern"
)
```

### 5. 内容排版

```python
from scripts.formatter import ContentFormatter

formatter = ContentFormatter()
html_content = formatter.format_content(
    markdown="# 标题\n\n正文内容",
    theme="minimal"
)
```

## 环境变量

| 变量 | 说明 |
|------|------|
| WECHAT_APP_ID | 微信公众号AppID |
| WECHAT_APP_SECRET | 微信公众号AppSecret |
| WECHAT_ACCESS_TOKEN | 访问令牌（可选，自动生成） |

## API限流

| API类型 | 限流 |
|---------|------|
| 草稿操作 | 1000次/天 |
| 发布文章 | 100次/天 |
| 素材上传 | 5000次/天 |

## 错误处理

```python
try:
    result = client.create_draft(...)
except WeChatAPIError as e:
    if e.code == 40001:  # access_token过期
        auth.refresh_access_token()
        result = client.create_draft(...)
    elif e.code == 45009:  # 接口调用超过频率限制
        time.sleep(60)  # 等待后重试
```

## 测试

```bash
cd skills/oms-wechat-ai-publisher
python -m pytest tests/ -v
```
