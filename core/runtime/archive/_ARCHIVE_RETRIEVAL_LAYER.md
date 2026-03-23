# ARCHIVE RETRIEVAL LAYER

## Purpose

The archive retrieval layer is the governed lookup surface for finalized
runtime artifacts.

It exists to consume a bounded archive set of approved finalized artifacts
and a bounded retrieval query, then emit one `archive_retrieval_result`
for operator, watcher, or later system use.

This layer does not resolve truth.
This layer does not execute logic.
This layer does not mutate archived artifacts.

It is retrieval only.

---

## Runtime Role

The archive retrieval layer sits downstream of:

- case closeout archive
- operator review projection
- review index / query surface

It sits upstream of:

- operator retrieval commands
- watcher retrieval surfaces
- later archive analytics or refinement surfaces

Its role is to answer:

- which archived finalized artifacts match the query
- how many matches were found
- what bounded result set may be safely returned

---

## Structural Rule

Archive retrieval may:

- validate archived finalized artifacts
- validate bounded retrieval query parameters
- filter artifacts by approved criteria
- page result sets
- emit one governed retrieval result

Archive retrieval may not:

- mutate source artifacts
- infer missing state
- reopen cases
- execute downstream logic
- expose internal fields

---

## Inputs

Approved archive item inputs:

- `case_closeout_record`
- `operator_review_view`
- `operator_review_index`

Approved query controls:

- `artifact_type`
- `case_id`
- `target_child_core`
- `closeout_state`
- `final_state`
- `intake_decision`
- `limit`
- `offset`

Rules:

- all archived items must be sealed
- all archived items must be approved finalized artifact types
- all query controls must be bounded and explicit
- no internal leakage is allowed

---

## Output

Approved output:

- `archive_retrieval_result`

This artifact provides:

- total archive count
- filtered count
- bounded result set
- query controls used
- pagination metadata

This output is retrieval only.

---

## Why This Layer Exists

Without this layer, archive access would require direct iteration over
mixed finalized artifacts and ad hoc filtering logic.

That would create:

- inconsistent retrieval behavior
- duplicated query logic
- risk of unsafe artifact exposure

The archive retrieval layer prevents that by creating one governed,
bounded retrieval surface for finalized case artifacts.

---

## Enforcement Rules

This layer enforces:

- strict artifact validation
- sealed input requirement
- internal leakage blocking
- approved query-field validation
- bounded output size
- deterministic filtering and pagination

---

## Final Constraint

This layer answers:

- what archived finalized artifacts match the query
- how many items matched
- what bounded result set may be returned

This layer does not answer:

- how to change archived state
- how to execute logic
- how to resolve new truth