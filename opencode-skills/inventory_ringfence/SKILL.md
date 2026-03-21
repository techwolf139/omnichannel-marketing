---
name: oms-inventory-ringfence
description: "Use when setting channel-exclusive inventory, protecting store stock during promotions, or managing store-as-warehouse operations. Triggers: set inventory isolation, protect store stock, enable store fulfillment, configure ringfence rules."
---

# 动态库存隔离与店仓一体化

## Overview

为各渠道动态圈定专属库存，大促期间自动保护线下门店安全库存。支持门店作为履约中心，赋予拣货、打包、发货的完整能力。

## When to Use

- 设置大促期间渠道专属库存
- 保护线下门店最低库存
- 启用门店履约能力
- 管理隔离规则

**触发词**: "库存隔离"、"保护库存"、"门店发货"、"店仓一体"、"Ring-fencing"

## Core Pattern

### 隔离场景 - 双11大促

| 时期 | 门店库存策略 |
|------|--------------|
| 平日 | 门店库存共享给天猫卖 |
| 双11当天 | 每款保留3件作为安全库存 |
| 大促结束 | 未售出库存释放给全渠道 |

### 隔离规则

```
RingfenceRule {
  scope: { sku_ids | category | tag },  // 适用范围
  ringfence_type: enum[percentage|fixed],
  ringfence_value: decimal,
  target_channel: string,
  time_range: {start, end}
}
```

### 隔离计算逻辑

```
可用库存 = 总库存 - 已隔离库存 - 已预占库存

订单占用时:
  1. 检查目标渠道是否有隔离规则
  2. 优先使用该渠道隔离库存
  3. 隔离库存不足，再从共享池扣减
```

## Quick Reference

### 店仓一体化流程

```
门店收到派单 → 店员接单 → 货架找货 → 扫码核验 → 打包 → 交接骑手
```

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 规则冲突 | 库存计算错误 | 优先级排序 |
| 隔离后库存不足 | 线下无货 | 合理设置安全库存 |
| 门店超配送半径 | 履约失败 | 切换到其他门店 |
