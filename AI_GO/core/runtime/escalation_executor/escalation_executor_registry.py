ALLOWED_ESCALATION_DECISION_TYPES = {
    "escalation_decision_v1",
}

ALLOWED_ESCALATION_EXECUTION_RESULT_TYPES = {
    "escalation_execution_result_v1",
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
    "none",
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

ESCALATION_ROUTE_TO_ADAPTER = {
    "retry_governance": "retry_governance_escalation_adapter",
    "operator_queue": "operator_queue_escalation_adapter",
    "none": "none",
}

ALLOWED_ESCALATION_ADAPTERS = {
    "none",
    "retry_governance_escalation_adapter",
    "operator_queue_escalation_adapter",
}