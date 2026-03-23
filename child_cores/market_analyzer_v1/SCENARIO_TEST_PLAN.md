# SCENARIO TEST PLAN — market_analyzer_v1

## Purpose

This document defines the domain-proof phase for market_analyzer_v1.

The goal is to prove not only that the child core runs, but that it behaves sensibly across multiple representative market cases.

---

## Scope

This scenario pack tests:

- valid necessity rebound acceptance
- non-necessity rejection
- rebound validation rejection
- crisis regime classification
- mixed candidate filtering
- unconfirmed shock rejection

---

## Scenario Set

### SCN-01 — valid_energy_rebound
Expected:
- success
- 1 recommendation
- regime = normal
- posture = allowed

### SCN-02 — non_necessity_rejected
Expected:
- failure
- error contains: no necessity-qualified candidates available

### SCN-03 — missing_confirmation_rejected
Expected:
- failure
- error contains: no rebound-validated candidates available

### SCN-04 — crisis_regime_structured_output
Expected:
- success
- 1 recommendation
- regime = crisis
- posture = conditional

### SCN-05 — mixed_candidate_set_filters_correctly
Expected:
- success
- 1 recommendation
- valid candidate survives
- invalid candidates filtered out

### SCN-06 — unconfirmed_shock_rejected
Expected:
- failure
- error contains: shock event is required for recommendation flow

---

## How To Run

### Structured report
```bat
python -m AI_GO.child_cores.market_analyzer_v1.ui.scenario_runner