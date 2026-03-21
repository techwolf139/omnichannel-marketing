# 动态库存隔离与店仓一体化 - 设计文档

## 1. 设计目标

实现灵活的库存隔离机制，在特定业务场景（如大促、渠道专属活动）下保护特定库存不被占用；同时赋能门店成为履约末端，形成店仓一体化的网络。

## 2. 核心概念

### 2.1 隔离规则

```
RingfenceRule {
  rule_id: string,
  name: string,
  
  scope: {
    sku_ids: [string] | category: string | tag: string,  // 适用范围
  },
  
  ringfence_type: enum[percentage|fixed|both],
  ringfence_value: decimal,        // 隔离数量/百分比
  
  target_channel: string,          // 隔离给哪个渠道
  
  priority: int,                   // 优先级（数字越大越优先）
  
  time_range: {start, end},
  
  status: enum[active|inactive]
}
```

### 2.2 隔离计算逻辑

```
可用库存 = 总库存 - 已隔离库存 - 已预占库存

当订单试图占用库存时:
  1. 检查目标渠道是否有隔离规则
  2. 如果有，优先使用该渠道隔离库存
  3. 如果隔离库存不足，再从共享池扣减
```

### 2.3 店仓能力配置

```
StoreCapability {
  store_id: string,
  fulfillment_types: [pickup, deliver],
  max_package_weight: decimal,     // 最大打包重量(kg)
  operating_hours: {open, close},
  delivery_radius: decimal,       // 配送半径(km)
  status: enum[active, inactive, suspended]
}
```

## 3. 核心能力

### 3.1 隔离规则管理

- 支持按SKU/品类/标签设置隔离
- 支持百分比和固定数量两种隔离方式
- 支持定时自动启用/失效

### 3.2 门店履约

- 门店接收OMS系统派单
- 支持PDA/手机APP操作
- 实时同步发货状态

## 4. 能力边界

### 4.1 支持的操作

- `set_ringfence`: 创建隔离规则
- `query_ringfence`: 查询隔离情况
- `release_ringfence`: 手动释放隔离
- `enable_store_fulfillment`: 启用门店履约
- `get_store_tasks`: 获取门店待处理任务

### 4.2 限制说明

- 同一SKU最多支持10条隔离规则
- 隔离规则变更需提前1小时生效
- 门店履约半径不超过10公里

## 5. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| RULE_CONFLICT | 规则冲突 | 返回冲突规则供选择 |
| STOCK_INSUFFICIENT | 隔离后库存不足 | 提示调整隔离量 |
| STORE_OFFLINE | 门店不在线 | 切换到其他门店 |
| RADIUS_EXCEEDED | 超出配送半径 | 提示扩大范围或换仓 |
