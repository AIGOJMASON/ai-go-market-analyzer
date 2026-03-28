# EXTERNAL MEMORY OUTPUT MERGE LAYER

Purpose:
Provide the lawful merge surface that projects a validated external-memory
return packet into operator-facing output without mutating recommendation
logic, PM authority, runtime authority, or execution state.

Input -> Output:
operator response
+ external_memory_return_packet
+ external_memory_return_receipt
-> merged operator response
-> output merge receipt

Why This Layer Exists:
The return-path layer produces advisory-ready packets.
The output-merge layer decides how that advisory packet may be projected
into live operator output safely.

Return path answers:
- what promoted external memory may return as advisory context?

Output merge answers:
- where may that advisory context appear in operator output?
- what fields are safe to add?
- what existing surfaces must remain untouched?

Authority Class:
bounded operator-output projection authority

It May:
- validate return packet and return receipt
- project advisory memory context into dedicated output fields
- preserve provenance references for operator visibility
- emit a merge receipt

It May Not:
- rewrite recommendation items
- rewrite recommendation confidence
- rewrite governance state
- rewrite PM workflow state
- rewrite runtime classification
- bypass the return path
- absorb final UI rendering authority

Hard Rules:
1. Only lawful external_memory_return_packet artifacts may be merged.
2. Merge is additive, not mutative, for core decision panels.
3. recommendation_panel must remain semantically unchanged.
4. governance_panel must remain semantically unchanged.
5. pm_workflow_panel must remain semantically unchanged.
6. The merge layer may only add bounded advisory surfaces.
7. Invalid return packets must be rejected with explicit receipts.
8. Output merge must preserve original operator response fields.

Primary Outputs:
- merged operator response
- external_memory_output_merge_receipt
- external_memory_output_merge_rejection_receipt

Allowed Projection Targets in Phase 5:
- top-level external_memory_return_panel
- top-level external_memory_provenance_refs
- top-level external_memory_merge_status
- cognition_panel.external_memory_advisory

Current Phase Scope:
Phase 5 operator-output projection only

Included:
- output-merge layer docs
- output-merge policy
- output-merge registry
- output-merge runtime
- output-merge receipt builder
- market-analyzer-specific adapter
- probe validation

Deferred:
- direct UI formatting
- dashboard-builder internal rewrite
- PM influence coupling
- multi-child-core shared merge routing

Canonical Flow:
operator_response
+ external_memory_return_packet
+ external_memory_return_receipt
-> output_merge_runtime
-> merged operator response
-> merge receipt

Merge Rule:
External memory may appear in operator output as advisory context.
External memory may not appear as hidden decision mutation.