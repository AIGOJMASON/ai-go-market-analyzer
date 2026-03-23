REQUIRED_TRANSPORT_ENVELOPE_FIELDS = {
    "transport_envelope_id",
    "transport_envelope_type",
    "timestamp",
    "summary",
    "result",
    "ack_index_ref",
    "ack_index_type",
    "delivery_receipt_ref",
    "delivery_index_ref",
    "dispatch_manifest_ref",
    "bundle_ref",
    "report_count",
    "payload_class",
    "route_class",
    "execution_mode",
    "transport_permitted",
}

REQUIRED_EXECUTION_RESULT_FIELDS = {
    "transport_execution_id",
    "transport_execution_result_type",
    "timestamp",
    "summary",
    "result",
    "transport_envelope_ref",
    "transport_envelope_type",
    "ack_index_ref",
    "payload_class",
    "route_class",
    "execution_mode",
    "adapter_class",
    "execution_attempted",
    "execution_permitted",
}

INTERNAL_FIELD_NAMES = {
    "_internal_state",
    "_debug_trace",
    "_raw_payload",
    "_authority_override",
    "_transport_secret",
    "_adapter_state",
}

SUCCESS_RESULT_VALUES = {
    "executed",
}

DENIED_RESULT_VALUES = {
    "denied",
    "rejected",
}