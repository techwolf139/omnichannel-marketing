"""
小红书开放平台 API 客户端
统一封装所有API调用
"""
import time
import requests
from typing import Optional, List, Dict, Any
from .auth import XHSAuth, XHSAPIError


class XHSClient:
    """
    小红书开放平台 API 客户端
    
    API文档: https://open.xiaohongshu.com/document/api
    """
    
    def __init__(self, auth: XHSAuth):
        self.auth = auth
    
    def _call(self, method: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> dict:
        """
        通用API调用
        
        Args:
            method: API方法名
            params: URL查询参数
            data: 请求体JSON数据
        
        Returns:
            API响应dict
        """
        self.auth.ensure_token_valid()
        
        headers = {"Authorization": f"Bearer {self.auth.access_token}"}
        url = f"{self.auth.host}/ark/open_api/v2/{method.replace('.', '/')}"
        
        response = requests.get(
            url, 
            params=params, 
            json=data, 
            headers=headers,
            timeout=30
        )
        
        result = response.json()
        
        if result.get("code") != 0:
            code = result.get("code", -1)
            msg = result.get("msg", "Unknown error")
            if code == 1003:
                self.auth.refresh_access_token()
                headers["Authorization"] = f"Bearer {self.auth.access_token}"
                response = requests.get(url, params=params, json=data, headers=headers, timeout=30)
                result = response.json()
            elif code == 1005:
                raise XHSAPIError(1005, "Rate limited, implement retry")
            else:
                raise XHSAPIError(code, msg)
        
        return result.get("data", {})
    
    # ========== 笔记数据 API ==========
    
    def note_exposure_get(self, note_id: str) -> dict:
        """
        获取笔记曝光数据
        
        Args:
            note_id: 笔记ID
        
        Returns:
            曝光数据 dict
        """
        return self._call(
            "note.exposure.get",
            params={"note_id": note_id}
        )
    
    def note_interaction_get(self, note_id: str) -> dict:
        """
        获取笔记互动数据（点赞/收藏/评论/分享）
        
        Args:
            note_id: 笔记ID
        
        Returns:
            互动数据 dict
        """
        return self._call(
            "note.interaction.get",
            params={"note_id": note_id}
        )
    
    def note_exposure_batch(self, note_ids: List[str]) -> List[dict]:
        """
        批量获取笔记曝光数据
        
        Args:
            note_ids: 笔记ID列表（最多50个）
        
        Returns:
            曝光数据列表
        """
        results = []
        for note_id in note_ids:
            try:
                data = self.note_exposure_get(note_id)
                results.append(data)
            except XHSAPIError as e:
                if e.code == 1005:
                    time.sleep(5)
                    data = self.note_exposure_get(note_id)
                    results.append(data)
                else:
                    raise
        return results
    
    # ========== KOL/蒲公英 API ==========
    
    def kol_order_list(self, page: int = 1, page_size: int = 20) -> dict:
        """
        获取蒲公英合作订单列表
        
        Args:
            page: 页码
            page_size: 每页数量（最大50）
        
        Returns:
            订单列表 dict
        """
        return self._call(
            "pugongyin.order.list",
            params={"page": page, "page_size": page_size}
        )
    
    def kol_order_detail(self, order_id: str) -> dict:
        """
        获取蒲公英合作订单详情
        
        Args:
            order_id: 合作单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "pugongyin.order.detail",
            params={"order_id": order_id}
        )
    
    # ========== 薯店订单 API ==========
    
    def shu_dian_order_search(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_state: Optional[int] = None,
        page: int = 1,
        page_size: int = 100
    ) -> dict:
        """
        搜索薯店订单
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            order_state: 订单状态 (1-待支付,2-已支付,3-已发货,4-已完成,5-已取消)
            page: 页码
            page_size: 每页数量
        
        Returns:
            订单列表 dict
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_state is not None:
            params["order_state"] = order_state
        
        return self._call("order.search", params=params)
    
    def shu_dian_order_detail(self, order_id: str) -> dict:
        """
        获取薯店订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "order.detail.get",
            params={"order_id": order_id}
        )
    
    # ========== 小程序订单 API ==========
    
    def mini_order_list(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order_state: Optional[int] = None,
        page: int = 1,
        page_size: int = 100
    ) -> dict:
        """
        获取小程序订单列表
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            order_state: 订单状态
            page: 页码
            page_size: 每页数量
        
        Returns:
            订单列表 dict
        """
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if order_state is not None:
            params["order_state"] = order_state
        
        return self._call("mini.order.list", params=params)
    
    def mini_order_detail(self, order_id: str) -> dict:
        """
        获取小程序订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情 dict
        """
        return self._call(
            "mini.order.detail",
            params={"order_id": order_id}
        )
