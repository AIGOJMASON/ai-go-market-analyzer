# OUTPUT_POLICY — market_analyzer_v1

## Purpose

This document defines the allowable output shape and style for market_analyzer_v1.

Outputs from this child core must be lean, structured, receipted, and non-executing.

---

## Required Output Characteristics

All outputs must be:

- structured
- bounded
- domain-specific
- receipted
- provenance-linked
- approval-gated where applicable

---

## Required Output Artifacts

The child core must be able to produce:

- market_regime_record
- event_propagation_record
- necessity_filtered_candidate_set
- rebound_validation_record
- trade_recommendation_packet
- receipt_trace_packet
- approval_request_packet

The child core may also render dashboard-facing views derived from these artifacts.

---

## Style Rules

Outputs must be:

- non-narrative
- non-promotional
- non-emotional
- non-speculative beyond validated structure

Do not include:

- hype language
- inevitability language
- persuasive trade language
- execution instructions framed as authority

---

## Approval Rule

No output may imply autonomous execution.

All recommendation outputs must preserve:

- execution_allowed = false
- approval_required = true
- approval gate reference = human_trade_approval_record

---

## Trace Rule

Every recommendation surface must carry or reference:

- upstream receipt information
- local artifact trace
- approval request linkage

---

## Failure Rule

If required artifacts or provenance are missing, output must be treated as invalid.

---

## Final Rule

market_analyzer_v1 produces recommendation surfaces only.
It does not produce execution authority.