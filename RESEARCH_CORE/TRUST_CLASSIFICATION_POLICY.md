# Trust Classification Policy

## Purpose

This policy defines how `RESEARCH_CORE` assigns explicit trust classes to screened research inputs and emitted research packets.

Trust classification exists to prevent hidden assumptions about reliability.

---

## Policy Principle

Trust must be declared.

No research signal may move downstream with implied credibility only.

A signal must carry an explicit trust class assigned under this policy.

---

## Trust Classes

The default trust classes are:

- `unverified`
- `screened`
- `corroborated`
- `restricted`
- `rejected`

These classes describe research handling confidence, not final truth.

---

## Class Definitions

### `unverified`
Signal has been received but has not yet passed sufficient screening for downstream reliance.

### `screened`
Signal has passed initial structural and source screening and may be used with caution.

### `corroborated`
Signal has meaningful support from multiple screened or credible references and may be treated as strong research input.

### `restricted`
Signal may contain relevant value but carries handling constraints, unresolved concerns, limited sourcing, or narrow-use conditions.

### `rejected`
Signal failed trust requirements and may not be used as a valid downstream research basis.

---

## Trust Assignment Inputs

Trust classification may consider:

- source identifiability
- source credibility
- source traceability
- corroboration level
- internal consistency
- relevance to declared scope
- screening outcome
- presence of unresolved concerns

---

## Rules of Assignment

1. Trust class must be explicit.
2. Trust class must be assigned after screening, not before.
3. Trust class applies to the research handling state, not metaphysical certainty.
4. Signals with missing source traceability may not exceed `unverified` unless special rules exist.
5. Contradictory or unstable signals may be marked `restricted` even when partially useful.
6. Failed inputs must be marked `rejected`, not silently dropped if they enter governed review.

---

## Downstream Meaning

### `unverified`
May be retained for controlled review but should not drive planning on its own.

### `screened`
May move downstream as provisional research input.

### `corroborated`
May move downstream as strong research input with declared support.

### `restricted`
May move downstream only with handling caution and visible constraint.

### `rejected`
May not move downstream as valid research basis.

---

## Rationale Requirement

When possible, trust classification should be accompanied by short rationale such as:

- source quality
- corroboration status
- unresolved issue
- handling restriction

This rationale may be stored in packet metadata or supporting state.

---

## Summary

Trust classification is mandatory inside `RESEARCH_CORE`.

Its purpose is to make research reliability explicit before downstream interpretation occurs.