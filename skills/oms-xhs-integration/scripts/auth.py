"""
小红书开放平台认证模块
OAuth 2.0 + MD5签名
"""
import hashlib
import time
import requests
from datetime import datetime, timedelta
from typing import Optional


class XHSAPIError(Exception):
    """小红书API异常"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"[{code}] {message}")


class XHSAuth:
    """
    小红书 OAuth 2.0 认证
    文档: https://open.xiaohongshu.com/document/api
    """
    
    SANDBOX_HOST = "http://flssandbox.xiaohongshu.com"
    PROD_HOST = "https://ark.xiaohongshu.com"
    
    def __init__(self, app_id: str, app_secret: str, use_sandbox: bool = True):
        self.app_id = app_id
        self.app_secret = app_secret
        self.host = self.SANDBOX_HOST if use_sandbox else self.PROD_HOST
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def _generate_sign(self, params: dict) -> str:
        """
        生成MD5签名
        签名规则: md5(app_secret + key1 + value1 + key2 + value2 + ... + app_secret)
        按key字典序排列
        """
        sorted_keys = sorted(params.keys())
        sign_str = self.app_secret
        for key in sorted_keys:
            sign_str += str(key) + str(params[key])
        sign_str += self.app_secret
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
    
    def _build_common_params(self, method: str) -> dict:
        """构建通用参数"""
        timestamp = int(time.time() * 1000)
        return {
            "appId": self.app_id,
            "method": method,
            "timestamp": timestamp,
            "version": "2.0"
        }
    
    def get_access_token(self, code: str) -> dict:
        """
        用授权码换取access_token
        code: OAuth授权码（有效期10分钟）
        """
        params = self._build_common_params("oauth.getAccessToken")
        params["code"] = code
        params["sign"] = self._generate_sign(params)
        
        url = f"{self.host}/ark/open_api/v3/common_controller"
        response = requests.post(url, json=params, timeout=30)
        result = response.json()
        
        if result.get("code") != 0:
            raise XHSAPIError(result.get("code", -1), result.get("msg", "Unknown error"))
        
        data = result["data"]
        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken")
        self.token_expires_at = datetime.now() + timedelta(seconds=data.get("expiresIn", 7200))
        
        return data
    
    def refresh_access_token(self) -> dict:
        """
        刷新access_token
        """
        params = self._build_common_params("oauth.refreshToken")
        params["refreshToken"] = self.refresh_token
        params["sign"] = self._generate_sign(params)
        
        url = f"{self.host}/ark/open_api/v3/common_controller"
        response = requests.post(url, json=params, timeout=30)
        result = response.json()
        
        if result.get("code") != 0:
            raise XHSAPIError(result.get("code", -1), result.get("msg", "Unknown error"))
        
        data = result["data"]
        self.access_token = data["accessToken"]
        self.refresh_token = data.get("refreshToken")
        self.token_expires_at = datetime.now() + timedelta(seconds=data.get("expiresIn", 7200))
        
        return data
    
    def ensure_token_valid(self) -> str:
        """确保token有效，过期则自动刷新"""
        if not self.access_token:
            raise XHSAPIError(1003, "Not authenticated, call get_access_token first")
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            self.refresh_access_token()
        
        return self.access_token
    
    def is_token_expired(self) -> bool:
        """检查token是否过期"""
        if not self.token_expires_at:
            return True
        return datetime.now() >= self.token_expires_at
