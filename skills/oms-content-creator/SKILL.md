---
name: oms-content-creator
description: "Use when generating viral content, writing titles, creating copy, or adapting content for different platforms. Triggers: content generation requests, title writing, viral copy creation, platform-specific content adaptation."
---

# 爆款文案生成引擎

## Overview

基于热点趋势和用户画像，自动生成多平台适配的爆款标题、正文和短视频脚本。支持一键改写适配微信、小红书、知乎、微博等不同平台的风格要求。

## When to Use

- 生成吸引眼球的爆款标题
- 撰写产品推广文案/正文
- 创作短视频口播脚本
- 将内容改写为不同平台风格
- 匹配热门话题提升内容曝光
- 优化现有内容的传播效果

**触发词**: "生成标题"、"写文案"、"内容创作"、"爆款文案"、"改写"、"脚本"

## Core Pattern

### 内容生成类型

| 类型 | 说明 | 输出格式 |
|------|------|----------|
| 标题生成 | 基于主题生成多风格标题 | 标题列表(5-10个) |
| 正文创作 | 产品/活动推广文案 | Markdown格式 |
| 脚本生成 | 短视频口播脚本 | JSON(场景+旁白+时长) |
| 平台改写 | 适配不同平台风格 | 目标平台格式 |

### 标题风格类型

| 风格 | 特点 | 适用场景 |
|------|------|----------|
| viral(爆款) | 数字+情绪+悬念 | 通用引流 |
| question(疑问) | 提问引发好奇 | 知乎、公众号 |
| list(清单) | 数字列表式 | 小红书、微博 |
| story(故事) | 场景化叙事 | 深度内容 |
| benefit(利益) | 直击痛点收益 | 电商推广 |

### 平台适配规则

| 平台 | 字数限制 | 风格特点 | 禁忌 |
|------|----------|----------|------|
| wechat | 20000 | 深度、故事化 | 过度营销感 |
| xiaohongshu | 1000 | emoji、短句、真实感 | 生硬广告 |
| zhihu | 10000 | 专业、逻辑、干货 | 标题党 |
| weibo | 2000 | 热点、互动、话题标签 | 长篇大论 |
| twitter | 280 | 简洁、直接 | 中文过多 |

## Implementation

### 内容生成结构

```
ContentGenerator {
  generate_title(topic: string, style: string) -> list[string]
  generate_body(topic: string, format: string, style: string) -> string
  generate_script(topic: string, duration: int, style: string) -> dict
}

TrendingMatcher {
  match_trending_topics(content: string) -> list[dict]
  fetch_platform_trending(platform: string, category: string) -> list[dict]
}

ContentRewriter {
  PLATFORM_LIMITS: dict[platform, max_chars]
  rewrite_for_platform(content: string, platform: string) -> string
}
```

### 脚本输出格式

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "duration": 3,
      "visual": "画面描述",
      "narration": "旁白文案"
    }
  ],
  "total_duration": 60,
  "hooks": ["开场钩子1", "开场钩子2"],
  "call_to_action": "引导行动"
}
```

## Quick Reference

### 内容创作场景

**场景A**: "为新品生成小红书爆款标题"
- 输入: 产品名称+卖点
- 输出: 5个符合小红书风格的标题
- 自动匹配emoji和话题标签

**场景B**: "将产品介绍改写成短视频脚本"
- 输入: 产品介绍文案+目标时长
- 输出: 分镜脚本(场景+旁白+时长)
- 包含开场hook和引导行动

**场景C**: "同一内容多平台分发"
- 输入: 原始内容+目标平台列表
- 输出: 各平台适配版本
- 自动调整字数和风格

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 标题过度夸张 | 用户反感、平台限流 | 真实有料+适度悬念 |
| 忽略平台调性 | 内容不契合、互动低 | 先了解平台用户偏好 |
| 内容过长 | 完读率低 | 控制字数在平台限制80% |
| 热点硬蹭 | 关联生硬 | 选择与内容强相关的热点 |
| 忽视行动引导 | 转化低 | 每个内容都有明确CTA |
