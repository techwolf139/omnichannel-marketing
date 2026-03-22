from typing import Dict, Any, List, Optional
from datetime import datetime


class OrderAdapter:
    STATUS_MAP = {
        1: "CREATED",
        2: "PAID",
        3: "ALLOCATED",
        4: "PICKING",
        5: "SHIPPED",
        6: "DELIVERED",
        7: "CANCELLED",
        99: "CANCELLED"
    }

    def to_standard_order(self, jd_order: Dict) -> Dict[str, Any]:
        items = self._parse_items(jd_order.get("item_info_list", []))
        return {
            "order_id": jd_order.get("order_id", ""),
            "source_order_id": str(jd_order.get("jd_order_id", "")),
            "source_channel": "JD",
            "customer": {
                "one_id": jd_order.get("customer_id", ""),
                "phone": self._mask_phone(jd_order.get("consignee_mobile", "")),
                "member_level": jd_order.get("member_level", "NORMAL")
            },
            "items": items,
            "amounts": {
                "goods_amount": float(jd_order.get("order_payment", 0)),
                "shipping_fee": float(jd_order.get("freight_price", 0)),
                "discount_amount": float(jd_order.get("coupon_payment", 0)),
                "order_amount": float(jd_order.get("order_payment", 0))
            },
            "shipping": {
                "receiver_name": jd_order.get("consignee_name", ""),
                "phone": jd_order.get("consignee_mobile", ""),
                "address": jd_order.get("address_detail", "")
            },
            "status": self.STATUS_MAP.get(jd_order.get("order_state", 0), "UNKNOWN"),
            "created_at": jd_order.get("order_start_time", ""),
            "paid_at": jd_order.get("pay_time", "")
        }

    def _parse_items(self, item_list: List[Dict]) -> List[Dict]:
        items = []
        for item in item_list:
            items.append({
                "sku_id": item.get("sku_id", ""),
                "sku_name": item.get("ware_name", ""),
                "quantity": item.get("num", 1),
                "unit_price": float(item.get("price", 0)),
                "final_price": float(item.get("jd_price", item.get("price", 0)))
            })
        return items

    def _mask_phone(self, phone: str) -> str:
        if len(phone) == 11:
            return phone[:3] + "****" + phone[7:]
        return "****"

    def from_standard_order(self, standard_order: Dict) -> Dict:
        return {
            "order_id": standard_order.get("source_order_id", ""),
            "jd_order_id": standard_order.get("source_order_id", ""),
            "order_state": self._map_status_to_jd(standard_order.get("status", "")),
            "consignee_name": standard_order.get("shipping", {}).get("receiver_name", ""),
            "consignee_mobile": standard_order.get("shipping", {}).get("phone", ""),
            "address_detail": standard_order.get("shipping", {}).get("address", "")
        }

    def _map_status_to_jd(self, oms_status: str) -> int:
        reverse_map = {
            "CREATED": 1,
            "PAID": 2,
            "ALLOCATED": 3,
            "PICKING": 4,
            "SHIPPED": 5,
            "DELIVERED": 6,
            "CANCELLED": 7
        }
        return reverse_map.get(oms_status, 1)
