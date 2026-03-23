from __future__ import annotations

DELIVERY_INDEX_REGISTRY = {
    "runtime_delivery_index": {
        "type": "read_only_delivery_index",
        "allowed_dispatch_manifest_types": [
            "runtime_dispatch_manifest",
        ],
    }
}