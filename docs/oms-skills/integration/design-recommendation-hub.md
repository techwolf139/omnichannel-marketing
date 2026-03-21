# 推荐中台详细设计

本文档定义推荐中台（Recommendation Hub）的详细设计规范，实现跨平台个性化推荐服务。

## 1. 设计目标

- **精准推荐**：基于全渠道用户行为的个性化推荐
- **实时响应**：毫秒级推荐结果返回
- **多场景支持**：首屏推荐、搜索排序、详情页推荐、购物车推荐
- **可解释性**：推荐理由可解释，提升用户信任

## 2. 推荐场景

| 场景 | 代码 | 说明 |
|------|------|------|
| 首页推荐 | HOME_RECOMMEND | 首屏个性化商品/内容推荐 |
| 商品详情页推荐 | PDP_RECOMMEND | "看了又看"、"相似商品" |
| 购物车推荐 | CART_RECOMMEND | "凑单推荐"、"加购推荐" |
| 订单完成页推荐 | ORDER_RECOMMEND | "再次购买"、"猜你喜欢" |
| 搜索排序 | SEARCH_RANK | 搜索结果智能排序 |
| 直播推荐 | LIVE_RECOMMEND | 直播间商品推荐 |
| 门店推荐 | STORE_RECOMMEND | 附近门店推荐 |

## 3. 推荐模型

### 3.1 模型类型

| 模型 | 适用场景 | 说明 |
|------|----------|------|
| 协同过滤 (CF) | 首页推荐、相似推荐 | 基于用户/物品相似度 |
| 内容推荐 (CB) | 冷启动、新用户 | 基于内容特征 |
| 深度学习 (DIN/DIEN) | 点击率预估 | 注意力机制 |
| 知识图谱 (KG) | 跨类目推荐 | 知识推理 |
| 强化学习 (RL) | 长期收益优化 | 序列决策 |

### 3.2 模型架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      推荐模型架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  特征输入层:                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │ 用户特征    │  │ 商品特征    │  │ 上下文特征  │           │
│  │ • 行为序列  │  │ • 基本属性  │  │ • 时间      │           │
│  │ • 偏好标签  │  │ • 销量      │  │ • 位置      │           │
│  │ • 生命周期  │  │ • 价格带    │  │ • 设备      │           │
│  └─────────────┘  └─────────────┘  └─────────────┘           │
│          │                │                │                    │
│          └────────────────┼────────────────┘                    │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    特征交叉层 (Feature Crossing)            │   │
│  │              Deep & Cross Network                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    DNN (Deep Neural Network)               │   │
│  │              多层感知机 (MLP)                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│                     ┌──────────┐                              │
│                     │ 预测层   │                              │
│                     │ CTR/CVR  │                              │
│                     └──────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. 数据模型

### 4.1 用户特征

```json
{
  "one_id": "uuid-xxx",
  "user_features": {
    "basic": {
      "age_range": "25-35",
      "gender": "female",
      "member_level": "gold",
      "lifecycle_stage": "active"
    },
    "behavior": {
      "total_orders": 15,
      "avg_order_amount": 566.67,
      "favorite_categories": ["女装", "美妆"],
      "favorite_price_ranges": ["200-500", "500-1000"],
      "recent_30d_browse_count": 120,
      "recent_30d_cart_count": 8
    },
    "interest": {
      "tags": ["时尚", "职场", "母婴"],
      "brand_preferences": ["品牌A", "品牌B"],
      "style_preferences": ["简约", "韩风"]
    }
  },
  "sequence_features": {
    "browse_sequence": [
      {"sku_id": "SKU001", "timestamp": 1705312200, "duration": 30},
      {"sku_id": "SKU002", "timestamp": 1705312260, "duration": 45}
    ],
    "cart_sequence": [
      {"sku_id": "SKU003", "timestamp": 1705312400}
    ]
  }
}
```

### 4.2 商品特征

```json
{
  "sku_id": "SKU_2024_001",
  "product_features": {
    "basic": {
      "category_id": "CAT_WOMEN_OUTER",
      "category_path": "女装/外套/羽绒服",
      "brand_id": "BRAND_A",
      "price": 599.00,
      "tags": ["韩版", "轻薄", "保暖"]
    },
    "statistics": {
      "sales_30d": 1500,
      "sales_7d": 450,
      "exposure_7d": 15000,
      "ctr": 0.035,
      "cvr": 0.025
    },
    "quality": {
      "rating": 4.8,
      "review_count": 2300,
      "return_rate": 0.03
    }
  }
}
```

