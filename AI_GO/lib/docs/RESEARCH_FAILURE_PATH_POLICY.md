# RESEARCH FAILURE PATH POLICY

## Purpose

This policy defines how the governed research route handles non-success outcomes after activation.

It exists to prevent silent failure, hidden retries, and false completion claims.

---

## Core Rule

Failure handling must preserve truth in this order:

1. stop the forward claim
2. emit a truthful runtime receipt
3. route unresolved state when the failure belongs to governed runtime execution
4. avoid mutation outside the owning boundary

---

## Failure Classes

### 1. Contract Failure
A contract failure occurs when the input payload does not satisfy the canonical research command contract.

Examples:
- missing `args`
- missing `title`
- invalid `source_refs` type

Handling rule:
- return `research_pipeline_failed`
- emit runtime receipt
- do **not** enqueue unresolved state

Reason:
No governed route was lawfully entered.

---

### 2. Pre-Persistence Runtime Failure
A pre-persistence runtime failure occurs after contract acceptance but before packet persistence succeeds.

Examples:
- intake normalization failure
- screening execution failure
- trust assignment failure
- packet construction failure

Handling rule:
- return `research_pipeline_failed`
- emit runtime receipt
- enqueue unresolved state

Reason:
The governed route was entered but did not complete.

---

### 3. Verification Failure
A verification failure occurs when packet persistence succeeds but watcher verification does not.

Examples:
- packet file missing
- invalid JSON artifact
- required packet keys missing
- packet shape invalid

Handling rule:
- return `research_pipeline_complete`
- set result status to degraded form
- emit runtime receipt
- enqueue unresolved state

Reason:
A packet artifact exists, but the transaction did not close truthfully.

---

### 4. Continuity Failure
A continuity failure occurs when watcher verification succeeds but continuity reflection does not.

Examples:
- SMI state write failure
- change ledger write failure
- state file corruption

Handling rule:
- return `research_pipeline_complete`
- set result status to degraded form
- emit runtime receipt
- enqueue unresolved state

Reason:
Artifact truth was established, but continuity truth was not fully committed.

---

## Retry Rule

The router does not retry automatically.

Reason:
Retry logic changes temporal behavior and can create hidden state mutation.
Any retry policy must be introduced as a separately governed feature.

---

## Unresolved Queue Rule

Unresolved queue routing is allowed only when:
- the route passed contract validation
- a governed execution path was actually entered
- the route ended in incomplete or degraded state

Unresolved queue routing is not allowed for pure contract rejection.

---

## Status Semantics

### Route-level
- `research_pipeline_complete`
- `research_pipeline_failed`

### Result-level
- `verified_and_recorded`
- `verified_with_continuity_failure`
- `persisted_with_verification_failure`

### Queue-level
- `queued`
- `skipped`
- `failed`

---

## Authority Boundaries

- router identifies failure class and composes the response
- runtime receipt records transaction truth
- unresolved queue stores follow-up state
- watcher does not enqueue
- SMI does not enqueue
- RESEARCH_CORE does not own failure queue state

---

## Enforcement Summary

- no silent failure
- no hidden retries
- no false completion claim
- no unresolved state for invalid input that never entered the route
- degraded runtime outcomes must be visible and recorded