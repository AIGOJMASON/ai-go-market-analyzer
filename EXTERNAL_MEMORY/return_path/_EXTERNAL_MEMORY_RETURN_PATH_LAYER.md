# EXTERNAL MEMORY RETURN PATH LAYER

Purpose:
Provide the lawful return-path surface that converts promoted external-memory
artifacts into bounded advisory-ready output packets for live system use.

Input -> Output:
external_memory_promotion_artifact
-> return-path validation
-> advisory packet
-> return-path receipt

Why This Layer Exists:
Promotion decides what retrieved memory may matter later.
The return path decides how that promoted memory may re-enter live output
without mutating runtime, PM, or recommendation authority.

Promotion answers:
- is this memory strong enough to matter later?

Return path answers:
- in what bounded form may this promoted memory be shown now?

Authority Class:
bounded advisory return-path authority

It May:
- validate promoted-memory artifact structure
- validate target child core and requester profile
- convert promoted memory into advisory-safe packet form
- emit return-path advisory packets and receipts
- provide panel-ready output summaries

It May Not:
- mutate recommendation logic
- mutate PM strategy
- mutate runtime state
- mutate persistence, retrieval, or promotion history
- bypass promotion
- become execution authority

Hard Rules:
1. Only promoted-memory artifacts may enter this layer.
2. Return-path output is advisory only.
3. Return-path output must preserve provenance and score visibility.
4. The return-path packet must be bounded and panel-safe.
5. No direct execution or recommendation mutation is allowed.
6. Unknown target child cores are rejected.
7. Unknown requester profiles are rejected.
8. Hold or reject promotion decisions may not pass this layer.
9. This layer emits output packets, not final UI surfaces.

Primary Outputs:
- external_memory_return_packet
- external_memory_return_receipt
- external_memory_return_rejection_receipt

Current Phase Scope:
Phase 4 return-path only

Included:
- return-path layer docs
- return-path registry
- return-path policy
- return-path runtime
- return-path receipt builder
- market-analyzer-specific adapter
- probe validation

Deferred:
- direct PM influence coupling
- direct runtime confidence adjustment
- multi-core shared advisory routing
- final operator dashboard merge logic

Canonical Flow:
promotion_artifact + promotion_receipt
-> return_path_runtime
-> validation
-> advisory packet
-> return-path receipt

Advisory Packet Purpose:
The advisory packet exists so later live output surfaces can display:
- promoted memory status
- recurrence / coherence notes
- source-quality context
- bounded caution posture
- memory lineage references

Return-Path Rule:
Promoted memory may return as advisory context.
Promoted memory may not return as command authority.