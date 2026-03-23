"""
测试WeChatAuth认证模块
"""

import pytest
from scripts.auth import WeChatAuth


class TestWeChatAuth:
    """测试WeChatAuth类"""
    
    def test_init(self):
        """测试初始化"""
        auth = WeChatAuth("app_id_123", "secret_456")
        assert auth.app_id == "app_id_123"
        assert auth.app_secret == "secret_456"
        assert auth._access_token is None
        assert auth._token_expires_at is None
    
    def test_get_access_token_returns_mock(self):
        """测试获取token返回mock值"""
        auth = WeChatAuth("app_id", "secret")
        token = auth.get_access_token()
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_refresh_access_token(self):
        """测试刷新token"""
        auth = WeChatAuth("app_id", "secret")
        token1 = auth.refresh_access_token()
        token2 = auth.refresh_access_token()
        
        # 两次刷新的token应该不同
        assert token1 != token2
        assert token1.startswith("mock_token_")
        assert token2.startswith("mock_token_")
    
    def test_get_access_token_caches_token(self):
        """测试token缓存"""
        auth = WeChatAuth("app_id", "secret")
        
        # 第一次获取会生成新token
        token1 = auth.get_access_token()
        # 未过期前应该返回相同token
        token2 = auth.get_access_token()
        
        assert token1 == token2
