# PM_TO_CHILD_CORE — market_analyzer_v1

## Purpose

This document defines the PM dispatch contract for routing lawful work to market_analyzer_v1.

---

## Route Target

core_id: market_analyzer_v1

Parent authority: PM_CORE

Lifecycle requirement: core must be active in PM_CORE/state/child_core_registry.json before runtime routing is lawful.

---

## Allowed Dispatch Packet Characteristics

PM may dispatch to this core only when the packet:

- is sealed or receipted
- identifies PM_CORE as dispatcher
- identifies market_analyzer_v1 as target_core
- contains lawful inherited market context
- contains no raw direct RESEARCH_CORE ingress
- conforms to child-core ingress schema

---

## Expected Dispatch Purpose

PM uses this route when it wants:

- necessity-sector rebound evaluation after a shock event
- market regime classification
- event propagation classification
- candidate filtering and rebound validation
- structured recommendation packet generation
- approval-gated market dashboard output

---

## Route Prohibitions

PM must not use this route to request:

- direct trade execution
- unrestricted market research
- long-term portfolio management
- multi-strategy autonomous trading
- raw research adjudication inside the child core

---

## Output Return Surface

The child core returns bounded artifacts only.

Expected return artifacts include:

- market_regime_record
- event_propagation_record
- necessity_filtered_candidate_set
- rebound_validation_record
- trade_recommendation_packet
- receipt_trace_packet
- approval_request_packet

---

## Final Rule

PM dispatch provides authority to evaluate and recommend within domain scope only.
It does not delegate execution authority.