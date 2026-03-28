from __future__ import annotations

OUTPUT_MERGE_REGISTRY: dict = {
    "layer_id": "external_memory.output_merge",
    "accepted_return_packet_type": "external_memory_return_packet",
    "accepted_return_receipt_type": "external_memory_return_receipt",
    "allowed_projection_targets": [
        "external_memory_return_panel",
        "external_memory_provenance_refs",
        "external_memory_merge_status",
        "cognition_panel.external_memory_advisory",
    ],
    "protected_fields": [
        "recommendation_panel",
        "governance_panel",
        "pm_workflow_panel",
        "approval_required",
        "execution_allowed",
        "route_mode",
    ],
    "rejection_reasons": [
        "invalid_operator_response",
        "invalid_return_packet_type",
        "invalid_return_receipt_type",
        "artifact_receipt_misalignment",
        "missing_required_advisory_fields",
    ],
    "emitted_artifacts": [
        "external_memory_output_merge_receipt",
        "external_memory_output_merge_rejection_receipt",
    ],
}