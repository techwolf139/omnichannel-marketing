from typing import Dict, Any, List
from .client import JDClient


class LogisticsAdapter:
    STATUS_MAP = {
        "ARRANGE": "SHIPPED",
        "DELIVERING": "IN_TRANSIT",
        "SIGN": "DELIVERED",
        "RETURN": "RETURNED"
    }

    def __init__(self, client: JDClient):
        self.client = client

    def search_logistics(self, jd_order_id: str) -> Dict[str, Any]:
        return self.client.logistics_order_search(jd_order_id)

    def to_standard_logistics(self, jd_logistics: Dict) -> Dict[str, Any]:
        return {
            "order_id": jd_logistics.get("order_id", ""),
            "tracking_number": jd_logistics.get("express_no", ""),
            "carrier_name": jd_logistics.get("express_name", ""),
            "status": self.STATUS_MAP.get(jd_logistics.get("state", ""), "UNKNOWN"),
            "shipped_at": jd_logistics.get("delivery_time", ""),
            "delivered_at": jd_logistics.get("sign_time", ""),
            "channel": "JD"
        }

    def parse_tracking_history(self, tracking_data: Dict) -> List[Dict]:
        history = []
        for item in tracking_data.get("tracking_list", []):
            history.append({
                "time": item.get("operate_time", ""),
                "status": item.get("operate_name", ""),
                "location": item.get("operate_Address", ""),
                "description": item.get("remark", "")
            })
        return history
