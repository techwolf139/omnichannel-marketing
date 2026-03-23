# oms-content-creator

爆款文案生成引擎 - 为OMS营销场景提供智能内容创作能力。

## 功能特性

- **标题生成**: 基于主题自动生成多风格爆款标题
- **正文创作**: 撰写产品/活动推广文案
- **脚本生成**: 创作短视频口播脚本
- **平台改写**: 一键适配微信、小红书、知乎、微博等平台风格
- **热点匹配**: 自动匹配热门话题提升内容曝光

## 安装

```bash
# 复制到项目目录
cp -r skills/oms-content-creator /path/to/your/project/
```

## 快速开始

```python
from scripts.generator import ContentGenerator
from scripts.rewriter import ContentRewriter
from scripts.trending import TrendingMatcher

# 生成标题
generator = ContentGenerator()
titles = generator.generate_title("护肤精华", style="viral")
print(titles)
# ['护肤精华的10个惊人秘密', '关于护肤精华你不知道的事']

# 改写为小红书风格
rewriter = ContentRewriter()
xhs_content = rewriter.rewrite_for_platform(original_content, "xiaohongshu")

# 匹配热门话题
matcher = TrendingMatcher()
topics = matcher.match_trending_topics(content)
```

## API 文档

### ContentGenerator

#### `generate_title(topic: str, style: str = "viral") -> list[str]`

生成标题列表。

**参数:**
- `topic`: 主题关键词
- `style`: 风格类型 (viral|question|list|story|benefit)

**返回:** 标题字符串列表

#### `generate_body(topic: str, format: str, style: str) -> str`

生成正文内容。

**参数:**
- `topic`: 主题
- `format`: 格式类型 (product|activity|story)
- `style`: 风格

**返回:** Markdown格式内容

#### `generate_script(topic: str, duration: int, style: str) -> dict`

生成短视频脚本。

**参数:**
- `topic`: 视频主题
- `duration`: 时长(秒)
- `style`: 风格

**返回:** 包含scenes、narration、duration的JSON

### ContentRewriter

#### `rewrite_for_platform(content: str, platform: str) -> str`

将内容改写为指定平台风格。

**支持平台:**
- `wechat`: 微信公众号
- `xiaohongshu`: 小红书
- `zhihu`: 知乎
- `weibo`: 微博
- `twitter`: Twitter/X

### TrendingMatcher

#### `match_trending_topics(content: str) -> list[dict]`

匹配与内容相关的热门话题。

#### `fetch_platform_trending(platform: str, category: str) -> list[dict]`

获取平台热门话题列表。

## 目录结构

```
oms-content-creator/
├── SKILL.md              # OpenCode Skill定义
├── README.md             # 本文档
├── design.md             # 详细设计文档
└── scripts/
    ├── __init__.py
    ├── generator.py      # 内容生成器
    ├── trending.py       # 热点匹配器
    ├── rewriter.py       # 内容改写器
    └── tests/            # 测试用例
        ├── test_generator.py
        ├── test_rewriter.py
        └── test_trending.py
```

## 测试

```bash
cd skills/oms-content-creator
python -m pytest scripts/tests/ -v
```

## 许可证

MIT
