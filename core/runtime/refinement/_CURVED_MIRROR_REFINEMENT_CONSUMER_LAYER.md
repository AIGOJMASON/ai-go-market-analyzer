# CURVED MIRROR REFINEMENT CONSUMER LAYER

## What it is

The Curved Mirror Refinement Consumer layer is a Curved-Mirror-specific downstream surface that consumes the shared `refinement_consumer_packet` and produces a Curved Mirror safe refinement receipt.

This layer extracts only Curved Mirror facing structural signals and converts them into a bounded artifact that Curved Mirror can consume without interpreting shared structures.

---

## Core function

Consumes:
- `refinement_consumer_packet`

Produces:
- `curved_mirror_refinement_receipt`

---

## Why it exists

Stage 67 introduced a shared consumer interface.

However, Curved Mirror must not:
- parse shared packets
- infer which fields belong to it
- reinterpret Rosetta-facing guidance

This layer ensures:
- Curved Mirror receives only its allowed view
- no cross-consumer leakage occurs
- no downstream interpretation drift is introduced

---

## Authority boundary

This layer:
- does NOT learn
- does NOT rescore
- does NOT reinterpret decisions
- does NOT mutate refinement truth

This layer ONLY:
- validates consumer packet integrity
- extracts Curved Mirror facing entries
- emits a sealed Curved Mirror receipt

---

## Curved Mirror input model

Each Curved Mirror entry must include:
- signal_type
- signal_value
- total_score
- commit_targets
- source_candidate_type

These must be:
- already committed
- already approved
- already promoted
- already routed

---

## Output contract

`curved_mirror_refinement_receipt` must include:
- issuing_authority
- source_artifact_type
- consumed_count
- curved_mirror_signals
- consumer_notes
- sealed

---

## Failure protection

Reject:
- unsealed input
- invalid artifact type
- missing curved_mirror_packet
- malformed signal entries
- internal field leakage
- invalid data types

---

## System role

This is the first Curved Mirror specific ingestion boundary for refinement.

It guarantees that Curved Mirror only consumes:
- committed
- governed
- bounded
- structural refinement signals