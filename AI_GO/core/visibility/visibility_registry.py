# AI_GO/core/visibility/visibility_registry.py

"""
VISIBILITY REGISTRY

Defines:
- allowed views
- required packet fields
- default windows
- prohibited fields
"""

REQUIRED_TOP_LEVEL_FIELDS = [
    "packet_type",
    "contract_version",
    "generated_at",
    "system_version",
    "visibility_mode",
    "generation_receipt",
    "summary",
    "runtime_view",
    "watcher_view",
    "smi_view",
    "external_memory_view",
    "inventory_view"
]

ALLOWED_VIEWS = [
    "summary",
    "runtime_view",
    "watcher_view",
    "smi_view",
    "receipt_view",
    "external_memory_view",
    "inventory_view",
    "pm_workflow_view",
    "canon_view"
]

DEFAULT_WINDOWS = {
    "receipts": 10,
    "watcher": 10,
    "smi": 10,
    "external_memory": 10
}

PROHIBITED_FIELDS = [
    "raw_files",
    "env_vars",
    "secrets",
    "full_logs",
    "unbounded_history"
]