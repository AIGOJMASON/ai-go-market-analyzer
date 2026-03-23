from __future__ import annotations

DELIVERY_RECEIPT_REGISTRY = {
    "runtime_delivery_receipt": {
        "type": "read_only_delivery_receipt",
        "allowed_delivery_index_types": [
            "runtime_delivery_index",
        ],
    }
}