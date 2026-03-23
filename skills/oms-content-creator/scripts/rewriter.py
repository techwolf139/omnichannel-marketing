"""
内容改写器 - 适配不同平台风格
"""

import re
from typing import Dict


class ContentRewriter:
    """多平台内容改写器"""
    
    PLATFORM_LIMITS = {
        "wechat": 20000,      # 微信公众号
        "xiaohongshu": 1000,  # 小红书
        "zhihu": 10000,       # 知乎
        "weibo": 2000,        # 微博
        "twitter": 280,       # Twitter/X
        "douyin": 500,        # 抖音文案
    }
    
    PLATFORM_CONFIG = {
        "wechat": {
            "style": "depth",
            "features": ["paragraph", "insight", "cta"],
            "emoji": False,
            "paragraph_max_lines": 5,
        },
        "xiaohongshu": {
            "style": "casual",
            "features": ["emoji", "bullet", "tag"],
            "emoji": True,
            "tag_prefix": "#",
        },
        "zhihu": {
            "style": "professional",
            "features": ["logic", "data", "conclusion"],
            "emoji": False,
        },
        "weibo": {
            "style": "hot",
            "features": ["tag", "emoji", "short"],
            "emoji": True,
            "tag_prefix": "#",
        },
        "twitter": {
            "style": "concise",
            "features": ["short", "hashtag"],
            "emoji": True,
            "tag_prefix": "#",
        },
        "douyin": {
            "style": "hook",
            "features": ["hook", "emoji", "short"],
            "emoji": True,
        },
    }
    
    # 常用emoji映射
    EMOJI_MAP = {
        "good": "👍",
        "fire": "🔥",
        "star": "⭐",
        "heart": "❤️",
        "tip": "💡",
        "warning": "⚠️",
        "check": "✅",
        "rocket": "🚀",
        "gift": "🎁",
        "party": "🎉",
    }
    
    def __init__(self):
        """初始化改写器"""
        pass
    
    def _truncate_content(self, content: str, limit: int) -> str:
        """
        截断内容至指定长度
        
        Args:
            content: 原始内容
            limit: 字数限制
            
        Returns:
            截断后的内容
        """
        if len(content) <= limit:
            return content
        
        # 保留最后完整句子
        truncated = content[:limit-3]
        last_period = max(
            truncated.rfind("。"),
            truncated.rfind("！"),
            truncated.rfind("？"),
            truncated.rfind(".")
        )
        
        if last_period > limit * 0.8:  # 如果能在80%长度内找到句子结尾
            return truncated[:last_period+1]
        
        return truncated + "..."
    
    def _add_emoji_xiaohongshu(self, content: str) -> str:
        """为小红书内容添加emoji"""
        # 在开头添加
        content = f"{self.EMOJI_MAP['heart']} {content}"
        
        # 在关键位置添加
        content = content.replace("推荐", f"{self.EMOJI_MAP['star']}推荐")
        content = content.replace("注意", f"{self.EMOJI_MAP['warning']}注意")
        content = content.replace("技巧", f"{self.EMOJI_MAP['tip']}技巧")
        
        # 在结尾添加
        content = f"{content}\n\n{self.EMOJI_MAP['check']} 觉得有用记得收藏哦~"
        
        return content
    
    def _add_tags(self, content: str, platform: str) -> str:
        """添加话题标签"""
        config = self.PLATFORM_CONFIG.get(platform, {})
        prefix = config.get("tag_prefix", "#")
        
        # 提取关键词作为标签
        common_tags = {
            "wechat": [],  # 微信通常不加标签
            "xiaohongshu": ["好物分享", "实用技巧", "生活记录"],
            "zhihu": [],   # 知乎通常不加标签
            "weibo": ["好物推荐", "生活日常", "种草"],
            "twitter": ["Tips", "LifeHacks", "Recommendation"],
            "douyin": ["好物推荐", "实用分享"],
        }
        
        tags = common_tags.get(platform, [])
        if tags:
            tag_str = " ".join([f"{prefix}{tag}" for tag in tags[:3]])
            content = f"{content}\n\n{tag_str}"
        
        return content
    
    def _format_paragraphs(self, content: str, platform: str) -> str:
        """
        根据平台调整段落格式
        
        Args:
            content: 原始内容
            platform: 平台名称
            
        Returns:
            格式化后的内容
        """
        config = self.PLATFORM_CONFIG.get(platform, {})
        
        # 分割段落
        paragraphs = content.split('\n\n')
        formatted = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue
            
            # 小红书：短句分行
            if platform == "xiaohongshu":
                sentences = re.split(r'([。！？])', para)
                para = '\n'.join([s for s in sentences if s and s not in ['。', '！', '？']])
            
            # 微博：精简段落
            if platform == "weibo" and len(para) > 100:
                para = para[:100] + "..."
            
            formatted.append(para)
        
        return '\n\n'.join(formatted)
    
    def rewrite_for_platform(self, content: str, platform: str) -> str:
        """
        将内容改写为指定平台风格
        
        Args:
            content: 原始内容
            platform: 平台名称 (wechat|xiaohongshu|zhihu|weibo|twitter|douyin)
            
        Returns:
            改写后的内容
        """
        # 获取平台限制
        limit = self.PLATFORM_LIMITS.get(platform, 1000)
        config = self.PLATFORM_CONFIG.get(platform, {})
        
        buffer = 80 if platform in ["xiaohongshu", "weibo"] else 10
        effective_limit = max(limit - buffer, 50)
        
        # 1. 截断内容
        result = self._truncate_content(content, effective_limit)
        
        # 2. 调整段落格式
        result = self._format_paragraphs(result, platform)
        
        # 3. 添加emoji（如平台支持）
        if config.get("emoji"):
            if platform == "xiaohongshu":
                result = self._add_emoji_xiaohongshu(result)
            else:
                # 其他平台简单添加
                result = f"{self.EMOJI_MAP['fire']} {result}"
        
        # 4. 添加话题标签
        if "tag" in config.get("features", []):
            result = self._add_tags(result, platform)
        
        return result
    
    def get_platform_info(self, platform: str) -> Dict:
        """
        获取平台配置信息
        
        Args:
            platform: 平台名称
            
        Returns:
            平台配置字典
        """
        return {
            "name": platform,
            "limit": self.PLATFORM_LIMITS.get(platform, 1000),
            "config": self.PLATFORM_CONFIG.get(platform, {}),
        }
