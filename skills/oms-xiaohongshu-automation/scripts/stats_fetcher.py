"""小红书笔记数据统计器

提供笔记曝光和互动数据查询功能。
"""

from typing import Optional


class StatsFetcher:
    """小红书笔记数据统计器
    
    用于获取小红书笔记的曝光、互动等统计数据，支持批量查询和趋势分析。
    
    Attributes:
        client: 小红书API客户端实例
        adapter: 笔记数据适配器
    """
    
    def __init__(self, xhs_client=None, note_adapter=None):
        """初始化数据统计器
        
        Args:
            xhs_client: 可选，小红书API客户端
            note_adapter: 可选，笔记数据适配器
        """
        self.client = xhs_client
        self.adapter = note_adapter
    
    def get_note_stats(self, note_id: str) -> dict:
        """获取笔记统计数据
        
        获取指定笔记的曝光、点赞、收藏、评论等数据。
        
        Args:
            note_id: 笔记ID
            
        Returns:
            dict: 统计数据，包含:
                - note_id: 笔记ID
                - exposure: 曝光量
                - read: 阅读量
                - like: 点赞数
                - collect: 收藏数
                - comment: 评论数
                - share: 分享数
                - updated_at: 数据更新时间
                
        Raises:
            ValueError: 当note_id无效时
            
        Example:
            >>> fetcher = StatsFetcher()
            >>> stats = fetcher.get_note_stats("note_123456")
            >>> print(f"曝光: {stats['exposure']}, 点赞: {stats['like']}")
        """
        if not note_id or not isinstance(note_id, str):
            raise ValueError("Invalid note_id")
        
        # Mock implementation - 实际应调用小红书API
        return {
            "note_id": note_id,
            "exposure": 10000,
            "read": 5000,
            "like": 500,
            "collect": 200,
            "comment": 50,
            "share": 30,
            "updated_at": "2024-01-15T10:30:00Z"
        }
    
    def get_batch_stats(self, note_ids: list[str]) -> list[dict]:
        """批量获取笔记统计数据
        
        同时获取多个笔记的统计数据。
        
        Args:
            note_ids: 笔记ID列表，最多50个
            
        Returns:
            list[dict]: 统计数据列表
            
        Raises:
            ValueError: 当note_ids超过限制时
        """
        if len(note_ids) > 50:
            raise ValueError("Max 50 note_ids allowed for batch query")
        
        return [self.get_note_stats(note_id) for note_id in note_ids]
    
    def get_stats_trend(self, note_id: str, days: int = 7) -> list[dict]:
        """获取笔记数据趋势
        
        获取指定笔记在最近N天的数据变化趋势。
        
        Args:
            note_id: 笔记ID
            days: 查询天数，默认7天，最大30天
            
        Returns:
            list[dict]: 每日数据列表，每项包含:
                - date: 日期
                - exposure: 曝光增量
                - like: 点赞增量
                - comment: 评论增量
        """
        days = min(max(1, days), 30)
        
        # Mock trend data
        from datetime import datetime, timedelta
        
        base_stats = self.get_note_stats(note_id)
        trend = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-1-i)).strftime("%Y-%m-%d")
            trend.append({
                "date": date,
                "exposure": base_stats["exposure"] // days,
                "like": base_stats["like"] // days,
                "comment": base_stats["comment"] // days
            })
        
        return trend
    
    def get_account_stats(self, account_id: Optional[str] = None) -> dict:
        """获取账号整体数据
        
        获取账号的粉丝、总曝光、总互动等整体数据。
        
        Args:
            account_id: 账号ID，默认使用当前登录账号
            
        Returns:
            dict: 账号统计数据，包含:
                - account_id: 账号ID
                - followers: 粉丝数
                - total_notes: 笔记总数
                - total_exposure: 总曝光量
                - total_likes: 总点赞数
                - engagement_rate: 互动率
        """
        # Mock implementation
        return {
            "account_id": account_id or "default_account",
            "followers": 5000,
            "total_notes": 100,
            "total_exposure": 500000,
            "total_likes": 25000,
            "engagement_rate": 0.05
        }
    
    def calculate_engagement_rate(self, stats: dict) -> float:
        """计算互动率
        
        根据统计数据计算互动率 = (点赞+收藏+评论) / 曝光
        
        Args:
            stats: 统计数据字典
            
        Returns:
            float: 互动率，0-1之间
        """
        exposure = stats.get("exposure", 0)
        if exposure == 0:
            return 0.0
        
        engagement = (
            stats.get("like", 0) +
            stats.get("collect", 0) +
            stats.get("comment", 0)
        )
        
        return round(engagement / exposure, 4)
