# EXTERNAL MEMORY RETRIEVAL POLICY

Purpose:
Define the lawful read rules for persisted external-memory records.

Primary Question:
May this requester read this set of records in this bounded form?

Required Request Fields:
- requester_profile
- target_child_core
- limit

Optional Fields:
- source_type
- trust_class
- min_adjusted_weight
- symbol
- sector

Phase 2 Requester Profiles:
1. operator_reader
   - broad inspection allowed
   - max_records: 25

2. market_analyzer_reader
   - market_analyzer_v1 target only
   - max_records: 15

3. pm_reader
   - strategic inspection allowed
   - max_records: 20

Hard Policy Rules:
1. Unknown requester_profile is rejected.
2. Unknown target_child_core is rejected.
3. Limit must be >= 1.
4. Limit may not exceed requester-profile max_records.
5. Retrieval is read-only.
6. Retrieved output must remain bounded and structured.
7. No implicit full-table scans may be exposed as output.
8. Filters may narrow results but may not widen authority.

Filtering Rules:
- source_type filter matches exact source_type
- trust_class filter matches exact trust_class
- min_adjusted_weight filters records whose adjusted_weight is >= threshold
- symbol filter checks payload_json symbol field
- sector filter checks payload_json sector field
- target_child_core must match the stored target_child_cores_json

Default Ordering:
Newest first by created_at descending

Output Shape:
retrieval artifact must include:
- request summary
- matched_count
- returned_count
- bounded records list

Each returned record must include:
- memory_id
- source_type
- trust_class
- source_quality_weight
- adjusted_weight
- target_child_cores
- provenance
- payload summary
- created_at

Phase 2 Limitation:
This layer retrieves persisted records only.
It does not:
- score recurrence
- arbitrate patterns
- promote memory
- feed runtime influence directly