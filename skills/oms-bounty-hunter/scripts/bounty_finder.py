"""
悬赏任务发现模块
支持从GitHub、Algora等平台搜索和获取悬赏任务
"""
import re
import os
from datetime import datetime
from typing import Optional


class BountyFinder:
    """
    悬赏任务发现器
    从多个平台搜索开源悬赏任务
    """
    
    # 悬赏相关标签
    BOUNTY_LABELS = ["bounty", "reward", "paid", "💰", "sponsored"]
    
    # 货币正则表达式
    REWARD_PATTERNS = [
        r'\$([\d,]+(?:\.\d{2})?)',  # $100, $1,000.50
        r'(\d+(?:\.\d+)?)\s*(USD|EUR|GBP)',  # 100 USD
        r'(\d+(?:\.\d+)?)\s*(ETH|BTC|USDC|USDT)',  # 0.5 ETH
        r'bounty[:\s]+\$?([\d,]+)',  # bounty: $100
        r'reward[:\s]+\$?([\d,]+)',  # reward: 100
    ]
    
    def __init__(self, github_token: str = None):
        """
        初始化BountyFinder
        
        Args:
            github_token: GitHub个人访问令牌，默认从环境变量获取
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN", "")
    
    def find_bounties(
        self, 
        keywords: list[str] = None, 
        reward_range: dict = None,
        platform: str = "github"
    ) -> list[dict]:
        """
        搜索悬赏任务
        
        Args:
            keywords: 搜索关键词列表，如 ["python", "flask"]
            reward_range: 奖励范围，如 {"min": 50, "max": 500, "currency": "USD"}
            platform: 平台名称，可选 "github", "algora", "all"
        
        Returns:
            list[dict]: 悬赏任务列表
        """
        bounties = []
        
        # 构建搜索查询
        query = self._build_search_query(keywords)
        
        if platform in ("github", "all"):
            github_bounties = self._search_github_bounties(query)
            bounties.extend(github_bounties)
        
        if platform in ("algora", "all"):
            algora_bounties = self._search_algora_bounties(keywords or [])
            bounties.extend(algora_bounties)
        
        # 按奖励范围过滤
        if reward_range:
            bounties = self._filter_by_reward(bounties, reward_range)
        
        return bounties
    
    def get_bounty_details(self, repo: str, issue_number: int) -> dict:
        """
        获取任务详情
        
        Args:
            repo: 仓库地址，格式 "owner/repo"
            issue_number: Issue编号
        
        Returns:
            dict: 任务详情
        """
        # 解析奖励信息
        reward_info = self._parse_reward_from_issue(f"Issue #{issue_number}", "")
        
        return {
            "repo": repo,
            "issue_number": issue_number,
            "title": f"Task for {repo}#{issue_number}",
            "description": f"Description for issue #{issue_number} in {repo}",
            "reward": reward_info.get("amount", "$100"),
            "currency": reward_info.get("currency", "USD"),
            "eligibility": ["open"],
            "status": "open",
            "labels": ["bounty"],
            "platform": "github",
            "url": f"https://github.com/{repo}/issues/{issue_number}",
            "deadline": None,
            "assignee": None,
            "skills_required": []
        }
    
    def _build_search_query(self, keywords: list[str] = None) -> str:
        """构建搜索查询字符串"""
        query_parts = keywords or []
        
        # 添加悬赏相关标签
        bounty_terms = ["bounty", "reward", "paid"]
        query_parts.extend(bounty_terms)
        
        # 构建查询
        query = " ".join(query_parts)
        query += " is:issue is:open label:bounty"
        
        return query
    
    def _search_github_bounties(self, query: str) -> list[dict]:
        """搜索GitHub上的悬赏任务"""
        # 模拟返回一些示例数据
        # 实际实现中会调用GitHub API
        return [
            {
                "repo": "example/python-project",
                "issue_number": 123,
                "title": "Add support for async operations",
                "reward": "$150",
                "currency": "USD",
                "status": "open",
                "labels": ["bounty", "enhancement", "good first issue"],
                "platform": "github",
                "url": "https://github.com/example/python-project/issues/123"
            },
            {
                "repo": "example/js-library",
                "issue_number": 456,
                "title": "Fix memory leak in component",
                "reward": "$200",
                "currency": "USD",
                "status": "open",
                "labels": ["bounty", "bug", "help wanted"],
                "platform": "github",
                "url": "https://github.com/example/js-library/issues/456"
            },
            {
                "repo": "example/docs-site",
                "issue_number": 789,
                "title": "Improve API documentation",
                "reward": "$100",
                "currency": "USD",
                "status": "open",
                "labels": ["bounty", "documentation"],
                "platform": "github",
                "url": "https://github.com/example/docs-site/issues/789"
            }
        ]
    
    def _search_algora_bounties(self, keywords: list[str]) -> list[dict]:
        """搜索Algora平台的悬赏任务"""
        # Algora API需要密钥
        api_key = os.environ.get("ALGORA_API_KEY")
        if not api_key:
            return []
        
        # 模拟返回
        return [
            {
                "repo": "algora/example",
                "issue_number": 1,
                "title": "Implement feature X",
                "reward": "0.5 ETH",
                "currency": "ETH",
                "status": "open",
                "labels": ["bounty"],
                "platform": "algora",
                "url": "https://algora.io/bounty/example/1"
            }
        ]
    
    def _filter_by_reward(self, bounties: list[dict], reward_range: dict) -> list[dict]:
        """按奖励范围过滤任务"""
        min_reward = reward_range.get("min", 0)
        max_reward = reward_range.get("max", float('inf'))
        target_currency = reward_range.get("currency", "USD")
        
        filtered = []
        for bounty in bounties:
            reward = bounty.get("reward", "$0")
            currency = bounty.get("currency", "USD")
            
            # 解析金额
            amount = self._parse_amount(reward)
            
            # 简单货币转换（实际应使用汇率API）
            if currency != target_currency:
                amount = self._convert_currency(amount, currency, target_currency)
            
            if min_reward <= amount <= max_reward:
                filtered.append(bounty)
        
        return filtered
    
    def _parse_reward_from_issue(self, title: str, body: str) -> dict:
        """从issue标题和正文解析奖励信息"""
        text = f"{title} {body}"
        
        for pattern in self.REWARD_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                currency = match.group(2) if len(match.groups()) > 1 else "USD"
                return {
                    "amount": f"${amount}" if currency == "USD" else f"{amount} {currency}",
                    "currency": currency.upper() if currency else "USD",
                    "raw": match.group(0)
                }
        
        return {"amount": "$0", "currency": "USD", "raw": None}
    
    def _parse_amount(self, reward_str: str) -> float:
        """解析奖励金额"""
        # 移除货币符号和逗号
        clean = re.sub(r'[^\d.]', '', reward_str)
        try:
            return float(clean) if clean else 0.0
        except ValueError:
            return 0.0
    
    def _convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """货币转换（简化版）"""
        # 简化汇率，实际应调用汇率API
        rates = {
            "USD": 1.0,
            "ETH": 3000.0,  # 假设 1 ETH = $3000
            "BTC": 60000.0,  # 假设 1 BTC = $60000
        }
        
        if from_currency in rates and to_currency in rates:
            usd_amount = amount * rates[from_currency]
            return usd_amount / rates[to_currency]
        
        return amount
