import hashlib
import time
import requests
from typing import Dict, Any, Optional, List
from .auth import JDAuth, JDAPIError


class JDClient:
    def __init__(self, auth: JDAuth, timeout: int = 30):
        self.auth = auth
        self.timeout = timeout
        self.server_url = auth.server_url

    def _generate_sign(self, params: Dict) -> str:
        params_str = "".join([f"{k}{v}" for k, v in sorted(params.items())])
        sign_str = f"{self.auth.app_secret}{params_str}{self.auth.app_secret}"
        return hashlib.md5(sign_str.encode()).hexdigest().upper()

    def _call_api(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if params is None:
            params = {}

        if self.auth.is_token_expired():
            self.auth.refresh_access_token()

        common_params = {
            "app_key": self.auth.app_key,
            "access_token": self.auth.access_token,
            "method": method,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "v": "2.0",
            "sign_method": "md5"
        }
        all_params = {**common_params, **params}
        all_params["sign"] = self._generate_sign(all_params)

        try:
            response = requests.post(
                self.server_url,
                data=all_params,
                timeout=self.timeout
            )
            result = response.json()
            if result.get("error_code") or result.get("code") != 0:
                error_code = result.get("error_code", result.get("code", 0))
                error_msg = result.get("error_description", result.get("message", "Unknown error"))
                raise JDAPIError(error_code, error_msg)
            return result
        except requests.exceptions.Timeout:
            raise JDAPIError(1006, "Request timeout")
        except requests.exceptions.RequestException as e:
            raise JDAPIError(1000, f"Network error: {str(e)}")

    def order_search(
        self,
        start_date: str = "",
        end_date: str = "",
        order_state: int = 0,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "order_state": order_state,
            "page": page,
            "page_size": page_size
        }
        return self._call_api("jd.order.search", params)

    def order_detail_get(self, jd_order_id: str) -> Dict[str, Any]:
        params = {"jd_order_id": jd_order_id}
        return self._call_api("jd.order.detail.get", params)

    def order_track_search(self, jd_order_id: str) -> Dict[str, Any]:
        params = {"jd_order_id": jd_order_id}
        return self._call_api("jd.order.track.search", params)

    def sku_list(
        self,
        ware_id: str = "",
        sku_id: str = "",
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        params = {
            "ware_id": ware_id,
            "sku_id": sku_id,
            "page": page,
            "page_size": page_size
        }
        return self._call_api("jd.product.sku.list", params)

    def inventory_update(
        self,
        sku_id: str,
        stock_num: int,
        shop_id: str = ""
    ) -> Dict[str, Any]:
        params = {
            "sku_id": sku_id,
            "stock_num": stock_num,
            "shop_id": shop_id
        }
        return self._call_api("jd.ware.inventory.securable.update", params)

    def inventory_remain_get(self, sku_id: str) -> Dict[str, Any]:
        params = {"sku_id": sku_id}
        return self._call_api("jd.ware.inventory.remain.get", params)

    def logistics_order_search(self, jd_order_id: str) -> Dict[str, Any]:
        params = {"jd_order_id": jd_order_id}
        return self._call_api("jd.logistics.order.search", params)

    def return_order_apply(
        self,
        jd_order_id: str,
        sku_id: str,
        return_num: int,
        return_reason: str
    ) -> Dict[str, Any]:
        params = {
            "jd_order_id": jd_order_id,
            "sku_id": sku_id,
            "return_num": return_num,
            "return_reason": return_reason
        }
        return self._call_api("jd.returnorder.apply", params)

    def refund_order_info(self, jd_order_id: str) -> Dict[str, Any]:
        params = {"jd_order_id": jd_order_id}
        return self._call_api("jd.refund.order.info", params)
