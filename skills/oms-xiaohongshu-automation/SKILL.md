---
name: oms-xiaohongshu-automation
description: "Use when automating Xiaohongshu tasks: fetching trending topics, publishing notes, or viewing note analytics. 用于小红书自动化任务：热点话题采集、笔记自动发布、数据统计分析。"
---

# 小红书自动化适配器

## Overview

小红书自动化工具集，支持热点话题实时采集、笔记内容自动发布、笔记数据分析三大核心场景。适用于内容运营人员批量管理小红书账号，提升运营效率。

## When to Use

- 热点话题采集：实时获取小红书热门话题，辅助内容选题
- 笔记自动发布：批量发布图文笔记，支持定时发布
- 数据统计分析：获取笔记曝光、互动数据，评估内容效果

**触发词**: "小红书自动化"、"热点采集"、"笔记发布"、"小红书数据"

## Core Pattern

### 自动化流程

| 场景 | 核心类 | 方法 | 说明 |
|------|--------|------|------|
| 热点采集 | `TrendingFetcher` | `fetch_trending_topics()` | 获取热门话题列表 |
| 笔记发布 | `NotePublisher` | `create_note()`, `publish_note()` | 创建并发布笔记 |
| 数据分析 | `StatsFetcher` | `get_note_stats()` | 获取笔记统计数据 |

### 数据流

```
热点采集 → 内容创作 → 笔记发布 → 数据监控
     ↑                              ↓
     └────── 效果反馈 ← 数据分析 ←──┘
```

## Implementation

### 数据模型

**TrendingTopic** (热点话题):
```python
{
    "topic": str,           # 话题名称
    "heat": int,            # 热度值
    "category": str,        # 分类：美妆/穿搭/美食/旅行等
    "rank": int,            # 排名
    "trend": str            # 趋势：rising/stable/declining
}
```

**NoteContent** (笔记内容):
```python
{
    "title": str,           # 标题
    "content": str,         # 正文内容
    "images": list[str],    # 图片URL列表
    "topics": list[str],    # 关联话题标签
    "location": str         # 地理位置（可选）
}
```

**NoteStats** (笔记统计数据):
```python
{
    "note_id": str,
    "exposure": int,        # 曝光量
    "like": int,            # 点赞数
    "collect": int,         # 收藏数
    "comment": int,         # 评论数
    "share": int,           # 分享数
    "read": int             # 阅读量
}
```

### 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 4001 | 认证失败 | 刷新access_token |
| 4002 | 参数错误 | 检查输入参数 |
| 4003 | 内容违规 | 人工审核内容 |
| 4004 | 频率限制 | 指数退避重试 |
| 4005 | 笔记不存在 | 检查note_id |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 获取热点话题 | `fetch_trending_topics()` | 100/分钟 |
| 创建笔记草稿 | `create_note()` | 50/分钟 |
| 发布笔记 | `publish_note()` | 20/分钟 |
| 获取笔记数据 | `get_note_stats()` | 200/分钟 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 图片尺寸不符合 | 发布失败 | 使用3:4或9:16比例，大小<20MB |
| 话题标签过多 | 被限流 | 单篇笔记标签不超过10个 |
| 发布频率过高 | 账号风控 | 单账号日发布不超过5篇 |
| 内容含敏感词 | 审核不通过 | 使用敏感词检测API预检 |
