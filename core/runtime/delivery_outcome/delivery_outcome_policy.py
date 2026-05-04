REQUIRED_TRANSPORT_EXECUTION_RESULT_FIELDS = {
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

REQUIRED_DELIVERY_OUTCOME_RECEIPT_FIELDS = {
    "delivery_outcome_receipt_id",
    "delivery_outcome_receipt_type",
    "timestamp",
    "summary",
    "result",
    "transport_execution_ref",
    "transport_execution_result_type",
    "transport_envelope_ref",
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
    "_receipt_private_state",
}