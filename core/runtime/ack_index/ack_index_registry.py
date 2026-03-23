from __future__ import annotations

ACK_INDEX_REGISTRY = {
    "runtime_ack_index": {
        "type": "read_only_ack_index",
        "allowed_delivery_receipt_types": [
            "runtime_delivery_receipt",
        ],
    }
}