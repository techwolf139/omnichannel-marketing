# OMS 社交内容技能实现计划

## 背景

作为 OMS Phase1 营销获客的扩展，填补内容创作与社交分发的能力空白。

## 技能列表

| 技能 | 名称 | 核心功能 |
|------|------|---------|
| `oms-content-creator` | 爆款文案生成 | 标题/正文/脚本/热点匹配 |
| `oms-wechat-ai-publisher` | 公众号自动发文 | 写稿/排版/封面/存草稿 |
| `oms-xiaohongshu-automation` | 小红书自动化 | 热点采集/笔记发布/数据查看 |
| `oms-social-media-auto` | 全平台分发 | 知乎/微博/小红书/X一键同步 |
| `oms-bounty-hunter` | 开源任务接单 | GitHub悬赏/方案撰写/提交赚钱 |

## 实现规范

### 目录结构

```
skills/
├── oms-content-creator/
│   ├── SKILL.md
│   ├── README.md
│   ├── design.md
│   └── scripts/
│       ├── __init__.py
│       ├── generator.py      # 文案生成核心
│       ├── trending.py       # 热点匹配
│       └── rewriter.py       # 多平台改写
├── oms-wechat-ai-publisher/
│   ├── SKILL.md
│   ├── README.md
│   ├── design.md
│   └── scripts/
│       ├── __init__.py
│       ├── auth.py          # 微信公众号认证
│       ├── client.py        # 草稿箱/发布API
│       ├── cover_generator.py
│       └── formatter.py      # Markdown→微信HTML
├── oms-xiaohongshu-automation/
│   ├── SKILL.md
│   ├── README.md
│   ├── design.md
│   └── scripts/
│       ├── __init__.py
│       ├── trending_fetcher.py  # 热点采集
│       ├── note_publisher.py   # 笔记发布
│       └── stats_fetcher.py    # 数据查看
├── oms-social-media-auto/
│   ├── SKILL.md
│   ├── README.md
│   ├── design.md
│   └── scripts/
│       ├── __init__.py
│       ├── dispatcher.py     # 分发调度器
│       ├── platforms/
│       │   ├── __init__.py
│       │   ├── zhihu.py
│       │   ├── weibo.py
│       │   ├── xhs.py
│       │   └── twitter.py
│       └── transformer.py    # 内容转换
└── oms-bounty-hunter/
    ├── SKILL.md
    ├── README.md
    ├── design.md
    └── scripts/
        ├── __init__.py
        ├── bounty_finder.py    # 任务发现
        ├── proposal_writer.py  # 方案撰写
        └── submitter.py        # 提交PR
```

### SKILL.md 格式

遵循现有模式:

```yaml
---
name: oms-{name}
description: "Use when [specific trigger scenarios]..."
---

# 技能标题

## Overview
[1-2 sentences]

## When to Use
- Scenario 1
- Scenario 2

**触发词**: "keyword1"、"keyword2"
```

### 依赖关系

- `oms-content-creator` 无依赖
- `oms-wechat-ai-publisher` 依赖 `oms-content-creator`
- `oms-xiaohongshu-automation` 依赖 `oms-content-creator`
- `oms-social-media-auto` 依赖其他三个发布技能
- `oms-bounty-hunter` 无依赖

### 关键设计决策

1. **认证**: 各平台OAuth 2.0，token存储于环境变量
2. **限流处理**: 指数退避重试
3. **错误处理**: 统一异常类 `PlatformAPIError`
4. **内容适配**: 各平台字符限制和格式转换

## Task Breakdown

### Task 1: oms-content-creator

实现爆款文案生成技能:
- 标题生成 (generate_title)
- 正文生成 (generate_body) 
- 脚本生成 (generate_script)
- 热点匹配 (match_trending_topics)
- 多平台改写 (rewrite_for_platform)

### Task 2: oms-wechat-ai-publisher

实现微信公众号自动发文技能:
- 草稿箱API (create_draft, publish_draft)
- 封面生成 (generate_cover)
- 内容排版 (format_content)
- 复用 content-creator 生成正文

### Task 3: oms-xiaohongshu-automation

实现小红书自动化技能:
- 热点采集 (fetch_trending_topics)
- 笔记发布 (create_note, publish_note)
- 数据查看 (get_note_stats)
- 复用现有 xhs-integration 的 API client

### Task 4: oms-social-media-auto

实现全平台分发技能:
- 分发调度器 (dispatch)
- 平台适配器 (zhihu, weibo, xhs, twitter)
- 内容转换 (transform_content)

### Task 5: oms-bounty-hunter

实现开源任务接单技能:
- GitHub Issues 搜索 (find_bounties)
- 方案撰写 (write_proposal)
- PR提交 (submit_pr)