### 4.3 推荐结果

```json
{
  "request_id": "req_xxx_xxx",
  "scene": "HOME_RECOMMEND",
  "one_id": "uuid-xxx",
  "recommendations": [
    {
      "sku_id": "SKU_2024_001",
      "score": 0.95,
      "reason": "同类用户也在买",
      "source": "cf_similarity",
      "position": 1
    },
    {
      "sku_id": "SKU_2024_002",
      "score": 0.88,
      "reason": "根据您的浏览偏好推荐",
      "source": "content_based",
      "position": 2
    }
  ],
  "explain": {
    "user_profile": "时尚女性，偏好200-500元",
    "matching_tags": ["韩版", "简约"]
  },
  "timestamp": 1705312800
}
```

## 5. 核心算法

### 5.1 协同过滤

```python
class CollaborativeFiltering:
    """协同过滤推荐"""
    
    def user_based_cf(self, one_id: str, candidates: List[str], k: int = 20):
        """
        基于用户的协同过滤
        
        Args:
            one_id: 目标用户
            candidates: 候选商品列表
            k: 使用的相似用户数
        
        Returns:
            推荐商品及得分
        """
        # 1. 获取目标用户行为向量
        user_vector = self.get_user_behavior_vector(one_id)
        
        # 2. 找到相似用户
        similar_users = self.find_similar_users(user_vector, top_k=k)
        
        # 3. 聚合相似用户的商品偏好
        scores = {}
        for user, similarity in similar_users:
            user_favorites = self.get_user_favorites(user)
            for sku, rating in user_favorites:
                scores[sku] = scores.get(sku, 0) + similarity * rating
        
        # 4. 过滤并排序
        scores = {k: v for k, v in scores.items() if k in candidates}
        return sorted(scores.items(), key=lambda x: -x[1])[:10]
    
    def item_based_cf(self, sku_id: str, candidates: List[str]):
        """
        基于商品的协同过滤
        
        Args:
            sku_id: 目标商品
            candidates: 候选商品列表
        """
        # 获取相似商品
        similar_items = self.get_similar_items(sku_id, top_k=50)
        
        # 过滤候选
        scores = {sku: sim for sku, sim in similar_items if sku in candidates}
        return sorted(scores.items(), key=lambda x: -x[1])[:10]
```

### 5.2 深度学习推荐

```python
class DeepRecommendationModel:
    """深度学习推荐模型 (DIN 简化版)"""
    
    def __init__(self):
        self.embedding_dim = 32
        self.dnn_layers = [256, 128, 64]
        
    def predict(self, user_features: dict, item_features: dict) -> float:
        """
        CTR 预估
        
        Args:
            user_features: 用户特征 (含行为序列)
            item_features: 商品特征
        
        Returns:
            点击概率
        """
        # 1. 用户兴趣抽取 (Attention)
        user_interest = self.attention_layer(
            query=item_features['embedding'],
            key=user_features['behavior_embeddings'],
            value=user_features['behavior_embeddings']
        )
        
        # 2. 特征拼接
        concat_features = tf.concat([
            user_features['basic_embeddings'],
            user_interest,
            item_features['embedding'],
            user_features['context_embeddings']
        ], axis=-1)
        
        # 3. DNN 前向传播
        dnn_input = concat_features
        for units in self.dnn_layers:
            dnn_input = tf.layers.dense(dnn_input, units, activation='relu')
            dnn_input = tf.layers.dropout(dnn_input, 0.2)
        
        # 4. 输出层
        output = tf.layers.dense(dnn_input, 1, activation='sigmoid')
        return output
```

### 5.3 混排策略

```python
class BlendingStrategy:
    """推荐结果混排策略"""
    
    def blend(self, 
              cf_scores: dict, 
              cb_scores: dict, 
              rl_scores: dict,
              weights: dict = None) -> List[Tuple[str, float]]:
        """
        多模型结果融合
        
        Args:
            cf_scores: 协同过滤得分
            cb_scores: 内容推荐得分
            rl_scores: 强化学习得分
            weights: 各模型权重
        
        Returns:
            融合后的推荐列表
        """
        if weights is None:
            weights = {'cf': 0.4, 'cb': 0.3, 'rl': 0.3}
        
        # 1. 分数归一化
        cf_norm = self.normalize(cf_scores)
        cb_norm = self.normalize(cb_scores)
        rl_norm = self.normalize(rl_scores)
        
        # 2. 加权融合
        final_scores = {}
        all_items = set(cf_scores) | set(cb_scores) | set(rl_scores)
        
        for item in all_items:
            score = (
                weights['cf'] * cf_norm.get(item, 0) +
                weights['cb'] * cb_norm.get(item, 0) +
                weights['rl'] * rl_norm.get(item, 0)
            )
            final_scores[item] = score
        
        # 3. 多样性惩罚
        final_scores = self.diversity_penalty(final_scores)
        
        return sorted(final_scores.items(), key=lambda x: -x[1])[:20]
    
    def diversity_penalty(self, scores: dict, alpha: float = 0.3) -> dict:
        """
        多样性惩罚：避免推荐结果过于集中
        """
        # 获取推荐类目分布
        category_dist = self.get_category_distribution(list(scores.keys()))
        
        # 对类目集中项降权
        for item, score in scores.items():
            category = self.get_item_category(item)
            if category_dist[category] > 0.3:  # 类目占比超过30%
                scores[item] = score * (1 - alpha)
        
        return scores
```

