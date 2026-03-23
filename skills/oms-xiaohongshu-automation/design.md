# 小红书自动化工具集 - 设计文档

## 1. 概述

### 1.1 背景

小红书作为主流内容社交平台，品牌方和MCN机构需要高效的内容运营工具来提升运营效率。本模块提供热点话题采集、笔记自动发布、数据统计分析三大核心能力。

### 1.2 设计目标

- **热点感知**: 实时获取平台热门话题，辅助内容选题
- **内容发布**: 支持批量图文笔记发布，提升发布效率
- **数据监控**: 追踪笔记表现，量化内容效果

## 2. 架构设计

### 2.1 组件图

```
┌─────────────────────────────────────────────────────────────┐
│                    小红书自动化工具集                         │
├───────────────┬───────────────┬─────────────────────────────┤
│ TrendingFetcher│ NotePublisher │      StatsFetcher          │
│   热点采集器    │   笔记发布器   │        数据统计器            │
├───────────────┼───────────────┼─────────────────────────────┤
│ fetch_trending │ create_note() │    get_note_stats()        │
│  _topics()     │ publish_note()│                            │
└───────┬───────┴───────┬───────┴────────────┬────────────────┘
        │               │                    │
        └───────────────┴────────────────────┘
                          │
                    ┌─────┴─────┐
                    │ XHS API   │
                    │ 小红书接口 │
                    └───────────┘
```

### 2.2 数据流

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   热点采集    │────→│   内容创作    │────→│   笔记发布    │
│ Trending     │     │ Content      │     │ NotePublish  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                                                  ↓
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   策略调整    │←────│   数据分析    │←────│   数据监控    │
│  Strategy    │     │  Analytics   │     │  StatsFetch  │
└──────────────┘     └──────────────┘     └──────────────┘
```

## 3. 模块详细设计

### 3.1 TrendingFetcher (热点采集器)

**职责**: 获取小红书热门话题列表

**核心方法**:
```python
class TrendingFetcher:
    def fetch_trending_topics(
        self, 
        category: str = "all", 
        limit: int = 20
    ) -> list[dict]:
        """
        获取热门话题列表
        
        Args:
            category: 话题分类 (all/beauty/fashion/food/travel)
            limit: 返回数量限制
            
        Returns:
            list[dict]: 话题列表，每项包含topic/heat/category/rank/trend
        """
```

**数据结构**:
```python
TrendingTopic = {
    "topic": str,       # 话题名称，如"春季穿搭"
    "heat": int,        # 热度值，如1000000
    "category": str,    # 分类，如"穿搭"
    "rank": int,        # 排名，如1
    "trend": str        # 趋势，如"rising"
}
```

### 3.2 NotePublisher (笔记发布器)

**职责**: 创建和发布小红书笔记

**核心方法**:
```python
class NotePublisher:
    def __init__(self, xhs_client=None):
        self.client = xhs_client
    
    def create_note(self, content: dict, images: list[str]) -> str:
        """
        创建笔记草稿
        
        Args:
            content: 笔记内容，包含title/content/topics
            images: 图片URL列表
            
        Returns:
            str: 笔记ID
        """
    
    def publish_note(self, note_id: str) -> dict:
        """
        发布笔记
        
        Args:
            note_id: 笔记ID
            
        Returns:
            dict: 发布结果，包含status/note_id
        """
```

**数据结构**:
```python
NoteContent = {
    "title": str,           # 标题
    "content": str,         # 正文
    "images": list[str],    # 图片列表
    "topics": list[str],    # 话题标签
    "location": str         # 地理位置
}

PublishResult = {
    "status": str,      # "published" | "pending" | "failed"
    "note_id": str,
    "published_at": str # ISO时间
}
```

### 3.3 StatsFetcher (数据统计器)

**职责**: 获取笔记的曝光和互动数据

**核心方法**:
```python
class StatsFetcher:
    def __init__(self, xhs_client=None, note_adapter=None):
        self.client = xhs_client
        self.adapter = note_adapter
    
    def get_note_stats(self, note_id: str) -> dict:
        """
        获取笔记统计数据
        
        Args:
            note_id: 笔记ID
            
        Returns:
            dict: 统计数据，包含曝光/点赞/收藏/评论等
        """
```

**数据结构**:
```python
NoteStats = {
    "note_id": str,
    "exposure": int,    # 曝光量
    "like": int,        # 点赞数
    "collect": int,     # 收藏数
    "comment": int,     # 评论数
    "share": int,       # 分享数
    "read": int         # 阅读量
}
```

## 4. 错误处理

### 4.1 错误码定义

| 错误码 | 名称 | 说明 | 处理建议 |
|--------|------|------|----------|
| 4001 | AUTH_FAILED | 认证失败 | 刷新token |
| 4002 | INVALID_PARAM | 参数错误 | 检查参数 |
| 4003 | CONTENT_VIOLATION | 内容违规 | 人工审核 |
| 4004 | RATE_LIMIT | 频率限制 | 指数退避 |
| 4005 | NOTE_NOT_FOUND | 笔记不存在 | 检查ID |

### 4.2 重试策略

```python
class XHSAutomationError(Exception):
    """小红书自动化异常基类"""
    pass

class RateLimitError(XHSAutomationError):
    """频率限制异常"""
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")
```

## 5. 限流策略

| API类型 | QPS限制 | 说明 |
|---------|---------|------|
| 热点话题 | 100/分钟 | 实时数据，限制较严 |
| 笔记创建 | 50/分钟 | 防止批量灌水 |
| 笔记发布 | 20/分钟 | 严格限制发布频率 |
| 数据统计 | 200/分钟 | 查询类接口，限制宽松 |

## 6. 集成接口

### 6.1 与OMS技能集成

| OMS技能 | 集成方式 | 用途 |
|---------|----------|------|
| oms-xhs-integration | API调用 | 复用认证和基础API |
| oms-one-id-merge | 用户识别 | 关联运营账号 |
| oms-promotion-engine | 事件触发 | 数据达标后发券 |

### 6.2 外部系统集成

```
┌──────────────┐
│ 内容管理系统  │ → 提供图文素材
└──────────────┘
       ↓
┌──────────────┐
│ 小红书自动化  │ → 发布到小红书
└──────────────┘
       ↓
┌──────────────┐
│ 数据分析平台  │ ← 获取统计数据
└──────────────┘
```

## 7. 测试策略

### 7.1 单元测试

- TrendingFetcher: 测试话题解析、分类筛选
- NotePublisher: 测试内容验证、发布流程
- StatsFetcher: 测试数据解析、错误处理

### 7.2 集成测试

- 完整发布流程
- 错误重试机制
- 限流处理
