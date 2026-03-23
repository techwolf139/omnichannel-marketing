# 小红书自动化工具集

小红书（Xiaohongshu）内容运营自动化模块，支持热点话题采集、笔记自动发布、数据统计分析。

## 功能特性

- **热点采集**: 实时获取小红书热门话题，支持分类筛选
- **笔记发布**: 批量创建图文笔记，支持定时发布
- **数据统计**: 获取笔记曝光、点赞、收藏、评论等数据

## 目录结构

```
oms-xiaohongshu-automation/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── trending_fetcher.py   # 热点话题采集器
│   ├── note_publisher.py     # 笔记发布器
│   └── stats_fetcher.py      # 数据统计器
└── tests/
    ├── __init__.py
    └── test_*.py              # 单元测试
```

## 快速开始

### 1. 配置环境变量

```bash
export XHS_APP_ID="your_app_id"
export XHS_APP_SECRET="your_app_secret"
export XHS_ACCESS_TOKEN="your_access_token"
```

### 2. 热点话题采集

```python
from scripts.trending_fetcher import TrendingFetcher

fetcher = TrendingFetcher()
topics = fetcher.fetch_trending_topics(category="beauty", limit=10)

for topic in topics:
    print(f"{topic['rank']}. {topic['topic']} - 热度: {topic['heat']}")
```

### 3. 发布笔记

```python
from scripts.note_publisher import NotePublisher

publisher = NotePublisher()

# 创建笔记内容
content = {
    "title": "今日穿搭分享",
    "content": "今天分享一套春季穿搭...",
    "images": ["https://example.com/image1.jpg"],
    "topics": ["穿搭", "春季", "日常"]
}

# 创建并发布
note_id = publisher.create_note(content, content["images"])
result = publisher.publish_note(note_id)
print(f"笔记发布成功: {result['note_id']}")
```

### 4. 获取笔记数据

```python
from scripts.stats_fetcher import StatsFetcher

fetcher = StatsFetcher()
stats = fetcher.get_note_stats("note_123456")

print(f"曝光: {stats['exposure']}")
print(f"点赞: {stats['like']}")
print(f"收藏: {stats['collect']}")
print(f"评论: {stats['comment']}")
```

## API限流

| 接口类型 | 限流 |
|---------|------|
| 热点话题API | 100次/分钟 |
| 笔记创建API | 50次/分钟 |
| 笔记发布API | 20次/分钟 |
| 数据统计API | 200次/分钟 |

## 完整工作流示例

```python
from scripts.trending_fetcher import TrendingFetcher
from scripts.note_publisher import NotePublisher
from scripts.stats_fetcher import StatsFetcher

# Step 1: 采集热点话题
fetcher = TrendingFetcher()
topics = fetcher.fetch_trending_topics(category="fashion", limit=5)
hot_topic = topics[0]["topic"]

# Step 2: 基于热点创作内容
content = {
    "title": f"#{hot_topic} 今日分享",
    "content": f"今天聊聊{hot_topic}...",
    "images": ["image1.jpg", "image2.jpg"],
    "topics": [hot_topic, "时尚", "穿搭"]
}

# Step 3: 发布笔记
publisher = NotePublisher()
note_id = publisher.create_note(content, content["images"])
publisher.publish_note(note_id)

# Step 4: 监控数据
stats_fetcher = StatsFetcher()
stats = stats_fetcher.get_note_stats(note_id)
print(f"笔记表现: 曝光{stats['exposure']}, 互动{stats['like'] + stats['comment']}")
```

## 测试

```bash
cd skills/oms-xiaohongshu-automation
python -m pytest tests/ -v
```
