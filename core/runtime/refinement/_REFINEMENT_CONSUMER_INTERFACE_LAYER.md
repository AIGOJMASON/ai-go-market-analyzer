# REFINEMENT CONSUMER INTERFACE LAYER

## What it is

The Refinement Consumer Interface layer is the first downstream consumer surface built on top of the committed refinement chain.

It converts committed refinement truth into bounded consumer-facing packets for:
- Rosetta
- Curved Mirror

This layer does NOT learn.

This layer does NOT alter committed refinement truth.

This layer does NOT reinterpret governance decisions beyond bounded consumer shaping.

It only transforms already-committed refinement outputs into lawful downstream interface artifacts.

---

## Core function

Consumes:
- `refinement_persistence_commit_record`

Produces:
- `refinement_consumer_packet`

---

## Why it exists

Upstream stages can now:
- observe
- select
- score
- arbitrate
- promote
- route
- commit

But those artifacts are still governance-native.

Rosetta and Curved Mirror need:
- consumer-safe shaping
- bounded payloads
- explicit consumer partitioning
- no hidden reinterpretation

This layer answers:

- what committed refinement truth each consumer may see
- how that truth is shaped for each consumer
- how consumer packets remain bounded and auditable

---

## Authority boundary

This layer:
- does NOT learn
- does NOT reweight
- does NOT infer causality
- does NOT change policy
- does NOT mutate committed refinement truth

This layer ONLY:
- validates committed refinement records
- partitions committed items into consumer-safe forms
- emits a sealed consumer packet

---

## Consumer model

Two initial consumers are supported:
- `rosetta`
- `curved_mirror`

Both consumers read from the same committed truth base.

They do NOT receive the same presentation form.

### Rosetta receives
- human-facing refinement guidance
- compact summary statements
- bounded pattern guidance
- readable emphasis ordering

### Curved Mirror receives
- structural refinement signals
- candidate type
- score
- route/commit context
- compact weighting-safe inputs

---

## Packet rules

Consumer eligibility:
- item must already be committed

Consumer packet must include:
- source lineage
- committed item count
- per-consumer packet sections
- consumer notes
- sealed output

Rosetta packet entries must include:
- guidance_type
- guidance_text
- source_candidate_type
- total_score

Curved Mirror packet entries must include:
- signal_type
- signal_value
- total_score
- commit_targets

---

## Output contract

`refinement_consumer_packet` must:
- be sealed
- include only committed items
- preserve lineage to Stage 66
- include separate `rosetta_packet` and `curved_mirror_packet`
- expose packet counts and notes

---

## Failure protection

Reject:
- unsealed inputs
- invalid artifact types
- missing required fields
- internal field leakage
- malformed committed items
- invalid commit status
- invalid route targets

---

## System role

This is the first real downstream interface boundary in refinement.

Stage 63 made refinement usable.

Stage 66 made refinement durably trustworthy.

Stage 67 makes refinement consumable by governed cognition layers.