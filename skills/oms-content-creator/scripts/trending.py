"""
热点匹配器 - 匹配热门话题
"""

from typing import List, Dict, Any
import re


class TrendingMatcher:
    """热门话题匹配器"""
    
    # 模拟热门话题数据
    MOCK_TRENDING_TOPICS = [
        {"id": "1", "name": "双十一攻略", "category": "购物", "heat_score": 0.95},
        {"id": "2", "name": "秋冬护肤", "category": "美妆", "heat_score": 0.88},
        {"id": "3", "name": "省钱技巧", "category": "生活", "heat_score": 0.82},
        {"id": "4", "name": "职场穿搭", "category": "时尚", "heat_score": 0.79},
        {"id": "5", "name": "健康减脂", "category": "健康", "heat_score": 0.85},
        {"id": "6", "name": "智能家居", "category": "科技", "heat_score": 0.76},
        {"id": "7", "name": "旅行打卡", "category": "旅行", "heat_score": 0.91},
        {"id": "8", "name": "母婴好物", "category": "母婴", "heat_score": 0.83},
    ]
    
    def __init__(self):
        """初始化热点匹配器"""
        pass
    
    def _extract_keywords(self, content: str) -> List[str]:
        """
        从内容中提取关键词
        
        Args:
            content: 内容文本
            
        Returns:
            关键词列表
        """
        # 简单实现：提取2-4个字的词作为关键词
        # 实际应用中可以使用NLP库如jieba
        words = re.findall(r'[\u4e00-\u9fa5]{2,6}', content)
        return list(set(words))[:10]  # 返回前10个不重复词
    
    def _calculate_relevance(self, content: str, topic: Dict[str, Any]) -> float:
        """
        计算内容与话题的相关度
        
        Args:
            content: 内容文本
            topic: 话题数据
            
        Returns:
            相关度分数(0-1)
        """
        topic_name = topic["name"]
        category = topic["category"]
        
        # 简单实现：检查话题名是否在内容中
        score = 0.0
        if topic_name in content:
            score += 0.5
        if category in content:
            score += 0.3
        
        # 检查关键词匹配
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            if keyword in topic_name or keyword in category:
                score += 0.05
        
        return min(score, 1.0)
    
    def match_trending_topics(self, content: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        匹配与内容相关的热门话题
        
        Args:
            content: 内容文本
            top_n: 返回前N个匹配结果
            
        Returns:
            匹配的话题列表，包含相关度分数
        """
        results = []
        
        for topic in self.MOCK_TRENDING_TOPICS:
            relevance = self._calculate_relevance(content, topic)
            if relevance > 0.1:  # 只返回相关度大于0.1的
                results.append({
                    "id": topic["id"],
                    "topic": topic["name"],
                    "category": topic["category"],
                    "heat_score": topic["heat_score"],
                    "relevance_score": round(relevance, 2)
                })
        
        # 按综合得分排序（热度*相关度）
        results.sort(key=lambda x: x["heat_score"] * x["relevance_score"], reverse=True)
        
        return results[:top_n]
    
    def fetch_platform_trending(self, platform: str, category: str = "all") -> List[Dict[str, Any]]:
        """
        获取平台热门话题列表
        
        Args:
            platform: 平台名称 (weibo|zhihu|xiaohongshu|douyin)
            category: 分类筛选
            
        Returns:
            热门话题列表
        """
        # 模拟从平台API获取数据
        # 实际应用中应调用各平台开放接口
        
        topics = self.MOCK_TRENDING_TOPICS.copy()
        
        # 按分类筛选
        if category != "all":
            topics = [t for t in topics if t["category"] == category]
        
        # 添加平台信息
        for topic in topics:
            topic["platform"] = platform
        
        # 按热度排序
        topics.sort(key=lambda x: x["heat_score"], reverse=True)
        
        return topics[:10]  # 返回前10条
