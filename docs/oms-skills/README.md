# OMS Skills 技能库总览

基于全渠道营销 OMS 系统概念设计文档，划分为5大业务阶段，共10个技能模块。

## 技能目录

| 阶段 | 技能目录 | 核心能力 |
|------|----------|----------|
| **Phase1** 全域触达与精准营销 | [one_id_merge](./one_id_merge/) | One-ID 归一与消费者画像融合 |
| | [promotion_engine](./promotion_engine/) | 跨场景促销规则引擎 |
| **Phase2** 统一订单捕获与智能路由 | [order_capture](./order_capture/) | 全渠道订单汇聚与清洗 |
| | [order_routing](./order_routing/) | 智能订单路由与拆合单 |
| **Phase3** 全局库存一盘货 | [inventory_realtime](./inventory_realtime/) | 库存水位实时映射与防超卖 |
| | [inventory_ringfence](./inventory_ringfence/) | 动态库存隔离与店仓一体化 |
| **Phase4** 无缝售后与全域服务 | [returns_crosschannel](./returns_crosschannel/) | 跨渠道退换货协同 |
| | [returns_logistics](./returns_logistics/) | 逆向物流与残次鉴定 |
| **Phase5** 跨渠道业财结算 | [profit_sharing](./profit_sharing/) | O2O利益分配与自动分润 |
| | [reconciliation](./reconciliation/) | 全渠道对账与财务凭证 |

---

## 技能索引

### Phase1 - 营销获客

#### one_id_merge
多渠道消费者身份融合，将碎片化画像归一为超级ID。

- **能力**: 多渠道身份识别、One-ID归一算法、消费者画像构建
- **调用示例**: 查询用户全渠道购买记录

#### promotion_engine
打通线上线下的促销规则引擎，支持积分、优惠券、赠品等玩法。

- **能力**: 促销规则配置、跨渠道规则匹配、券码发放
- **调用示例**: 发放定向优惠券给指定用户群

### Phase2 - 订单路由

#### order_capture
统一接入全网订单来源，标准化清洗后汇聚。

- **能力**: 多平台订单接入、订单标准化、黄牛/异常识别
- **调用示例**: 查询今日抖音渠道订单

#### order_routing
智能计算最优履约路径，支持订单拆分与合并。

- **能力**: 智能寻源、订单路由、拆合单决策
- **调用示例**: 查询订单履约路径和状态

### Phase3 - 库存管理

#### inventory_realtime
全网库存实时映射，防止超卖。

- **能力**: 多层级库存映射、实时可售发布、预扣减防超卖
- **调用示例**: 查询SKU可售库存

#### inventory_ringfence
动态隔离库存，赋能门店成为履约中心。

- **能力**: 动态库存隔离、安全库存保护、店仓一体化
- **调用示例**: 设置大促期间渠道专属库存

### Phase4 - 售后服务

#### returns_crosschannel
跨渠道退换货协同，Anywhere Return。

- **能力**: 跨渠道退换、自动状态冲销、业绩重新计算
- **调用示例**: 查询退货进度

#### returns_logistics
逆向物流追踪，残次鉴定，库存再流转。

- **能力**: 逆向物流追踪、残次鉴定分级、库存智能分流
- **调用示例**: 查询退货质检结果

### Phase5 - 财务结算

#### profit_sharing
O2O利益分配，自动分润结算。

- **能力**: 多维度业绩归属、自动分润结算、灵活规则配置
- **调用示例**: 查询订单分润明细

#### reconciliation
全渠道对账，生成财务凭证。

- **能力**: 账单汇集、自动对账、凭证生成
- **调用示例**: 生成月度对账报表

---

## 设计原则

1. **单一职责**: 每个 skill 只负责一个业务领域
2. **自然语言入口**: AI 解析用户指令，转换为 skill 调用
3. **幂等性**: 同一操作多次执行结果一致
4. **可编排**: 复杂流程可多个 skill 组合调用

## 文档结构

每个 skill 目录包含：

| 文件 | 说明 |
|------|------|
| `skill.md` | 技能定义：名称、能力描述、调用示例 |
| `design.md` | 设计文档：数据模型、核心概念、能力边界、错误处理 |
