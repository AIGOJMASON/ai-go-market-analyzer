ALLOWED_DELIVERY_OUTCOME_RECEIPT_TYPES = {
    "delivery_outcome_receipt_v1",
}

ALLOWED_FAILURE_RETRY_DECISION_TYPES = {
    "failure_retry_decision_v1",
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

ALLOWED_ADAPTER_CLASSES = {
    "manual_release_adapter",
    "gated_auto_release_adapter",
}

ALLOWED_OUTCOME_RESULTS = {
    "executed",
    "denied",
    "failed",
    "rejected",
}