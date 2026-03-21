# One-ID 归一与消费者画像融合 - 设计文档

## 1. 设计目标

实现全渠道消费者身份归一，打破线上线下数据孤岛，为精准营销和个性化服务提供基础数据能力。

## 2. 核心概念

### 2.1 身份标识类型

| 类型 | 说明 | 示例 |
|------|------|------|
| 原始标识 | 各渠道原生的唯一标识 | 天猫OpenID、抖音OpenID |
| 关联标识 | 需要关联后才能确定的标识 | 手机号、邮箱 |
| 归一标识 | 系统内的唯一超级ID | One-ID |

### 2.2 归一算法

**置信度评分机制**:

| 匹配因素 | 权重 | 说明 |
|----------|------|------|
| 手机号完全匹配 | 40% | 最高置信度 |
| 设备ID匹配 | 25% | 同一手机登录 |
| 收货地址重叠 | 20% | 相同收货人地址 |
| 行为特征相似 | 15% | 浏览/购买品类重叠 |

**归一决策**:
- 置信度 ≥ 90%: 自动归一
- 置信度 60%-90%: 需人工确认
- 置信度 < 60%: 不归一

## 3. 数据模型

### 3.1 核心实体

```
Consumer {
  one_id: string,           // 超级ID，UUID格式
  primary_identifier: {    // 主标识
    type: string,          // phone/openid/unionid
    value: string
  },
  identities: [{            // 所有关联身份
    channel: string,
    id_type: string,
    id_value: string,
    confidence: float,
    merged_at: datetime
  }],
  profile: {
    tags: [string],         // 偏好标签
    total_orders: int,
    total_amount: decimal
  },
  created_at: datetime,
  updated_at: datetime
}
```

## 4. 能力边界

### 4.1 支持的操作

- `resolve`: 通过任意标识查询One-ID
- `merge`: 手动合并两个身份
- `split`: 拆分误合并的身份
- `get_profile`: 获取完整消费者画像

### 4.2 限制说明

- 隐私合规：手机号需脱敏展示（138****8888）
- 数据延迟：归一结果有5分钟缓存
- 合规要求：不存储未经授权的身份信息

## 5. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| ID_NOT_FOUND | 标识不存在 | 返回空画像，提示新建 |
| MERGE_CONFLICT | 合并冲突 | 推送人工审核队列 |
| CHANNEL_API_ERROR | 渠道API异常 | 返回已归一数据，标记数据源异常 |
