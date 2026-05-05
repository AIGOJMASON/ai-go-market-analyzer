ALLOWED_TRANSPORT_ENVELOPE_TYPES = {
    "delivery_transport_envelope_v1",
}

ALLOWED_EXECUTION_RESULT_TYPES = {
    "transport_execution_result_v1",
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

EXECUTION_MODE_TO_ADAPTER = {
    "manual_release": "manual_release_adapter",
    "gated_auto_release": "gated_auto_release_adapter",
}

ROUTE_TO_ALLOWED_ADAPTERS = {
    "internal_handoff": {
        "manual_release_adapter",
        "gated_auto_release_adapter",
    },
    "watcher_delivery": {
        "manual_release_adapter",
        "gated_auto_release_adapter",
    },
}