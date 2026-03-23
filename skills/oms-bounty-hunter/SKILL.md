---
name: oms-bounty-hunter
description: "Use when finding GitHub bounty tasks, writing proposals for open source projects, or submitting PRs for reward programs. Triggers: bounty hunting, GitHub issues with rewards, open source contributions, sponsored tasks, bug bounties."
---

# 开源任务接单适配器

## Overview

为开源贡献者提供一站式的GitHub悬赏任务接单服务。从发现任务、撰写方案到提交PR全流程支持，帮助开发者高效参与开源并获得奖励。

## When to Use

- 搜索GitHub悬赏任务
- 撰写解决方案提案
- 提交PR接单
- 检查任务资格
- 追踪接单状态

**触发词**: "GitHub悬赏", "开源任务", "接单赚钱", "Bounty", "悬赏任务"

## Core Pattern

### 任务搜索分类

| 类别 | 关键词 | 说明 |
|------|--------|------|
| 功能需求 | `enhancement`, `feature` | 新功能开发 |
| Bug修复 | `bug`, `fix` | 问题修复 |
| 文档优化 | `documentation`, `docs` | 文档改进 |
| 性能优化 | `performance`, `optimize` | 性能提升 |
| 安全修复 | `security`, `vulnerability` | 安全漏洞 |

### 常见悬赏平台

| 平台 | 悬赏类型 | 结算方式 |
|------|----------|----------|
| GitHub Issues | 项目自设悬赏 | 加密货币/PayPal |
| Algora | 任务赏金平台 | 加密货币 |
| Gitcoin | Web3任务平台 | 代币 |
| Bountysource | 传统赏金平台 | PayPal |

### 任务生命周期

```
发现任务 → 资格检查 → 方案撰写 → 代码实现 → 提交PR → 审核通过 → 领取奖励
```

## Implementation

### 数据模型

**BountyTask** (悬赏任务):
```python
{
    "repo": str,                    # 仓库地址 owner/repo
    "issue_number": int,            # Issue编号
    "title": str,                   # 任务标题
    "description": str,             # 任务描述
    "reward": str,                  # 奖励金额 (如 "$100"或"0.5 ETH")
    "currency": str,                # 币种 USD/ETH/BTC
    "status": str,                  # open/assigned/completed/closed
    "labels": list[str],            # 标签列表
    "eligibility": list[str],       # 参与资格要求
    "deadline": datetime,           # 截止日期
    "assignee": str,                # 当前认领者 (可选)
    "skills_required": list[str]    # 所需技能
}
```

**BountyProposal** (解决方案提案):
```python
{
    "bounty": BountyTask,           # 关联的任务
    "solution": str,                # 解决方案描述
    "approach": str,                # 实现思路
    "timeline": str,                # 预计时间线
    "pr_number": int,               # 关联的PR编号
    "status": str                   # draft/submitted/approved/rejected
}
```

**SubmissionResult** (提交结果):
```python
{
    "pr_number": int,               # PR编号
    "url": str,                     # PR链接
    "status": str,                  # 状态
    "submitted_at": datetime,       # 提交时间
    "review_status": str            # 审核状态
}
```

## Quick Reference

| 操作 | 方法 | 说明 |
|------|------|------|
| 搜索悬赏任务 | `find_bounties()` | 按关键词和奖励范围搜索 |
| 获取任务详情 | `get_bounty_details()` | 获取完整任务信息 |
| 检查资格 | `check_eligibility()` | 验证是否满足接单条件 |
| 撰写提案 | `write_proposal()` | 生成PR描述 |
| 提交PR | `submit_pr()` | 提交解决方案 |

## Common Mistakes

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 未检查资格要求 | PR被拒 | 先调用check_eligibility() |
| 忽略任务截止日期 | 过期提交 | 确认deadline后再接单 |
| 方案描述不清 | 审核缓慢 | 详细描述实现思路和时间线 |
| 同时接多个冲突任务 | 无法按时完成 | 合理评估时间和精力 |
| 未与维护者沟通 | 方案不符合预期 | 大改动前先讨论 |
