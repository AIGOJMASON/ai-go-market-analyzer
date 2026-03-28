# EXTERNAL MEMORY OUTPUT MERGE POLICY

Purpose:
Define the lawful rules for projecting external-memory return packets into
operator-facing output safely.

Required Inputs:
- operator response dict
- external_memory_return_packet
- external_memory_return_receipt

Minimum Input Law:
- return packet artifact_type must be external_memory_return_packet
- return receipt artifact_type must be external_memory_return_receipt
- requester_profile must match between packet and receipt
- target_child_core must match between packet and receipt
- memory_context_panel.state must be present
- advisory_summary.state must be present

Phase 5 Allowed Merge Targets:
1. top-level external_memory_return_panel
2. top-level external_memory_provenance_refs
3. top-level external_memory_merge_status
4. cognition_panel.external_memory_advisory

Prohibited Mutations:
- recommendation_panel
- governance_panel
- pm_workflow_panel
- recommendation items
- recommendation confidence
- approval_required
- execution_allowed
- route_mode
- candidate selection state

Merge Method:
- preserve original response
- add bounded external-memory surfaces only
- create cognition_panel if absent
- do not delete any existing fields
- do not rename any existing fields

Success Output:
Merged response must include:
- external_memory_merge_status = "merged"
- external_memory_return_panel
- external_memory_provenance_refs
- cognition_panel.external_memory_advisory

Rejection Rules:
Reject when:
- operator response is not a dict
- return packet invalid
- return receipt invalid
- packet/receipt misaligned
- required advisory fields missing

Phase 5 Limitation:
This layer projects advisory context only.
It does not:
- perform final UI styling
- alter runtime or PM truth
- change recommendations
- create new persistence or promotion records