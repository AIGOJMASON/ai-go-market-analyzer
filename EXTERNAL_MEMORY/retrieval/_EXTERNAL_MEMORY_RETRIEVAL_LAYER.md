# EXTERNAL MEMORY RETRIEVAL LAYER

Purpose:
Provide the lawful read surface for persisted external-memory records after
admission and durable storage have already occurred.

Input -> Output:
bounded retrieval request
-> filtered DB query
-> bounded retrieval artifact
-> retrieval receipt

Why This Layer Exists:
The external-memory admission layer decides what may persist.
This retrieval layer decides what may be lawfully read back out.

Those are different authorities.

Admission answers:
- may this record enter durable storage?

Retrieval answers:
- may this requester read this record set now?
- in what bounded form?
- with what filters and limits?

Authority Class:
read-only external-memory retrieval authority

It May:
- validate retrieval request structure
- validate requester and target legality
- query persisted external-memory records
- apply bounded filters and record limits
- emit retrieval artifacts and receipts

It May Not:
- mutate stored records
- promote records into reusable influence
- mutate PM strategy
- mutate runtime state
- bypass registry constraints
- return raw unrestricted DB dumps

Hard Rules:
1. Retrieval is read-only.
2. All retrieval must be request-based and receipted.
3. Record limits are mandatory.
4. Requester legality is explicit, not inferred.
5. Child-core target filtering is explicit, not guessed.
6. Retrieval does not equal promotion.
7. Retrieved records are not automatically runtime influence.
8. This layer must preserve source-quality and weight visibility.

Primary Outputs:
- external_memory_retrieval_artifact
- external_memory_retrieval_receipt
- external_memory_retrieval_failure_receipt

Current Phase Scope:
Phase 2 retrieval only

Included:
- retrieval layer docs
- retrieval registry
- retrieval policy
- retrieval runtime
- retrieval receipt builder
- sqlite-backed query surface
- probe validation

Deferred:
- promotion
- continuity indexing beyond current DB fields
- return-path influence into live analyzer
- PM and child-core promoted memory consumers

Canonical Flow:
retrieval_request
-> retrieval_runtime
-> retrieval_registry validation
-> db query
-> bounded artifact
-> receipt

Required Retrieval Controls:
- requester_profile
- target_child_core
- limit
- optional source_type filter
- optional trust_class filter
- optional persistence_decision-compatible view
- optional minimum adjusted weight

Default Phase 2 Requester Profiles:
- operator_reader
- market_analyzer_reader
- pm_reader

Primary Query Fields Available:
- memory_id
- qualification_record_id
- source_type
- trust_class
- source_quality_weight
- signal_quality_weight
- domain_relevance_weight
- persistence_value_weight
- contamination_penalty
- redundancy_penalty
- adjusted_weight
- target_child_cores_json
- provenance_json
- payload_json
- created_at