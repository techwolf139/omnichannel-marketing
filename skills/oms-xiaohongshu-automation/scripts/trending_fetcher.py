"""小红书热点话题采集器

提供热点话题实时采集功能，支持分类筛选和排序。
"""

from typing import Optional


class TrendingFetcher:
    """小红书热点话题采集器
    
    用于获取小红书平台上的热门话题，支持按分类筛选和数量限制。
    
    Attributes:
        api_client: 小红书API客户端实例
        base_url: API基础地址
    """
    
    # 支持的话题分类
    VALID_CATEGORIES = ["all", "beauty", "fashion", "food", "travel", 
                        "home", "tech", "fitness", "entertainment"]
    
    def __init__(self, api_client=None, base_url: str = "https://open.xiaohongshu.com"):
        """初始化热点采集器
        
        Args:
            api_client: 可选，小红书API客户端
            base_url: API基础地址
        """
        self.api_client = api_client
        self.base_url = base_url
    
    def fetch_trending_topics(self, category: str = "all", limit: int = 20) -> list[dict]:
        """获取热门话题列表
        
        获取指定分类下的热门话题，按热度排序返回。
        
        Args:
            category: 话题分类，可选值: all, beauty, fashion, food, travel,
                     home, tech, fitness, entertainment
            limit: 返回数量限制，默认20，最大100
            
        Returns:
            list[dict]: 话题列表，每项包含:
                - topic: 话题名称
                - heat: 热度值
                - category: 分类
                - rank: 排名
                - trend: 趋势(rising/stable/declining)
                
        Raises:
            ValueError: 当category参数无效时
            
        Example:
            >>> fetcher = TrendingFetcher()
            >>> topics = fetcher.fetch_trending_topics(category="fashion", limit=10)
            >>> print(topics[0])
            {
                "topic": "春季穿搭",
                "heat": 1000000,
                "category": "穿搭",
                "rank": 1,
                "trend": "rising"
            }
        """
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category: {category}. "
                f"Must be one of {self.VALID_CATEGORIES}"
            )
        
        limit = min(max(1, limit), 100)  # 限制1-100
        
        # Mock implementation - 实际应调用小红书API
        mock_topics = [
            {
                "topic": "热门话题",
                "heat": 1000000,
                "category": "美妆",
                "rank": 1,
                "trend": "rising"
            },
            {
                "topic": "春季穿搭",
                "heat": 850000,
                "category": "穿搭",
                "rank": 2,
                "trend": "stable"
            },
            {
                "topic": "美食探店",
                "heat": 720000,
                "category": "美食",
                "rank": 3,
                "trend": "rising"
            }
        ]
        
        # 根据分类筛选
        if category != "all":
            category_map = {
                "beauty": "美妆",
                "fashion": "穿搭",
                "food": "美食",
                "travel": "旅行"
            }
            target_cat = category_map.get(category, category)
            mock_topics = [
                t for t in mock_topics 
                if t["category"] == target_cat or category == "all"
            ]
        
        return mock_topics[:limit]
    
    def get_topic_detail(self, topic: str) -> dict:
        """获取话题详情
        
        获取指定话题的详细信息，包括热度趋势、相关笔记数等。
        
        Args:
            topic: 话题名称
            
        Returns:
            dict: 话题详情，包含:
                - topic: 话题名称
                - heat: 当前热度
                - note_count: 相关笔记数
                - participant_count: 参与人数
                - trend_7d: 7天热度趋势列表
        """
        # Mock implementation
        return {
            "topic": topic,
            "heat": 1000000,
            "note_count": 50000,
            "participant_count": 12000,
            "trend_7d": [800000, 850000, 900000, 950000, 980000, 1000000, 1000000]
        }
