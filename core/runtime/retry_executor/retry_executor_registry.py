ALLOWED_FAILURE_RETRY_DECISION_TYPES = {
    "failure_retry_decision_v1",
}

ALLOWED_RETRY_EXECUTION_RESULT_TYPES = {
    "retry_execution_result_v1",
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

RETRY_EXECUTION_MODE_TO_ADAPTER = {
    "manual_release": "manual_retry_adapter",
    "gated_auto_release": "gated_auto_retry_adapter",
}

ALLOWED_RETRY_ADAPTERS = {
    "manual_retry_adapter",
    "gated_auto_retry_adapter",
}

ROUTE_TO_ALLOWED_RETRY_ADAPTERS = {
    "internal_handoff": {
        "manual_retry_adapter",
        "gated_auto_retry_adapter",
    },
    "watcher_delivery": {
        "manual_retry_adapter",
        "gated_auto_retry_adapter",
    },
}