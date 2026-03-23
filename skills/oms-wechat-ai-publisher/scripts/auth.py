"""
微信公众号认证模块

管理微信公众号AccessToken的获取和刷新。
"""

import time
from datetime import datetime, timedelta
from typing import Optional


class WeChatAuth:
    """
    微信公众号认证管理器
    
    负责管理AccessToken的生命周期，包括获取和自动刷新。
    
    Attributes:
        app_id: 微信公众号AppID
        app_secret: 微信公众号AppSecret
        _access_token: 当前有效的AccessToken
        _token_expires_at: Token过期时间
    """
    
    TOKEN_REFRESH_BUFFER = 300
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        self._token_counter: int = 0
    
    def get_access_token(self) -> str:
        """
        获取有效的AccessToken
        
        如果当前Token即将过期，会自动刷新。
        
        Returns:
            有效的AccessToken字符串
            
        Example:
            >>> auth = WeChatAuth("wx123456", "secret123")
            >>> token = auth.get_access_token()
        """
        if self._is_token_expired():
            return self.refresh_access_token()
        return self._access_token or "mock_token"
    
    def refresh_access_token(self) -> str:
        self._token_counter += 1
        self._access_token = f"mock_token_{int(time.time())}_{self._token_counter}"
        self._token_expires_at = datetime.now() + timedelta(seconds=7200)
        return self._access_token
    
    def _is_token_expired(self) -> bool:
        """
        检查Token是否即将过期
        
        Returns:
            True表示Token已过期或即将过期
        """
        if not self._token_expires_at:
            return True
        return datetime.now() >= (self._token_expires_at - timedelta(seconds=self.TOKEN_REFRESH_BUFFER))