## 6. API 接口

### 6.1 商品推荐

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /recommend/product` | GET | 获取商品推荐 |

```json
// Request
{
  "one_id": "uuid-xxx",
  "scene": "HOME_RECOMMEND",
  "size": 10,
  "context": {
    "page": 1,
    "position": "首屏"
  }
}

// Response
{
  "code": 0,
  "data": {
    "request_id": "req_xxx",
    "items": [
      {
        "sku_id": "SKU001",
        "title": "女装冬季羽绒服",
        "image_url": "https://xxx.jpg",
        "price": 599.00,
        "score": 0.95,
        "reason": "同类用户也在买"
      }
    ],
    "explain": {
      "user_profile": "时尚女性",
      "update_time": "2024-01-15 14:00:00"
    }
  }
}
```

### 6.2 推荐反馈

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /recommend/feedback` | POST | 上报推荐效果 |

```json
// Request
{
  "request_id": "req_xxx",
  "feedback_type": "click",  // click/expose/purchase
  "sku_id": "SKU001",
  "timestamp": 1705312800
}
```

## 7. 特征工程

### 7.1 特征类型

| 类别 | 特征 | 更新频率 |
|------|------|----------|
| 用户基础 | 年龄、性别、会员等级 | T+1 |
| 用户行为 | 浏览/点击/购买序列 | 实时 |
| 用户偏好 | 类目偏好、价格带 | 每日 |
| 商品基础 | 类目、品牌、价格 | T+1 |
| 商品统计 | 销量、评分、转化率 | 每日 |
| 上下文 | 时间、位置、天气 | 实时 |

### 7.2 特征存储 (Feature Store)

```
┌─────────────────────────────────────────────────────────────┐
│                    Feature Store 架构                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  离线特征 (Hive/Spark):                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 用户基础特征 | 商品特征 | 统计特征                    │   │
│  └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          ▼ (每日同步)                       │
│  在线特征 (Redis):                                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 用户实时行为 | 商品实时统计 | 上下文特征              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 8. A/B 测试

### 8.1 实验配置

```json
{
  "experiment_id": "exp_recommend_v2",
  "name": "首页推荐算法V2",
  "description": "对比CF和深度学习模型效果",
  "status": "running",
  "traffic": 0.2,
  "variants": [
    {
      "name": "control",
      "algorithm": "collaborative_filtering",
      "weight": 0.5
    },
    {
      "name": "treatment", 
      "algorithm": "deep_learning",
      "weight": 0.5
    }
  ],
  "metrics": [
    {"name": "ctr", "type": "ctr"},
    {"name": "cvr", "type": "cvr"},
    {"name": "gmv", "type": "gmv"}
  ],
  "start_time": "2024-01-01",
  "end_time": "2024-01-31"
}
```

### 8.2 流量分配

```
请求 → Hash(one_id + experiment_id) → [0,1] 区间
                                │
                                ├── [0, 0.1) → Variant A
                                ├── [0.1, 0.3) → Variant B
                                └── [0.3, 1.0) → Control
```

## 9. 性能指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| P99 Latency | 推荐接口P99延迟 | < 50ms |
| QPS | 推荐服务吞吐量 | > 10000 |
| CTR | 点击率 | +5% vs 基线 |
| CVR | 转化率 | +3% vs 基线 |
| Coverage | 覆盖率 | > 30% |

## 10. 冷启动策略

| 场景 | 策略 |
|------|------|
| 新用户 | 热门商品 + 类目通用偏好 + 人口属性相似用户 |
| 新商品 | 相似已有商品、协同过滤、相似类目 |
| 老用户新场景 | 跨场景行为迁移 |
