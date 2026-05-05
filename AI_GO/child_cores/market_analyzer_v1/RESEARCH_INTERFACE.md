# RESEARCH_INTERFACE — market_analyzer_v1

## Purpose

This document defines how market_analyzer_v1 relates to research surfaces.

The child core does not ingest raw research directly.
It may only consume PM_CORE-inherited, validated, sealed research-derived artifacts.

---

## Authority Position

RESEARCH_CORE is upstream of PM_CORE.
market_analyzer_v1 is downstream of PM_CORE.

Therefore:

- RESEARCH_CORE may inform PM truth
- PM_CORE may package lawful inherited inputs
- market_analyzer_v1 may consume only PM-delivered inheritance packets

---

## Allowed Research Relationship

This child core may receive:

- PM-delivered research_packet derivatives
- PM-delivered event context
- PM-delivered market context
- PM-delivered conditioning derived from refinement

All such inputs must be:

- sealed or receipted
- schema-valid
- domain-relevant
- explicitly routed to market_analyzer_v1

---

## Forbidden Research Relationship

This child core must never:

- ingest raw RESEARCH_CORE output directly
- call external research as authority
- bypass PM validation
- mutate research truth
- reweight research signals
- generate new upstream truth claims

---

## Runtime Rule

Research is inherited input only.

This child core performs application logic on validated market context.
It does not perform independent research adjudication.

---

## Failure Rule

If a packet appears to originate from raw research or lacks PM-delivered authority, the child core must reject ingress and terminate.

---

## Accepted Upstream Artifact Classes

Examples of lawful inherited inputs:

- research_packet
- pm_decision_packet
- refinement_conditioning_packet
- market_case_record
- event_propagation_record
- market_regime_record

Acceptance still requires:

- seal/receipt presence
- artifact schema validity
- PM dispatch targeting this core

---

## Output Relationship

This child core may emit receipted downstream recommendation artifacts.
Those outputs do not redefine research truth.
They apply market_analyzer_v1 domain policy to inherited truth.

---

## Final Rule

market_analyzer_v1 is not a research authority.
It is a bounded execution unit using validated upstream market information.