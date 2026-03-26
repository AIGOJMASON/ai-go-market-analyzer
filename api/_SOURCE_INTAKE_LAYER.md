# SOURCE INTAKE LAYER

## Purpose

The Source Intake Layer introduces a governed intake boundary for external-style market signals before they become candidate cases or advisory analysis inputs.

This layer exists to solve the gap between:

- manual operator case entry
- source-driven operator discovery

It does **not** replace the governed market analyzer route.

It sits upstream of that route and performs only bounded intake, normalization, clustering, dissemination, and candidate suggestion.

---

## Responsibilities

The Source Intake Layer is responsible for:

1. accepting bounded source records
2. validating source type and trust class
3. normalizing raw source items into canonical signal records
4. clustering related signals into candidate groups
5. disseminating ranked operator-visible suggestions
6. preserving provenance and governance truth

---

## Non-Responsibilities

The Source Intake Layer must never:

- execute trades
- mutate recommendation logic
- bypass PM workflow
- create hidden learning state
- infer unsupported facts beyond bounded normalization rules
- overwrite runtime outputs from Market Analyzer V1

---

## Authority Boundary

The layer is:

- advisory-only
- read/generated
- append-oriented
- non-executing
- non-mutating

All outputs from this layer are suggestion artifacts.

They may inform later governed analysis, but they may not become recommendations without passing through the canonical market analyzer route.

---

## Canonical Flow

```text
approved source input
    ↓
source registry validation
    ↓
source normalization
    ↓
signal clustering
    ↓
dissemination ranking
    ↓
operator inbox + candidate suggestion surface
    ↓
optional downstream analysis by governed market analyzer route
Output Artifacts

This layer emits the following bounded artifacts:

source_signal_record
source_cluster_record
source_candidate_record
source_inbox_record

These artifacts are explicit and inspectable.

No hidden state is permitted.

Global Invariants

The Source Intake Layer must preserve the following invariants:

execution_influence = false
recommendation_mutation_allowed = false
runtime_mutation_allowed = false
source_records_append_only = true
provenance_required = true
Source Classes

Approved source classes:

operator_manual
newswire
rss_feed
watchlist_note
macro_note
social_observation

These classes may differ in trust level, but all must remain bounded and explicitly tagged.

Dissemination Model

The dissemination layer produces:

ranked incoming signals
grouped candidate cases
suggested operator next steps

Suggested next steps are limited to:

monitor
review
analyze
dismiss

These are workflow suggestions only.

They are not trade instructions.

Relationship to Existing Market Analyzer V1

This layer does not replace:

/market-analyzer/run
/market-analyzer/run/live
PM cognition stages 16 through 23
receipt, watcher, or closeout flows

Instead, it creates a lawful upstream desk so the operator no longer has to hand-build every case before analysis.

Operator Surface Rule

The operator-facing surface should expose:

Incoming Signals
Candidate Cases
Suggested Actions
Governance + Provenance

Manual case entry may remain available, but it must no longer be the sole visible operating mode.

Completion Standard

This layer is considered complete only when:

source intake is bounded and validated
normalization is deterministic
clustering is inspectable
dissemination is operator-readable
outputs remain advisory-only
provenance remains visible
downstream analysis remains optional and governed