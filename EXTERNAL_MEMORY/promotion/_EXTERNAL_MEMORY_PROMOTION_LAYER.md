# EXTERNAL MEMORY PROMOTION LAYER

Purpose:
Provide the lawful promotion surface that evaluates retrieved external-memory
records and determines whether any record or bounded record group is eligible
to become reusable promoted memory.

Input -> Output:
retrieval artifact
-> promotion scoring
-> promotion arbitration
-> promotion artifact or promotion rejection
-> promotion receipt

Why This Layer Exists:
Admission decides what may persist.
Retrieval decides what may be read.
Promotion decides what may matter later.

Those are distinct authorities.

Admission answers:
- may this record enter durable storage?

Retrieval answers:
- may this requester read this record set now?

Promotion answers:
- do these retrieved records deserve reusable influence class?

Authority Class:
bounded promotion authority for retrieved external memory

It May:
- validate retrieval artifact and receipt pairing
- score retrieved records for reuse eligibility
- arbitrate bounded promotion outcomes
- emit promoted-memory artifacts and receipts
- reject weak or noisy retrieval sets explicitly

It May Not:
- mutate stored records
- bypass retrieval controls
- mutate PM strategy directly
- mutate runtime state directly
- rewrite recommendation logic directly
- skip scoring or arbitration

Hard Rules:
1. Promotion requires lawful retrieval input.
2. Promotion is not automatic because records were retrieved.
3. Promotion must preserve provenance and source-quality visibility.
4. Promotion must remain bounded by requester profile and target core.
5. Promotion may emit advisory-ready promoted memory only.
6. Promotion does not directly alter live output in Phase 3.
7. Promotion rejection must be explicit and receipted.
8. Promotion may group records only within the same target child core.
9. Promotion does not replace later runtime return-path integration.

Primary Outputs:
- external_memory_promotion_artifact
- external_memory_promotion_receipt
- external_memory_promotion_rejection_receipt

Current Phase Scope:
Phase 3 promotion only

Included:
- promotion layer docs
- promotion registry
- promotion policy
- promotion scoring runtime
- promotion arbitration runtime
- promotion receipt builder
- market-analyzer-specific promotion adapter
- probe validation

Deferred:
- live runtime return-path influence
- PM influence coupling
- child-core execution coupling
- longitudinal recurrence aggregation beyond retrieved record set
- training-grade memory promotion tier

Canonical Flow:
retrieval_artifact + retrieval_receipt
-> promotion_runtime
-> promotion_scoring
-> promotion_arbitration
-> promotion artifact or rejection receipt

Promotion Question:
Do these retrieved records show enough combined quality, relevance, and
retrieval coherence to deserve reusable advisory status?

Primary Decision Axes:
- source_quality_weight
- adjusted_weight
- trust_class strength
- record_count coherence
- symbol / sector coherence
- contamination drag
- requester-profile legality

Promotion Classes:
1. promoted
   - eligible for later bounded advisory reuse
2. hold
   - not promoted in Phase 3
3. reject
   - not reusable

Promotion does NOT equal runtime influence.
Later layers will decide how promoted memory may lawfully return.