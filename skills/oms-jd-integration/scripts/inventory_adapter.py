from typing import Dict, Any
from .client import JDClient


class InventoryAdapter:
    def __init__(self, client: JDClient):
        self.client = client

    def sync_inventory(self, sku_id: str, quantity: int, shop_id: str = "") -> Dict[str, Any]:
        return self.client.inventory_update(sku_id, quantity, shop_id)

    def get_inventory(self, sku_id: str) -> Dict[str, Any]:
        return self.client.inventory_remain_get(sku_id)

    def to_standard_inventory(self, jd_inventory: Dict) -> Dict[str, Any]:
        return {
            "sku_id": jd_inventory.get("sku_id", ""),
            "available_quantity": jd_inventory.get("stock_num", 0),
            "locked_quantity": jd_inventory.get("lock_stock_num", 0),
            "channel": "JD",
            "updated_at": jd_inventory.get("update_time", "")
        }
