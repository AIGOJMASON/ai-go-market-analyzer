ALLOWED_TRANSPORT_ENVELOPE_TYPES = {
    "delivery_transport_envelope_v1",
}

ALLOWED_ACK_INDEX_TYPES = {
    "runtime_acknowledgement_index_v1",
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