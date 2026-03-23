# 开源任务接单适配器 (oms-bounty-hunter)

GitHub悬赏任务发现和接单模块，支持任务搜索、方案撰写、PR提交全流程。

## 功能特性

- **任务发现**: 多平台悬赏任务聚合搜索
- **资格检查**: 自动验证接单资格
- **方案撰写**: 智能生成PR描述和解决方案
- **PR提交**: 一站式提交和状态追踪
- **奖励追踪**: 多币种奖励管理

## 目录结构

```
oms-bounty-hunter/
├── SKILL.md              # 技能定义
├── README.md             # 本文件
├── design.md             # 设计文档
├── scripts/
│   ├── __init__.py
│   ├── bounty_finder.py  # 悬赏任务发现
│   ├── proposal_writer.py # 方案撰写
│   └── submitter.py      # PR提交
└── tests/
    ├── __init__.py
    └── test_*.py          # 单元测试
```

## 快速开始

### 1. 配置GitHub Token

```python
import os
os.environ["GITHUB_TOKEN"] = "your_github_token"
```

### 2. 搜索悬赏任务

```python
from scripts.bounty_finder import BountyFinder

finder = BountyFinder()
bounties = finder.find_bounties(
    keywords=["python", "flask"],
    reward_range={"min": 50, "max": 500, "currency": "USD"}
)

for bounty in bounties:
    print(f"{bounty['repo']}#{bounty['issue_number']}: {bounty['title']}")
    print(f"  奖励: {bounty['reward']}")
```

### 3. 获取任务详情

```python
details = finder.get_bounty_details("owner/repo", 123)
print(f"描述: {details['description']}")
print(f"资格要求: {details['eligibility']}")
```

### 4. 检查接单资格

```python
from scripts.submitter import BountySubmitter

submitter = BountySubmitter()
eligible = submitter.check_eligibility("owner/repo", details)
print(f"有资格接单: {eligible}")
```

### 5. 撰写解决方案

```python
from scripts.proposal_writer import ProposalWriter

writer = ProposalWriter()
solution = """
我将通过以下步骤解决此问题:
1. 分析现有代码结构
2. 实现新功能模块
3. 添加单元测试
4. 更新文档
"""

proposal = writer.write_proposal(details, solution)
print(proposal)
```

### 6. 提交PR

```python
result = submitter.submit_pr("owner/repo", details, proposal)
print(f"PR已提交: {result['url']}")
```

## 环境变量

| 变量 | 说明 |
|------|------|
| GITHUB_TOKEN | GitHub个人访问令牌 |
| ALGORA_API_KEY | Algora平台API密钥 (可选) |
| GITCOIN_API_KEY | Gitcoin平台API密钥 (可选) |

## 支持的悬赏平台

| 平台 | 支持状态 | 说明 |
|------|----------|------|
| GitHub Issues | ✅ | 原生支持，通过标签识别 |
| Algora | ✅ | 需配置API密钥 |
| Gitcoin | ⚠️ | 部分支持 |
| Bountysource | ⚠️ | 部分支持 |

## 常用搜索关键词

| 类型 | 关键词示例 |
|------|-----------|
| 功能开发 | `feature`, `enhancement`, `new` |
| Bug修复 | `bug`, `fix`, `error` |
| 文档 | `documentation`, `docs`, `readme` |
| 性能 | `performance`, `optimize`, `speed` |
| 安全 | `security`, `vulnerability`, `cve` |

## 测试

```bash
cd skills/oms-bounty-hunter
python -m pytest tests/ -v
```
