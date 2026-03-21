# One-ID Hub 详细设计

本文档定义 One-ID Hub（统一身份中心）的详细设计规范，实现跨平台用户身份归一。

## 1. 设计目标

- **统一身份**：将分散在各平台的消费者身份归一为唯一标识
- **实时查询**：毫秒级响应身份查询请求
- **高准确性**：基于置信度的自动归一，减少人工干预
- **可扩展性**：支持新平台快速接入

## 2. 核心概念

### 2.1 身份类型

| 类型 | 代码 | 说明 | 示例 |
|------|------|------|------|
| 手机号 | PHONE | 最高置信度身份标识 | 138****8888 |
| 邮箱 | EMAIL | 用户注册邮箱 | u***@example.com |
| 会员号 | MEMBER_ID | 品牌会员体系ID | MBR_2024_001 |
| 平台OpenID | OPENID | 平台唯一标识 | douyin_openid_xxx |
| UnionID | UNIONID | 微信生态唯一标识 | wechat_unionid_xxx |
| 设备ID | DEVICE_ID | 设备指纹 | IDFA/GAID |

### 2.2 归一状态

| 状态 | 代码 | 说明 |
|------|------|------|
| 已归一 | MERGED | 已确认合并到 One-ID |
| 待确认 | PENDING | 需要人工确认 |
| 已拆分 | SPLIT | 从 One-ID 中拆分 |
| 孤立 | ORPHAN | 无法归一的身份 |

## 3. 数据模型

### 3.1 One-ID 主表

