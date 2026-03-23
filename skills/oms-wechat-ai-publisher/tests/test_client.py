"""
测试WeChatClient客户端模块
"""

import pytest
from scripts.auth import WeChatAuth
from scripts.client import WeChatClient


class TestWeChatClient:
    """测试WeChatClient类"""
    
    def test_init(self):
        """测试初始化"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        assert client.auth == auth
    
    def test_create_draft(self):
        """测试创建草稿"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        
        draft_id = client.create_draft(
            title="测试标题",
            body="<p>测试内容</p>",
            cover_url="https://example.com/cover.jpg"
        )
        
        assert isinstance(draft_id, str)
        assert draft_id == "draft_id_123"
    
    def test_publish_draft(self):
        """测试发布草稿"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        
        result = client.publish_draft("draft_id_123")
        
        assert isinstance(result, dict)
        assert "msg_id" in result
        assert result["msg_id"] == "12345"
    
    def test_update_draft(self):
        """测试更新草稿"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        
        success = client.update_draft(
            draft_id="draft_id_123",
            title="新标题",
            body="<p>新内容</p>",
            cover_url="https://example.com/new_cover.jpg"
        )
        
        assert success is True
    
    def test_get_draft(self):
        """测试获取草稿详情"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        
        draft = client.get_draft("draft_id_123")
        
        assert isinstance(draft, dict)
        assert "media_id" in draft
        assert "content" in draft
    
    def test_delete_draft(self):
        """测试删除草稿"""
        auth = WeChatAuth("app_id", "secret")
        client = WeChatClient(auth)
        
        success = client.delete_draft("draft_id_123")
        
        assert success is True
