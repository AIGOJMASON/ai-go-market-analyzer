# Screening Policy

## Purpose

This policy defines the minimum screening rules applied to incoming research signal before trust classification and packet emission.

Screening exists to stop malformed, irrelevant, unsupported, or unsafe signal from passing downstream as governed research.

---

## Policy Principle

No raw signal becomes packetized research without screening.

Screening is the first formal control surface inside `RESEARCH_CORE`.

---

## Screening Goals

Screening is used to determine whether an input is:

- structurally usable
- relevant to declared scope
- attributable to sources
- coherent enough for trust review
- suitable for packet construction

---

## Minimum Screening Checks

Each input should be screened for:

1. presence of identifiable source or source reference
2. minimum structural completeness
3. relevance to declared domain, core, or system scope
4. basic internal coherence
5. absence of obvious duplication when duplication matters
6. declared handling issues or constraints when present

---

## Screening Outcomes

Valid screening outcomes are:

- `passed`
- `deferred`
- `needs_review`
- `rejected`

---

## Outcome Definitions

### `passed`
The signal is sufficiently structured to proceed to trust classification.

### `deferred`
The signal may be relevant but cannot yet proceed because a required element is missing or unresolved.

### `needs_review`
The signal contains ambiguity, instability, or unusual characteristics requiring explicit human or higher-order review.

### `rejected`
The signal is too incomplete, irrelevant, incoherent, or unsupported to proceed.

---

## Screening Rules

1. Screening checks structure before interpretation.
2. Screening does not assign strategy.
3. Screening does not replace trust classification.
4. Relevance alone is insufficient without minimum structural integrity.
5. Inputs with unclear sourcing may be deferred or rejected depending on severity.
6. High-risk ambiguity should surface as `needs_review`, not silent acceptance.

---

## Relationship to Trust Classification

Screening answers:

Is this signal fit to proceed?

Trust classification answers:

How strongly may this signal be relied on?

These are separate steps and must remain separate.

---

## Relationship to Packet Emission

Only inputs that lawfully pass screening may proceed toward packet construction.

Deferred or review-bound items may remain in research state, but may not be emitted as normal valid packets without explicit rule support.

---

## Summary

Screening is the structural gate of `RESEARCH_CORE`.

Its purpose is to ensure that only research inputs with minimum usability and relevance proceed toward trust classification and packet emission.