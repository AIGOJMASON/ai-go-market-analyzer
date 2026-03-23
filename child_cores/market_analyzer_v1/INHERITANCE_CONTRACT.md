# INHERITANCE_CONTRACT — market_analyzer_v1

## Authority Source

This child core inherits authority strictly from:

PM_CORE

It does not possess independent authority.

---

## Inheritance Scope

Allowed inputs:

- validated research artifacts
- weighted decision artifacts
- refinement-conditioned signals
- sealed upstream packets

---

## Forbidden Inputs

This core MUST reject:

- unsealed artifacts
- raw RESEARCH_CORE outputs
- user-provided direct data
- any data lacking provenance

---

## Inheritance Rules

1. No mutation of upstream artifacts
2. No reweighting of signals
3. No reinterpretation beyond domain template
4. No persistence of unresolved state

---

## Conditioning Model

Refinement is:

- read-only
- non-learning
- non-persistent beyond execution cycle

---

## Data Integrity Enforcement

All inputs must:

- include artifact_type
- include receipt or seal
- pass schema validation
- match expected domain structure

Failure → immediate rejection

---

## Output Responsibility

This core must produce:

- deterministic outputs
- traceable recommendations
- receipt-linked artifacts

---

## Lifecycle Compliance

Child core must follow:

INIT → INGEST → PROCESS → OUTPUT → TERMINATE

No persistent runtime memory allowed beyond state/current/

---

## PM_CORE Relationship

- PM dispatches execution
- PM validates upstream
- PM receives output artifacts

Child core cannot:

- self-dispatch
- reroute outputs
- bypass PM validation

---

## Registry Requirement

This core is not active until:

- registered in child_core_registry.json
- registered in PM_CORE registry
- routing is confirmed valid

---

## Violation Handling

Any violation triggers:

- immediate termination
- no output emission
- error routed back to PM_CORE