```sql
CREATE TABLE one_id (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    one_id VARCHAR(64) UNIQUE NOT NULL COMMENT 'One-ID唯一标识',
    primary_id_type VARCHAR(32) NOT NULL COMMENT '主标识类型',
    primary_id_value VARCHAR(128) COMMENT '主标识值（脱敏）',
    primary_id_hash VARCHAR(64) NOT NULL COMMENT '主标识哈希（检索用）',
    confidence_score DECIMAL(5,2) DEFAULT 100.00 COMMENT '置信度',
    status TINYINT DEFAULT 1 COMMENT '状态：1-正常，0-禁用',
    merge_count INT DEFAULT 0 COMMENT '合并次数',
    last_identity_id BIGINT COMMENT '最后更新的identity记录ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_primary_hash (primary_id_hash),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 3.2 身份关系表

```sql
CREATE TABLE identity_relation (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    one_id VARCHAR(64) NOT NULL COMMENT '所属One-ID',
    channel VARCHAR(32) NOT NULL COMMENT '平台渠道',
    id_type VARCHAR(32) NOT NULL COMMENT '身份类型',
    id_value VARCHAR(256) NOT NULL COMMENT '身份值',
    id_hash VARCHAR(64) NOT NULL COMMENT '身份值哈希',
    raw_value VARCHAR(512) COMMENT '原始值（加密存储）',
    confidence DECIMAL(5,2) NOT NULL COMMENT '置信度',
    last_active DATETIME COMMENT '最后活跃时间',
    status TINYINT DEFAULT 1 COMMENT '状态：1-有效，0-无效',
    merged_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '合并时间',
    expired_at DATETIME COMMENT '过期时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_one_id (one_id),
    INDEX idx_channel (channel),
    INDEX idx_id_hash (id_hash),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### 3.3 身份图谱（Neo4j）

```cypher
// 节点类型
(:OneId {one_id, confidence})
(:Identity {id_value, channel, id_type, confidence})

// 关系类型
(:OneId)-[:HAS_IDENTITY {confidence, merged_at}]->(:Identity)
(:Identity)-[:SIMILAR_TO {score, reason}]->(:Identity)
```

## 4. 归一算法

### 4.1 置信度权重

| 匹配因素 | 权重 | 说明 |
|----------|------|------|
| 手机号完全匹配 | 40% | 最高置信度 |
| 手机号哈希匹配 | 35% | 哈希脱敏匹配 |
| UnionID匹配 | 35% | 微信生态内 |
| OpenID+同设备 | 25% | 同一设备多账号 |
| 收货地址重叠 | 20% | 相同收货人 |
| 行为相似度 | 15% | 浏览/购买品类重叠 |
| 昵称相似 | 10% | 需其他因素辅助 |

### 4.2 归一决策规则

```
归一决策:
  ├── 置信度 ≥ 95%: 自动归一
  ├── 置信度 80%-95%: 高置信度归一
  ├── 置信度 60%-80%: 待确认归一
  ├── 置信度 40%-60%: 人工审核
  └── 置信度 < 40%: 不归一
```

### 4.3 身份合并流程

```
新身份进入
    │
    ▼
计算所有已有One-ID的置信度
    │
    ▼
最高置信度 ≥ 阈值？
    │
    ├── 是 → 自动合并到该One-ID
    │
    └── 否 → 检查是否有候选One-ID
              │
              ├── 有多个候选 → 推送人工审核
              │
              └── 无候选 → 创建新One-ID
```

## 5. 核心功能

### 5.1 身份查询

```python
def resolve_identity(identifier_type: str, identifier_value: str) -> dict:
    """
    通过任意标识查询One-ID
    
    Args:
        identifier_type: phone/openid/unionid/member_id
        identifier_value: 标识值
    
    Returns:
        {
            "one_id": "uuid-xxx",
            "confidence": 95.0,
            "profile": {...}
        }
    """
    # 1. 计算标识哈希
    id_hash = hash(identifier_type, identifier_value)
    
    # 2. 查询身份关系表
    identity = db.identity_relation.find_one(
        id_hash=id_hash,
        status=1
    )
    
    if not identity:
        return None
    
    # 3. 查询One-ID及画像
    one_id = db.one_id.find_one(one_id=identity.one_id)
    profile = build_profile(identity.one_id)
    
    return {
        "one_id": identity.one_id,
        "confidence": identity.confidence,
        "profile": profile
    }
```

### 5.2 身份归一

```python
def merge_identities(source_id: str, target_one_id: str, confidence: float):
    """
    合并身份到目标One-ID
    
    Args:
        source_id: 源身份记录ID
        target_one_id: 目标One-ID
        confidence: 本次合并置信度
    """
    # 1. 获取源身份
    source = db.identity_relation.get(source_id)
    
    # 2. 计算合并后置信度
    new_confidence = calculate_merge_confidence(
        target_one_id.confidence,
        confidence
    )
    
    # 3. 更新One-ID置信度
    db.one_id.update(
        one_id=target_one_id,
        confidence=new_confidence
    )
    
    # 4. 移动身份关系到目标One-ID
    db.identity_relation.update(
        id=source_id,
        one_id=target_one_id,
        merged_at=now()
    )
    
    # 5. 记录合并日志
    log_merge(source, target_one_id, confidence)
```

### 5.3 身份拆分

```python
def split_identity(identity_id: str, reason: str):
    """
    拆分误合并的身份
    
    Args:
        identity_id: 待拆分的身份记录ID
        reason: 拆分原因
    """
    # 1. 获取身份信息
    identity = db.identity_relation.get(identity_id)
    
    # 2. 检查One-ID下是否还有其他身份
    other_count = db.identity_relation.count(
        one_id=identity.one_id,
        status=1
    )
    
    if other_count <= 1:
        # 最后一个身份，One-ID保留但不关联此身份
        pass
    
    # 3. 更新身份状态
    db.identity_relation.update(
        id=identity_id,
        status=0,  # 标记为无效
        updated_at=now()
    )
    
    # 4. 记录拆分日志
    log_split(identity, reason)
```

## 6. API 接口

### 6.1 身份查询

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /identity/resolve` | POST | 通过标识查询 One-ID |

```json
// Request
{
  "identifier_type": "phone",
  "identifier_value": "13812345678"
}

// Response
{
  "code": 0,
  "data": {
    "one_id": "uuid-xxx-xxx",
    "confidence": 95.0,
    "is_new": false,
    "profile": {
      "total_orders": 15,
      "total_amount": 8500.00,
      "tags": ["时尚女性", "复购用户"]
    }
  }
}
```

### 6.2 身份合并

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /identity/merge` | POST | 手动合并身份 |

```json
// Request
{
  "source": {
    "channel": "douyin",
    "id_type": "openid",
    "id_value": "douyin_xxx"
  },
  "target_one_id": "uuid-xxx",
  "confidence": 75.0,
  "operator": "admin"
}
```

### 6.3 身份拆分

| 接口 | 方法 | 说明 |
|------|------|------|
| `POST /identity/split` | POST | 拆分误合并身份 |

```json
// Request
{
  "identity_id": 12345,
  "reason": "误合并，两个不同用户"
}
```

### 6.4 获取用户画像

| 接口 | 方法 | 说明 |
|------|------|------|
| `GET /identity/{one_id}/profile` | GET | 获取用户画像 |

```json
// Response
{
  "code": 0,
  "data": {
    "one_id": "uuid-xxx",
    "identities": [
      {"channel": "tmall", "id_type": "openid", "last_active": "2024-01-15"},
      {"channel": "douyin", "id_type": "openid", "last_active": "2024-01-14"}
    ],
    "profile": {
      "tags": ["时尚女性", "母婴用户"],
      "lifecycle": "复购用户",
      "total_orders": 15,
      "total_amount": 8500.00,
      "last_order_time": "2024-01-10"
    }
  }
}
```

## 7. 缓存设计

### 7.1 缓存策略

| 缓存类型 | Key 格式 | TTL | 说明 |
|----------|----------|-----|------|
| One-ID 查询 | `id:hash:{id_hash}` | 1小时 | 身份→One-ID 映射 |
| 画像缓存 | `profile:{one_id}` | 5分钟 | 用户画像缓存 |
| 批量查询 | `batch:resolve:{batch_hash}` | 10分钟 | 批量查询结果 |

### 7.2 缓存更新策略

```
读取:
  Cache → Hit → 返回
  Cache → Miss → DB查询 → 写入Cache → 返回

写入:
  DB写入 → 删除Cache相关Key → 异步重建Cache
```

## 8. 图计算优化

### 8.1 图查询优化

```cypher
// 查找与目标One-ID可能关联的身份
MATCH (i:Identity {id_hash: $hash})
MATCH (o:OneId)-[:HAS_IDENTITY]->(i)
RETURN o.one_id AS one_id, i.confidence AS confidence
ORDER BY confidence DESC
LIMIT 5
```

### 8.2 批量归一处理

```python
def batch_merge_identities(batch: List[dict]):
    """
    批量处理身份归一
    用于每日定时任务处理积压的身份
    """
    # 1. 批量获取待处理身份
    pending = get_pending_identities(limit=1000)
    
    # 2. 批量计算置信度
    for identity in pending:
        candidates = find_candidate_one_ids(identity)
        if candidates:
            best = max(candidates, key=lambda x: x.confidence)
            if best.confidence >= MERGE_THRESHOLD:
                merge_async(identity, best.one_id, best.confidence)
    
    # 3. 推送无法自动处理的到审核队列
    push_to_review_queue(unresolved)
```

## 9. 监控指标

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| query_latency_p99 | 查询延迟P99 | > 50ms |
| merge_success_rate | 自动归一成功率 | < 90% |
| pending_review_count | 待审核数量 | > 1000 |
| cache_hit_rate | 缓存命中率 | < 80% |
| graph_query_latency | 图查询延迟 | > 100ms |

## 10. 安全与合规

| 安全措施 | 说明 |
|----------|------|
| 数据脱敏 | 手机号等敏感信息脱敏存储 |
| 加密传输 | HTTPS + TLS 1.3 |
| 权限控制 | API 鉴权 + 操作审计 |
| 数据过期 | 长期不活跃身份自动归档 |
| 同意授权 | 仅处理已授权用户数据 |
