# 全渠道对账与财务凭证 - 设计文档

## 1. 设计目标

构建全渠道、一体化的业财对账体系，解决多平台账单汇总难、差异定位慢、财务凭证生成效率低的问题。

## 2. 核心概念

### 2.1 对账类型

| 类型 | 说明 | 频率 |
|------|------|------|
| 日对账 | 每日核对前一日流水 | T+1 |
| 周对账 | 按周汇总核对 | 周一 |
| 月对账 | 月末结账前全面核对 | 月底 |

### 2.2 账单差异类型

| 类型 | 代码 | 说明 |
|------|------|------|
| 金额差异 | AMT_DIFF | 订单金额与账单不符 |
| 平台扣点差 | FEE_DIFF | 平台扣点与预估不符 |
| 退款未达 | REFUND_MISS | 退款未在账单体现 |
| 隐藏优惠 | HIDDEN_DISC | 平台额外优惠未记录 |

### 2.3 财务凭证模型

```
Voucher {
  voucher_id: string,
  voucher_no: string,           // 凭证号
  
  period: string,               // 会计期间
  business_date: date,
  
  lines: [{
    account_code: string,       // 科目编码
    account_name: string,      // 科目名称
    direction: enum[debit|credit],
    amount: decimal,
    summary: string            // 摘要
  }],
  
  attachments: [{
    type: string,
    file_url: string
  }],
  
  status: enum[draft|approved|posted],
  erp_sync_status: enum
}
```

### 2.4 凭证生成规则

```
收入确认凭证:
  借: 应收账款-平台  (订单金额)
  贷: 商品销售收入  (净额)
  贷: 应交增值税    (税额)

退款凭证:
  借: 商品销售收入  (退款金额，红字)
  贷: 应收账款-平台 (退款金额)

分润凭证:
  借: 销售费用-佣金  (分润金额)
  贷: 应付账款-门店  (应付门店)
```

## 3. 核心能力

### 3.1 账单接入

| 平台 | 接入方式 | 账单内容 |
|------|----------|----------|
| 天猫 | API拉取 | 订单收入、平台扣点、推广费 |
| 京东 | API拉取 | 货款、扣点、退款 |
| 抖音 | API拉取 | GMV、佣金、退款 |
| 微信支付 | API拉取 | 交易流水、手续费 |
| 支付宝 | API拉取 | 交易流水、服务费 |

### 3.2 差异处理

- 系统自动标记差异项
- 支持人工确认差异原因
- 差异分类统计输出报表

## 4. 能力边界

### 4.1 支持的操作

- `sync_bill`: 同步平台账单
- `reconcile`: 执行对账
- `query_diff`: 查询差异明细
- `generate_voucher`: 生成凭证
- `post_voucher`: 过账凭证
- `export_report`: 导出报表

### 4.2 限制说明

- 对账期间最多支持90天
- 单次凭证最多100条分录
- 已过账凭证不支持修改

## 5. 错误处理

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| BILL_SYNC_FAILED | 账单同步失败 | 记录错误，重试3次 |
| RECONCILE_TIMEOUT | 对账超时 | 分批处理 |
| VOUCHER_CONFLICT | 凭证生成冲突 | 检查重复生成 |
| ERP_CONNECTION_ERROR | ERP连接异常 | 标记待推送，人工跟进 |
