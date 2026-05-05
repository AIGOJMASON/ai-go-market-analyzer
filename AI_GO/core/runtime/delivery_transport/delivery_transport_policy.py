REQUIRED_ACK_INDEX_FIELDS = {
    "ack_index_id",
    "ack_index_type",
    "timestamp",
    "summary",
    "result",
    "acknowledgement_registered",
    "delivery_receipt_ref",
    "delivery_index_ref",
    "dispatch_manifest_ref",
    "bundle_ref",
    "report_count",
    "payload_class",
    "route_class",
    "execution_mode",
}

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

INTERNAL_FIELD_NAMES = {
    "_internal_state",
    "_debug_trace",
    "_raw_payload",
    "_authority_override",
    "_transport_secret",
}

TRUE_RESULT_VALUES = {
    "accepted",
}

FALSE_RESULT_VALUES = {
    "rejected",
    "failed",
    "pending",
}