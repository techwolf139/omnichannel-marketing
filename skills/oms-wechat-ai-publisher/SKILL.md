---
name: oms-wechat-ai-publisher
description: "Use when publishing WeChat public account articles, generating cover images, formatting content, or managing drafts on WeChat Official Account platform."
---

# 微信公众号自动发文适配器

## Overview

微信公众号（WeChat Official Account）内容发布适配器，实现文章草稿创建、封面生成、内容排版、定时发布等核心功能。支持Markdown转微信公众号图文格式，自动适配移动端阅读体验。

## When to Use

- 发布微信公众号文章
- 生成AI封面图
- 内容排版转换（Markdown → 微信图文）
- 管理公众号草稿
- 定时发布文章

**触发词**: "微信公众号", "公众号发文", "微信发布", "封面生成", "图文排版"

## Core Pattern

### 微信公众号API分类

| 类别 | 核心API | 说明 |
|------|---------|------|
| 素材 | `uploadimg`, `uploadnews` | 图片/图文素材上传 |
| 草稿 | `draft/add`, `draft/update` | 草稿创建与更新 |
| 发布 | `publish/submit` | 文章发布 |
| 用户 | `user/get` | 粉丝管理 |
| 统计 | `user/summary` | 数据统计 |

### 认证方式

AccessToken机制（2小时有效期）

## Implementation

### 数据模型

**WeChatAuthConfig**:
```python
{
    "app_id": str,
    "app_secret": str,
    "access_token": str,
    "token_expires_at": datetime
}
```

**WeChatArticle** (微信公众号文章):
```python
{
    "title": str,
    "author": str,
    "content": str,           # HTML格式正文
    "digest": str,            # 摘要
    "content_source_url": str, # 原文链接
    "thumb_media_id": str,    # 封面图片素材ID
    "show_cover_pic": bool,   # 是否显示封面
    "need_open_comment": bool, # 是否打开评论
    "only_fans_can_comment": bool  # 是否仅粉丝可评论
}
```

### 排版主题

| 主题 | 特点 | 适用场景 |
|------|------|----------|
| default | 经典微信风格 | 日常推文 |
| minimal | 极简留白 | 深度长文 |
| modern | 现代卡片式 | 品牌宣传 |

## Quick Reference

| 操作 | 方法 | 限流 |
|------|------|------|
| 创建草稿 | `create_draft()` | 1000/天 |
| 更新草稿 | `update_draft()` | 1000/天 |
| 发布文章 | `publish_draft()` | 100/天 |
| 生成封面 | `generate_cover()` | 无限制 |
| 内容排版 | `format_content()` | 无限制 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| AccessToken过期未刷新 | API调用失败 | 定期刷新Token |
| 图片超过5MB | 上传失败 | 压缩图片后再上传 |
| 正文超过20000字 | 发布失败 | 拆分文章或精简内容 |
| 封面比例错误 | 显示裁剪 | 使用900×383像素封面 |
| 外链未转注 | 用户无法点击 | 使用content_source_url字段 |
