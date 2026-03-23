---
name: oms-social-media-auto
description: "Use when posting content to multiple platforms simultaneously, cross-posting to Zhihu, Weibo, Xiaohongshu, or Twitter, managing multi-account social media publishing, or automating content distribution workflows."
---

# 全平台分发适配器

## Overview

全平台社交媒体内容分发适配器，实现一键多平台发布。支持知乎、微博、小红书、Twitter四大主流平台，通过统一内容模型自动适配各平台格式要求，实现内容跨平台同步与多账号管理。

## When to Use

- 全平台一键分发内容
- 跨平台内容同步管理
- 多账号统一管理
- 内容格式自动适配
- 发布状态批量追踪

**触发词**: "全平台分发"、"多平台发布"、"一键同步"、"跨平台发文"

## Core Pattern

### 支持平台

| 平台 | 内容类型 | 核心API | 说明 |
|------|----------|---------|------|
| 知乎 | 文章/回答 | `article.create`, `answer.create` | 长文内容，支持话题标签 |
| 微博 | 博文/图文 | `statuses.update`, `statuses.upload` | 短内容，支持图片/视频 |
| 小红书 | 笔记 | `note.publish` | 图文笔记，支持话题和标签 |
| Twitter | 推文 | `tweets.create`, `media.upload` | 短文本，支持多媒体 |

### 认证方式

各平台OAuth 2.0认证 + Access Token管理

## Implementation

### 数据模型

**SocialContent** (统一内容模型):
```python
{
    "content_id": str,           # 内容唯一ID
    "title": str,                # 标题（可选，适用于长文）
    "body": str,                 # 正文内容
    "media": list[str],          # 媒体文件路径列表
    "topics": list[str],         # 话题/标签列表
    "mentions": list[str],       # @提及用户列表
    "visibility": str,           # 可见性: public/friends/private
    "scheduled_at": datetime,    # 定时发布时间
    "source_url": str            # 原文链接（用于跨平台引用）
}
```

**DispatchResult** (分发结果):
```python
{
    "content_id": str,
    "platform": str,             # 平台标识
    "status": str,               # 状态: success/pending/failed
    "platform_content_id": str,  # 平台返回的内容ID
    "platform_url": str,         # 平台内容链接
    "published_at": datetime,    # 实际发布时间
    "error_message": str         # 错误信息（失败时）
}
```

### 平台适配规则

| 规则 | 知乎 | 微博 | 小红书 | Twitter |
|------|------|------|--------|---------|
| 最大长度 | 无限制 | 5000字 | 1000字 | 280/4000字 |
| 图片数量 | 无限制 | 18张 | 18张 | 4张 |
| 视频支持 | 是 | 是 | 是 | 是 |
| 话题格式 | #话题# | #话题# | #话题 | #话题 |
| 链接支持 | 是 | 是 | 个人主页 | 是 |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 单平台发布 | `dispatch(content, [platform])` | 按平台限流 |
| 全平台发布 | `dispatch_all(content)` | 聚合限流 |
| 内容转换 | `transform(content, platform)` | 无 |
| 发布状态查询 | `get_status(content_id)` | 100/分钟 |
| 批量删除 | `delete_batch(content_ids)` | 50/分钟 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 内容超长度限制 | 发布失败 | 使用ContentTransformer自动截断或拆分 |
| 图片格式不支持 | 上传失败 | 提前转换格式为平台支持的类型 |
| 未处理限流 | 账号临时封禁 | 实现指数退避重试机制 |
| Token过期未刷新 | 所有发布失败 | 自动检测并刷新Token |
| 未检查平台规则 | 内容被屏蔽 | 预检敏感词和平台规范 |
