# REVIEW INDEX LAYER

## Purpose

The review index layer is the governed aggregation and query surface for
operator review artifacts.

It exists to consume one or more approved `operator_review_view` artifacts
and produce a bounded `operator_review_index` that supports filtering,
selection, and pagination without mutating source artifacts.

This layer does not resolve truth.
This layer does not execute logic.
This layer does not alter lifecycle state.

It is a read-only aggregation and query projection.

---

## Runtime Role

The review index layer sits downstream of:

- operator review view

It sits upstream of:

- operator dashboards
- CLI query surfaces
- watcher feeds
- reporting layers

Its role is to answer:

- what cases exist in the current view set
- which cases match filter criteria
- how to page or slice the results

---

## Structural Rule

Review index may:

- validate multiple operator_review_view artifacts
- apply bounded filters
- apply pagination
- emit one index artifact

Review index may not:

- mutate source artifacts
- infer missing data
- execute downstream logic
- expose internal fields

---

## Inputs

Approved inputs:

- list of `operator_review_view`

Rules:

- all inputs must be sealed
- all inputs must be valid artifacts
- no internal leakage allowed

Optional query controls:

- filter criteria
- pagination (limit, offset)

---

## Output

Approved output:

- `operator_review_index`

This artifact provides:

- total count
- filtered count
- list of results (bounded)
- pagination metadata

---

## Why This Layer Exists

Without this layer:

- operators would manually iterate over records
- filtering would be inconsistent
- pagination would be ad hoc

This layer provides a governed, consistent query surface.

---

## Enforcement Rules

This layer enforces:

- artifact validation
- sealed input requirement
- internal leakage blocking
- bounded output size
- deterministic filtering

---

## Final Constraint

This layer answers:

- what cases match a query
- how many exist
- how they can be paged

This layer does not answer:

- how to change the case
- how to execute logic
- how to resolve new truth