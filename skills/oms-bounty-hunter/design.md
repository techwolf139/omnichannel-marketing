# 开源任务接单 - 详细设计

## 1. 系统架构

### 1.1 模块划分

```
oms-bounty-hunter/
├── bounty_finder.py      # 任务发现模块
├── proposal_writer.py    # 方案撰写模块
└── submitter.py          # PR提交模块
```

### 1.2 数据流

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  悬赏平台API    │────→│  BountyFinder   │────→│  任务列表       │
│  (GitHub等)     │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ↓
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GitHub PR API  │←────│  BountySubmitter│←────│  任务详情       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               ↑
                               │
┌─────────────────┐     ┌─────────────────┐
│  PR描述文本     │←────│ ProposalWriter  │
│                 │     │                 │
└─────────────────┘     └─────────────────┘
```

## 2. 数据模型

### 2.1 BountyTask

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| repo | str | 仓库全名 | "facebook/react" |
| issue_number | int | Issue编号 | 12345 |
| title | str | 任务标题 | "Fix memory leak in useEffect" |
| description | str | 任务描述 | Markdown格式 |
| reward | str | 奖励金额 | "$100" |
| currency | str | 币种 | "USD" / "ETH" / "BTC" |
| status | str | 状态 | open/assigned/completed/closed |
| labels | list[str] | 标签 | ["bounty", "good first issue"] |
| eligibility | list[str] | 资格要求 | ["CLA signed", "first-time contributor"] |
| deadline | datetime | 截止日期 | 2024-12-31 |
| assignee | str | 认领者 | "username" (可选) |
| skills_required | list[str] | 所需技能 | ["Python", "React"] |
| platform | str | 来源平台 | "github" / "algora" / "gitcoin" |
| url | str | 任务链接 | "https://github.com/..." |

### 2.2 BountyProposal

| 字段 | 类型 | 说明 |
|------|------|------|
| bounty | BountyTask | 关联的悬赏任务 |
| solution | str | 解决方案描述 |
| approach | str | 实现思路 |
| timeline | str | 预计时间线 |
| pr_number | int | 关联的PR编号 |
| status | str | draft/submitted/approved/rejected |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

### 2.3 SubmissionResult

| 字段 | 类型 | 说明 |
|------|------|------|
| pr_number | int | PR编号 |
| url | str | PR链接 |
| status | str | opened/closed/merged |
| submitted_at | datetime | 提交时间 |
| review_status | str | pending/approved/changes_requested |
| reviewer | str | 审核人 |

## 3. 模块设计

### 3.1 bounty_finder.py

**职责**: 从多个平台搜索和获取悬赏任务

**主要方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| find_bounties | keywords, reward_range, platform | list[BountyTask] | 搜索任务 |
| get_bounty_details | repo, issue_number | BountyTask | 获取详情 |
| search_github_issues | query, labels | list[dict] | GitHub搜索 |
| search_algora_tasks | keywords | list[dict] | Algora搜索 |
| parse_reward | title, body | dict | 解析奖励金额 |

**搜索策略**:

1. **GitHub Issues**: 搜索带 `bounty`, `reward`, `$` 等关键词的issue
2. **Algora**: 调用Algora API获取活跃任务
3. **Gitcoin**: 调用Gitcoin API (需key)

### 3.2 proposal_writer.py

**职责**: 生成专业的PR描述和解决方案提案

**主要方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| write_proposal | bounty, solution | str | 生成完整提案 |
| generate_pr_description | bounty, solution | str | 生成PR描述 |
| generate_implementation_plan | bounty | str | 生成实施计划 |

**PR描述模板**:

```markdown
## 解决方案

{solution_description}

## 实现思路

{implementation_approach}

## 变更内容

- [ ] 功能实现
- [ ] 单元测试
- [ ] 文档更新

## 测试

- [ ] 本地测试通过
- [ ] 所有现有测试通过

---
Closes #{issue_number}
```

### 3.3 submitter.py

**职责**: 提交PR并追踪状态

**主要方法**:

| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| submit_pr | repo, bounty, proposal | SubmissionResult | 提交PR |
| check_eligibility | repo, bounty | bool | 检查资格 |
| get_pr_status | repo, pr_number | dict | 获取PR状态 |
| claim_bounty | repo, issue_number | dict | 认领任务 |

**资格检查规则**:

1. 是否已签署CLA
2. 是否是首次贡献者限制
3. 是否已被其他人认领
4. 是否已过截止日期

## 4. 平台集成

### 4.1 GitHub API

**认证**: Personal Access Token

**核心端点**:
- `GET /search/issues` - 搜索悬赏issue
- `GET /repos/{owner}/{repo}/issues/{number}` - 获取issue详情
- `POST /repos/{owner}/{repo}/pulls` - 创建PR
- `GET /repos/{owner}/{repo}/pulls/{number}` - 获取PR状态

**限流**: 5000次/小时 (已认证)

### 4.2 Algora API (可选)

**认证**: API Key

**核心端点**:
- `GET /api/v1/bounties` - 获取悬赏列表
- `POST /api/v1/bounties/{id}/claim` - 认领任务

### 4.3 Gitcoin API (可选)

**认证**: API Key

**核心端点**:
- `GET /api/v0.1/bounties/` - 获取悬赏列表

## 5. 错误处理

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 401 | 认证失败 | 检查GITHUB_TOKEN |
| 403 | 限流 | 等待后重试 |
| 404 | 任务不存在 | 跳过该任务 |
| 422 | 参数错误 | 检查请求参数 |

## 6. MVP 暂不实现

| 功能 | 原因 |
|------|------|
| 自动代码提交 | MVP阶段手动提交更安全 |
| 多平台钱包集成 | 先专注GitHub原生悬赏 |
| 智能合约交互 | Web3功能后续迭代 |
| 实时通知推送 | 先使用轮询 |
| 历史数据分析 | 先实现核心功能 |

## 7. 安全注意事项

1. **Token安全**: GitHub Token应存储在环境变量，不要硬编码
2. **代码审查**: 自动提交代码前需人工审查
3. **权限控制**: Token仅需 `repo` 和 `read:user` 权限
4. **审计日志**: 记录所有PR提交操作
