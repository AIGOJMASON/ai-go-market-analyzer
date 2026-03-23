# REFINEMENT ARBITRATION LAYER

## What it is

The Refinement Arbitration layer is the decision boundary of the refinement pipeline.

It converts scored refinement candidates into governed decisions.

---

## Core function

Consumes:
- refinement_scoring_record

Produces:
- refinement_decision_record

---

## Why it exists

Upstream stages:
- select candidates (Stage 61)
- score candidates (Stage 62)

But they do not decide outcomes.

This layer determines:
- what is approved
- what is deferred
- what is rejected

---

## Authority boundary

This layer:
- does NOT learn
- does NOT modify system behavior
- does NOT reweight models
- does NOT infer causality

This layer ONLY:
- applies deterministic thresholds
- enforces caps
- produces explicit decisions

---

## Decision model

Each candidate is assigned:
- approved
- deferred
- rejected

---

## Rules

Score thresholds:
- score >= 4 → approved
- score == 3 → deferred
- score <= 2 → rejected

Approval cap:
- max 3 approved per batch

Tie-breaking:
1. higher score
2. candidate type priority
3. lexical fallback

---

## Candidate priority

1. pattern_note
2. target_child_core_count
3. closeout_count
4. intake_count

---

## Output contract

refinement_decision_record must:
- preserve candidate identity
- include score and decision
- include decision reason
- include counts
- be sealed

---

## Failure protection

Reject:
- unsealed inputs
- invalid artifact types
- malformed candidates
- internal field leakage

---

## System role

This is the first lawful decision surface in refinement.

Selection → Scoring → Decision

This stage completes that chain.