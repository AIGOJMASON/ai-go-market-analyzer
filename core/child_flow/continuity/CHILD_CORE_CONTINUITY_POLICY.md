
---

## FILE: `AI_GO/core/child_flow/continuity/CHILD_CORE_CONTINUITY_POLICY.md`

```md
# CHILD CORE CONTINUITY POLICY
## Stage 26 Admission Policy

## Purpose
This policy governs whether a watcher result may be admitted into continuity intake.

This is an intake policy only.
It is not a mutation policy.

---

## Admission Principle
Watcher output is not continuity by default.

Watcher output becomes eligible for continuity intake only when:
1. its structure is valid
2. its provenance is intact
3. its target scope is lawful
4. its signal is continuity-worthy
5. its admission does not create unresolved persistence without basis

---

## Required Inputs

### Required artifact
- `watcher_result`

### Required metadata
- `continuity_context`

---

## Required Contract — watcher_result

### Mandatory keys
- `findings`

### Optional keys
- `findings_ref`

### Findings requirements
- `findings` must be a dictionary
- `findings` must not be empty
- `findings` must represent watcher output, not synthetic summary text
- Stage 26 must evaluate only admissibility, not rewrite findings

---

## Required Contract — continuity_context

### Mandatory keys
- `target_core`
- `watcher_id`
- `watcher_receipt_ref`
- `output_disposition_ref`
- `runtime_ref`
- `event_timestamp`
- `continuity_scope`
- `intake_reason`
- `admission_policy_version`

### Rules
- `target_core` must be registered
- `continuity_scope` must be allowed for the target core
- `admission_policy_version` must match an allowed version in registry
- refs must be non-empty strings

---

## Admission Checks

### 1. provenance integrity
The intake request must preserve lineage back through:
- watcher receipt
- output disposition receipt
- runtime ref
- target core identity

If the chain is incomplete, reject.

### 2. contract integrity
If the watcher-result contract is malformed, reject.

### 3. scope legality
If requested continuity scope is not registered for the target core, reject.

### 4. continuity worthiness
A watcher result is continuity-worthy only if at least one of the following is true:
- repeated signal across runs
- critical operational failure
- policy violation
- durable domain relevance
- unresolved issue requiring survival beyond the current run

If none apply, hold or reject depending on severity and completeness.

### 5. duplication and freshness
If the event appears duplicate, stale, or superseded:
- hold if human review may resolve it
- otherwise reject

### 6. entropy threshold
Reject or hold when admission would create unresolved continuity burden without adequate coherence.

---

## Decision Rules

### accepted
Use only when:
- all required fields are present
- all integrity checks pass
- continuity worthiness is established
- no duplication or legality block exists

### held
Use when:
- contract is valid
- provenance is sufficient
- but continuity worthiness is unresolved, incomplete, or awaiting corroboration

Examples:
- weak repeated pattern not yet confirmed
- possible duplicate needing merge review
- incomplete but non-fatal supporting refs
- signal important enough not to discard immediately

### rejected
Use when:
- required data is missing
- watcher contract is broken
- target core or scope is not allowed
- event is clearly duplicate, stale, or non-continuity-worthy
- findings are too weak to justify persistence
- intake would violate entropy discipline

---

## Hold Rules
A hold must include:
- hold reason
- release condition
- review window or expiry marker

A hold may not become indefinite continuity shadow state.

---

## Rejection Codes

### structural_invalid
Required contract fields missing or malformed.

### lineage_broken
Required provenance refs missing or inconsistent.

### scope_unlawful
Requested target or continuity scope not registered.

### duplicate_event
Event appears already admitted or superseded.

### stale_event
Event outside admissible freshness window for its scope.

### insufficient_signal
Findings do not justify continuity persistence.

### policy_version_invalid
Admission policy version is unknown or disallowed.

### entropy_block
Admission would create unresolved continuity burden without lawful basis.

---

## Non-Permissions
Stage 26 policy does not authorize:
- continuity mutation
- watcher replay
- freeform summarization
- final memory writing
- downstream publication
- new interpretation beyond intake policy tests

---

## Policy Version
Current version: `stage26.v1`

All Stage 26 decisions must record the policy version used.