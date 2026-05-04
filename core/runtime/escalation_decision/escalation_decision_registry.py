ALLOWED_SOURCE_RECEIPT_TYPES = {
    "delivery_outcome_receipt_v1",
    "retry_outcome_receipt_v1",
}

ALLOWED_ESCALATION_DECISION_TYPES = {
    "escalation_decision_v1",
}

ALLOWED_PAYLOAD_CLASSES = {
    "runtime_report_bundle",
    "watcher_report_package",
}

ALLOWED_ROUTE_CLASSES = {
    "internal_handoff",
    "watcher_delivery",
}

ALLOWED_EXECUTION_MODES = {
    "manual_release",
    "gated_auto_release",
}

ALLOWED_SOURCE_ADAPTER_CLASSES = {
    "manual_release_adapter",
    "gated_auto_release_adapter",
}

ALLOWED_RETRY_ADAPTER_CLASSES = {
    "manual_retry_adapter",
    "gated_auto_retry_adapter",
}

ALLOWED_ESCALATION_CLASSES = {
    "none",
    "retry_path",
    "operator_review",
    "policy_block",
}

ALLOWED_ESCALATION_ROUTES = {
    "none",
    "retry_governance",
    "operator_queue",
}