import hashlib
import time
from typing import Dict, Optional
from datetime import datetime, timedelta


class JDAuth:
    def __init__(
        self,
        app_key: str,
        app_secret: str,
        access_token: str = "",
        refresh_token: str = "",
        token_expires_at: str = "",
        server_url: str = "https://api.jd.com/routerjson"
    ):
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = token_expires_at
        self.server_url = server_url

    def is_token_expired(self) -> bool:
        if not self.token_expires_at:
            return True
        try:
            expires = datetime.strptime(self.token_expires_at, "%Y-%m-%dT%H:%M:%SZ")
            return datetime.utcnow() >= expires - timedelta(minutes=10)
        except (ValueError, TypeError):
            return True

    def get_access_token(self) -> Dict:
        params = {
            "grant_type": "app_auth",
            "app_key": self.app_key,
            "app_secret": self.app_secret
        }
        sign = self._generate_sign(params)
        params["sign"] = sign
        return {"code": 0, "access_token": self.access_token}

    def refresh_access_token(self) -> Dict:
        params = {
            "grant_type": "refresh_token",
            "app_key": self.app_key,
            "refresh_token": self.refresh_token
        }
        sign = self._generate_sign(params)
        params["sign"] = sign
        return {"code": 0, "access_token": self.access_token}

    def _generate_sign(self, params: Dict) -> str:
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        param_str = "".join([f"{k}{v}" for k, v in sorted_params])
        sign_str = f"{self.app_secret}{param_str}{self.app_secret}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()


class JDAPIError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"JD API Error {code}: {message}")
