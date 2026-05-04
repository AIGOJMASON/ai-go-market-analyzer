# WATCHER_INTERFACE — market_analyzer_v1

## Purpose

This document defines local watcher responsibility for market_analyzer_v1.

Watcher verifies that local outputs satisfy structural and policy requirements
before continuity is recorded or downstream trust is assumed.

---

## Authority Position

Watcher is a verification surface, not a decision authority.

Watcher may:

- validate required output artifacts
- validate approval-gate enforcement
- validate receipt/provenance presence
- validate domain-policy compliance
- issue watcher receipts for valid runs

Watcher may not:

- approve trades
- activate the core
- override PM truth
- inject new recommendations
- bypass missing validations

---

## Required Verification Targets

Watcher must verify presence and structure of:

- market_regime_record
- event_propagation_record
- necessity_filtered_candidate_set
- rebound_validation_record
- trade_recommendation_packet
- receipt_trace_packet
- approval_request_packet

Watcher must also verify:

- execution_allowed is false
- approval gate is present
- recommendation outputs are structured
- receipt trace exists

---

## Failure Handling

On failure, watcher must:

- reject verification
- emit a failure result
- prevent continuity write
- prevent watcher success receipt issuance

---

## Continuity Rule

Local continuity may be recorded only after watcher success.

---

## Final Rule

Watcher is the local proof boundary for market_analyzer_v1.
No verified run, no continuity.