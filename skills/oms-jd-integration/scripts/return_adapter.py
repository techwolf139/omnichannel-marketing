from typing import Dict, Any
from .client import JDClient


class ReturnAdapter:
    STATUS_MAP = {
        "APPLIED": "RETURN_REQUEST",
        "APPROVED": "RETURN_APPROVED",
        "SHIPPED": "RETURN_SHIPPED",
        "RECEIVED": "RETURN_RECEIVED",
        "REFUNDED": "REFUNDED",
        "REJECTED": "RETURN_REJECTED"
    }

    def __init__(self, client: JDClient):
        self.client = client

    def apply_return(
        self,
        jd_order_id: str,
        sku_id: str,
        return_num: int,
        return_reason: str
    ) -> Dict[str, Any]:
        return self.client.return_order_apply(
            jd_order_id, sku_id, return_num, return_reason
        )

    def query_refund(self, jd_order_id: str) -> Dict[str, Any]:
        return self.client.refund_order_info(jd_order_id)

    def to_standard_return(self, jd_return: Dict) -> Dict[str, Any]:
        return {
            "return_id": jd_return.get("return_id", ""),
            "order_id": jd_return.get("jd_order_id", ""),
            "sku_id": jd_return.get("sku_id", ""),
            "quantity": jd_return.get("return_num", 0),
            "status": self.STATUS_MAP.get(jd_return.get("status", ""), "UNKNOWN"),
            "reason": jd_return.get("return_reason", ""),
            "refund_amount": jd_return.get("refund_amount", 0),
            "applied_at": jd_return.get("apply_time", ""),
            "channel": "JD"
        }
