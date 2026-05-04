ALLOWED_RETRY_EXECUTION_RESULT_TYPES = {
    "retry_execution_result_v1",
}

ALLOWED_RETRY_OUTCOME_RECEIPT_TYPES = {
    "retry_outcome_receipt_v1",
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