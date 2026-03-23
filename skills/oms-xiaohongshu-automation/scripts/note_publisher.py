"""小红书笔记发布器

提供笔记创建和发布功能，支持图文内容发布。
"""

from typing import Optional
from datetime import datetime


class NotePublisher:
    """小红书笔记发布器
    
    用于创建和发布小红书图文笔记，支持批量发布和定时发布。
    
    Attributes:
        client: 小红书API客户端实例
        default_location: 默认地理位置
    """
    
    # 图片限制
    MAX_IMAGES = 18
    MIN_IMAGES = 1
    MAX_TITLE_LENGTH = 20
    MAX_CONTENT_LENGTH = 1000
    
    def __init__(self, xhs_client=None, default_location: Optional[str] = None):
        """初始化笔记发布器
        
        Args:
            xhs_client: 可选，小红书API客户端
            default_location: 默认地理位置
        """
        self.client = xhs_client
        self.default_location = default_location
        self._drafts = {}  # 草稿存储
    
    def create_note(self, content: dict, images: list[str]) -> str:
        """创建笔记草稿
        
        创建一篇笔记草稿，不立即发布。可用于预览或定时发布。
        
        Args:
            content: 笔记内容，应包含:
                - title: 标题（必填，最多20字）
                - content: 正文内容（最多1000字）
                - topics: 话题标签列表（可选）
                - location: 地理位置（可选）
            images: 图片URL列表，至少1张，最多18张
            
        Returns:
            str: 笔记草稿ID
            
        Raises:
            ValueError: 当参数无效时
            
        Example:
            >>> publisher = NotePublisher()
            >>> content = {
            ...     "title": "今日穿搭分享",
            ...     "content": "今天分享一套春季穿搭...",
            ...     "topics": ["穿搭", "春季"]
            ... }
            >>> note_id = publisher.create_note(content, ["image1.jpg"])
        """
        # 参数校验
        if not content.get("title"):
            raise ValueError("Title is required")
        
        if len(content["title"]) > self.MAX_TITLE_LENGTH:
            raise ValueError(f"Title too long, max {self.MAX_TITLE_LENGTH} chars")
        
        if content.get("content") and len(content["content"]) > self.MAX_CONTENT_LENGTH:
            raise ValueError(f"Content too long, max {self.MAX_CONTENT_LENGTH} chars")
        
        if not images or len(images) < self.MIN_IMAGES:
            raise ValueError(f"At least {self.MIN_IMAGES} image required")
        
        if len(images) > self.MAX_IMAGES:
            raise ValueError(f"Max {self.MAX_IMAGES} images allowed")
        
        # 生成草稿ID (实际应调用API创建)
        note_id = f"note_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 存储草稿
        self._drafts[note_id] = {
            "note_id": note_id,
            "title": content["title"],
            "content": content.get("content", ""),
            "images": images,
            "topics": content.get("topics", []),
            "location": content.get("location", self.default_location),
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }
        
        return note_id
    
    def publish_note(self, note_id: str, scheduled_time: Optional[str] = None) -> dict:
        """发布笔记
        
        将草稿发布到小红书平台。支持定时发布。
        
        Args:
            note_id: 笔记草稿ID
            scheduled_time: 定时发布时间，ISO格式（可选）
            
        Returns:
            dict: 发布结果，包含:
                - status: 发布状态 ("published"/"scheduled"/"pending"/"failed")
                - note_id: 笔记ID
                - published_at: 发布时间（ISO格式）
                - url: 笔记链接
                
        Raises:
            ValueError: 当note_id不存在时
            
        Example:
            >>> publisher = NotePublisher()
            >>> note_id = publisher.create_note(content, images)
            >>> result = publisher.publish_note(note_id)
            >>> print(result["status"])  # "published"
        """
        if note_id not in self._drafts:
            raise ValueError(f"Note draft not found: {note_id}")
        
        draft = self._drafts[note_id]
        
        # 模拟发布
        result = {
            "status": "scheduled" if scheduled_time else "published",
            "note_id": note_id,
            "published_at": scheduled_time or datetime.now().isoformat(),
            "url": f"https://www.xiaohongshu.com/explore/{note_id}"
        }
        
        # 更新草稿状态
        draft["status"] = result["status"]
        draft["published_at"] = result["published_at"]
        
        return result
    
    def get_draft(self, note_id: str) -> Optional[dict]:
        """获取草稿详情
        
        Args:
            note_id: 笔记草稿ID
            
        Returns:
            dict: 草稿详情，不存在则返回None
        """
        return self._drafts.get(note_id)
    
    def delete_draft(self, note_id: str) -> bool:
        """删除草稿
        
        Args:
            note_id: 笔记草稿ID
            
        Returns:
            bool: 是否删除成功
        """
        if note_id in self._drafts:
            del self._drafts[note_id]
            return True
        return False
