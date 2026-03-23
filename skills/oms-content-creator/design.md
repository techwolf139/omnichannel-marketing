# 爆款文案生成引擎 - 详细设计文档

## 1. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    oms-content-creator                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Generator  │  │   Rewriter   │  │   Trending   │      │
│  │   (生成器)    │  │   (改写器)    │  │   (热点匹配)  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 2. 模块设计

### 2.1 ContentGenerator (内容生成器)

**职责:** 基于输入参数生成各类内容

**核心方法:**

| 方法 | 输入 | 输出 | 说明 |
|------|------|------|------|
| generate_title | topic, style | list[str] | 生成多风格标题 |
| generate_body | topic, format, style | str | 生成正文内容 |
| generate_script | topic, duration, style | dict | 生成视频脚本 |

**标题生成策略:**

```python
TITLE_TEMPLATES = {
    "viral": [
        "{topic}的{num}个惊人秘密",
        "关于{topic}你不知道的事",
        "为什么{topic}让所有人疯狂？",
        "{topic}，原来我们都错了！",
    ],
    "question": [
        "{topic}真的有用吗？",
        "如何选择{topic}？",
        "{topic}值不值得买？",
    ],
    "list": [
        "{topic}的{num}种用法",
        "{num}个{topic}选购技巧",
        "盘点{num}款热门{topic}",
    ],
}
```

### 2.2 ContentRewriter (内容改写器)

**职责:** 将内容改写为不同平台风格

**平台适配策略:**

```python
PLATFORM_CONFIG = {
    "wechat": {
        "max_chars": 20000,
        "style": "depth",
        "features": ["story", "insight", "cta"],
        "emoji": False,
    },
    "xiaohongshu": {
        "max_chars": 1000,
        "style": "casual",
        "features": ["emoji", "bullet", "tag"],
        "emoji": True,
    },
    "zhihu": {
        "max_chars": 10000,
        "style": "professional",
        "features": ["logic", "data", "conclusion"],
        "emoji": False,
    },
}
```

**改写流程:**
1. 检测内容长度，截取至平台限制
2. 根据平台风格调整语气
3. 添加平台特色元素(emoji/标签等)
4. 优化段落结构

### 2.3 TrendingMatcher (热点匹配器)

**职责:** 匹配热门话题，提升内容曝光

**热点数据结构:**

```python
TrendingTopic {
    id: str
    name: str              # 话题名称
    category: str          # 分类
    heat_score: float      # 热度分(0-1)
    relevance_score: float # 相关度分(0-1)
    platform: str          # 来源平台
    updated_at: datetime   # 更新时间
}
```

**匹配算法:**
1. 提取内容关键词
2. 计算与热点的语义相似度
3. 按综合得分排序返回

## 3. 数据模型

### 3.1 脚本输出格式

```json
{
  "metadata": {
    "topic": "视频主题",
    "duration": 60,
    "style": "viral",
    "target_platform": "douyin"
  },
  "scenes": [
    {
      "scene_number": 1,
      "timestamp": "0-3",
      "duration": 3,
      "type": "hook",
      "visual": "特写镜头，手持产品",
      "narration": "你知道吗？90%的人用错了方法！",
      "caption": "开场钩子",
      "bgm": "紧张节奏"
    }
  ],
  "hooks": [
    "你知道吗？90%的人用错了方法！",
    "这个产品让我省下1000块！",
    "别再被坑了！"
  ],
  "call_to_action": "点击左下角链接，限时优惠！",
  "hashtags": ["#好物推荐", "#省钱攻略"]
}
```

## 4. 扩展设计

### 4.1 新增平台支持

要支持新平台，需在 `ContentRewriter.PLATFORM_LIMITS` 和 `PLATFORM_CONFIG` 中添加配置:

```python
PLATFORM_LIMITS["new_platform"] = 5000
PLATFORM_CONFIG["new_platform"] = {
    "max_chars": 5000,
    "style": "custom",
    "features": ["feature1", "feature2"],
}
```

### 4.2 自定义标题模板

可通过继承 `ContentGenerator` 并重写 `TITLE_TEMPLATES` 来扩展:

```python
class CustomGenerator(ContentGenerator):
    TITLE_TEMPLATES = {
        "custom_style": ["{topic}独家揭秘", "{topic}必看"]
    }
```

## 5. 性能考虑

- 标题生成: O(1) - 模板替换
- 内容改写: O(n) - 文本处理
- 热点匹配: 依赖外部API，建议缓存

## 6. 错误处理

| 场景 | 处理方式 |
|------|----------|
| 无效平台 | 返回原始内容，记录警告 |
| 内容为空 | 返回空字符串 |
| 热点API失败 | 返回空列表，不影响主流程 |
