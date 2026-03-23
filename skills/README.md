# OMS Skills 技能库

全渠道营销 OMS 系统 AI Agent 技能集合，遵循 OpenCode Skill 格式规范。

## 技能列表

| Skill | 名称 | 适用场景 |
|-------|------|----------|
| `oms-content-creator` | 爆款文案生成引擎 | 标题生成、正文创作、脚本生成、热点匹配、多平台改写 |
| `oms-wechat-ai-publisher` | 微信公众号自动发文 | 写稿排版、封面生成、草稿管理、定时发布 |
| `oms-xiaohongshu-automation` | 小红书自动化 | 热点采集、笔记发布、数据查看 |
| `oms-social-media-auto` | 全平台分发适配器 | 知乎/微博/小红书/X一键同步 |
| `oms-bounty-hunter` | 开源任务接单 | GitHub悬赏任务、方案撰写、PR提交 |
| `oms-jd-integration` | 京东开放平台集成 | 京东订单同步、库存管理、物流追踪、退货处理 |
| `oms-xhs-integration` | 小红书开放平台集成 | 笔记曝光数据、KOL合作管理、薯店/小程序订单、UTM归因 |
| `oms-one-id-merge` | One-ID 归一与消费者画像融合 | 跨渠道身份识别、消费者画像查询 |
| `oms-promotion-engine` | 跨场景促销规则引擎 | 创建促销、发放优惠券、积分管理 |
| `oms-order-capture` | 全渠道订单汇聚与清洗 | 多平台订单查询、异常订单识别 |
| `oms-order-routing` | 智能订单路由与拆合单 | 订单分配、履约路径计算 |
| `oms-inventory-realtime` | 库存水位实时映射与防超卖 | 库存查询、预占管理、超卖防护 |
| `oms-inventory-ringfence` | 动态库存隔离与店仓一体化 | 渠道库存隔离、门店履约 |
| `oms-returns-crosschannel` | 跨渠道退换货协同 | Anywhere Return、退换货申请 |
| `oms-returns-logistics` | 逆向物流与残次鉴定 | 退货追踪、质检、库存再流转 |
| `oms-profit-sharing` | O2O利益分配与自动分润 | 分润计算、佣金结算 |
| `oms-reconciliation` | 全渠道对账与财务凭证 | 对账报表、凭证生成 |

## 业务阶段映射

```
Phase0 平台对接     → oms-jd-integration, oms-xhs-integration
Phase1 营销获客     → oms-content-creator, oms-wechat-ai-publisher, oms-xiaohongshu-automation, oms-social-media-auto, oms-one-id-merge, oms-promotion-engine
Phase2 订单路由     → oms-order-capture, oms-order-routing
Phase3 库存管理     → oms-inventory-realtime, oms-inventory-ringfence
Phase4 售后服务     → oms-returns-crosschannel, oms-returns-logistics
Phase5 财务结算     → oms-profit-sharing, oms-reconciliation
Phase6 价值变现     → oms-bounty-hunter
```

## 设计文档

详细设计文档位于: `./docs/oms-skills/`

每个 skill 包含:
- `SKILL.md` - OpenCode 技能定义
- `design.md` - 详细设计文档

## 使用方式

在 OpenCode 中，当用户询问相关业务问题时，AI Agent 会自动加载对应 skill。

**触发示例**:
- "帮我写一个爆款标题" → 加载 `oms-content-creator`
- "生成小红书风格的文案" → 加载 `oms-content-creator`
- "发布微信公众号文章" → 加载 `oms-wechat-ai-publisher`
- "同步内容到微博和知乎" → 加载 `oms-social-media-auto`
- "搜索GitHub悬赏任务" → 加载 `oms-bounty-hunter`
- "查询京东订单状态" → 加载 `oms-jd-integration`
- "同步小红书薯店订单" → 加载 `oms-xhs-integration`
- "查一下手机号138****8888的消费者画像" → 加载 `oms-one-id-merge`
- "帮我创建一个大促优惠券" → 加载 `oms-promotion-engine`
- "查一下订单A123456的履约路径" → 加载 `oms-order-routing`
