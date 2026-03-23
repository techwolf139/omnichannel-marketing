"""
解决方案提案撰写模块
生成专业的PR描述和解决方案
"""
from datetime import datetime


class ProposalWriter:
    """
    悬赏任务方案撰写器
    生成专业的PR描述和实现方案
    """
    
    # PR描述模板
    PR_TEMPLATE = """## 解决方案

{solution}

## 实现思路

{approach}

## 时间线

{timeline}

## 变更清单

- [ ] 核心功能实现
- [ ] 单元测试覆盖
- [ ] 集成测试
- [ ] 文档更新
- [ ] 代码审查

## 测试说明

- [ ] 本地开发环境测试通过
- [ ] 所有现有测试通过
- [ ] 新增测试用例覆盖新功能
- [ ] 边缘情况处理验证

## 相关链接

- 关联Issue: #{issue_number}
- 悬赏平台: {platform}

---

**声明**: 此PR用于响应悬赏任务，请维护者审核。

/cc @maintainers
"""
    
    def __init__(self):
        """初始化ProposalWriter"""
        pass
    
    def write_proposal(self, bounty: dict, solution: str) -> str:
        """
        撰写完整的解决方案提案
        
        Args:
            bounty: 悬赏任务信息
            solution: 解决方案描述
        
        Returns:
            str: 格式化的提案文本
        """
        approach = self._generate_approach(bounty)
        timeline = self._generate_timeline(bounty)
        
        return self.PR_TEMPLATE.format(
            solution=solution,
            approach=approach,
            timeline=timeline,
            issue_number=bounty.get("issue_number", 0),
            platform=bounty.get("platform", "GitHub")
        )
    
    def generate_pr_description(self, bounty: dict, solution: str) -> str:
        """
        生成PR描述
        
        Args:
            bounty: 悬赏任务信息
            solution: 解决方案描述
        
        Returns:
            str: PR描述文本
        """
        return self.write_proposal(bounty, solution)
    
    def generate_implementation_plan(self, bounty: dict) -> str:
        """
        生成实施计划
        
        Args:
            bounty: 悬赏任务信息
        
        Returns:
            str: 实施计划文本
        """
        title = bounty.get("title", "Task")
        skills = bounty.get("skills_required", [])
        
        plan = f"""# {title} - 实施计划

## 1. 需求分析

基于任务描述，分析核心需求：
- 理解业务场景
- 明确功能边界
- 识别技术难点

## 2. 技术方案

### 2.1 架构设计
- 模块划分
- 接口定义
- 数据流向

### 2.2 技术选型
"""
        
        if skills:
            plan += "\n所需技能:\n"
            for skill in skills:
                plan += f"- {skill}\n"
        
        plan += """
## 3. 开发步骤

### Phase 1: 基础准备
- [ ] 环境搭建
- [ ] 依赖安装
- [ ] 分支创建

### Phase 2: 核心实现
- [ ] 功能开发
- [ ] 单元测试
- [ ] 代码重构

### Phase 3: 集成验证
- [ ] 集成测试
- [ ] 性能测试
- [ ] 文档完善

## 4. 风险控制

| 风险点 | 影响 | 应对措施 |
|--------|------|----------|
| 技术难点 | 延期 | 提前调研，预留缓冲时间 |
| 需求变更 | 返工 | 与维护者充分沟通 |
| 测试覆盖 | 质量 | TDD开发，覆盖率>80% |

## 5. 验收标准

- [ ] 功能符合需求描述
- [ ] 代码通过审查
- [ ] 测试覆盖率达标
- [ ] 文档完整更新
"""
        
        return plan
    
    def _generate_approach(self, bounty: dict) -> str:
        """生成实现思路"""
        title = bounty.get("title", "")
        labels = bounty.get("labels", [])
        
        approach_parts = []
        
        # 根据标签判断类型
        if "bug" in labels or "fix" in labels:
            approach_parts.append("1. 复现问题，定位根因")
            approach_parts.append("2. 编写修复代码")
            approach_parts.append("3. 添加回归测试")
        elif "documentation" in labels or "docs" in labels:
            approach_parts.append("1. 梳理现有文档结构")
            approach_parts.append("2. 补充缺失内容")
            approach_parts.append("3. 优化表达清晰度")
        elif "enhancement" in labels or "feature" in labels:
            approach_parts.append("1. 分析现有架构")
            approach_parts.append("2. 设计新功能模块")
            approach_parts.append("3. 实现并集成测试")
        else:
            approach_parts.append("1. 理解任务需求")
            approach_parts.append("2. 设计解决方案")
            approach_parts.append("3. 编码实现")
            approach_parts.append("4. 测试验证")
        
        return "\n".join(f"{part}" for part in approach_parts)
    
    def _generate_timeline(self, bounty: dict) -> str:
        """生成时间线"""
        deadline = bounty.get("deadline")
        
        timeline = """| 阶段 | 预计时间 | 交付物 |
|------|----------|--------|
| 需求理解 | 1天 | 需求分析文档 |
| 方案设计 | 1-2天 | 技术方案 |
| 代码开发 | 2-5天 | 功能实现 |
| 测试验证 | 1-2天 | 测试报告 |
| PR提交 | 1天 | Pull Request |
"""
        
        if deadline:
            timeline += f"\n**截止日期**: {deadline}\n"
        
        return timeline
    
    def estimate_effort(self, bounty: dict) -> dict:
        """
        估算任务工作量
        
        Args:
            bounty: 悬赏任务信息
        
        Returns:
            dict: 工作量估算
        """
        labels = bounty.get("labels", [])
        title = bounty.get("title", "")
        
        # 根据标签和标题估算
        effort = {
            "difficulty": "medium",
            "estimated_days": 3,
            "skill_level": "intermediate"
        }
        
        # 难度判断
        if "good first issue" in labels:
            effort["difficulty"] = "easy"
            effort["estimated_days"] = 1
            effort["skill_level"] = "beginner"
        elif "complex" in labels or "hard" in labels:
            effort["difficulty"] = "hard"
            effort["estimated_days"] = 7
            effort["skill_level"] = "advanced"
        
        # 类型判断
        if "documentation" in labels:
            effort["estimated_days"] = max(1, effort["estimated_days"] - 1)
        elif "bug" in labels:
            effort["estimated_days"] = min(5, effort["estimated_days"] + 1)
        
        return effort
