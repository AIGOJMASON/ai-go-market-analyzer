# ESCALATION DECISION LAYER

## Purpose

The escalation decision layer classifies whether governed escalation is
required after delivery outcome or retry outcome processing.

It consumes a valid outcome receipt and converts it into an escalation
decision artifact.

This layer does not execute escalation.
It does not send notifications.
It does not perform retries.

It only classifies whether escalation is required and under what
approved class and route later layers may act.

---

## Why This Layer Exists

Stage 46 can suggest escalation during failure / retry governance.
Stage 48 records retry outcomes.

But no layer yet exists that answers:

- should the system escalate now
- what escalation class applies
- what escalation route is approved
- whether escalation is required at all

This layer fills that gap.

It provides a governed escalation decision object so later layers can
act without mixing decision logic with escalation action.

---

## Inputs

This layer accepts only:

- Stage 45 delivery outcome receipts
- Stage 48 retry outcome receipts

No transport envelopes, retry decisions, or execution results may be
converted directly into escalation decisions.

---

## Outputs

This layer produces:

- escalation_decision

The decision records:

- which source receipt was consumed
- which source receipt type was consumed
- whether escalation is required
- the escalation class
- the escalation route
- a bounded governance summary

---

## Guarantees

This layer guarantees:

- read-only transformation
- no upstream mutation
- no escalation side effects
- no hidden field leakage
- deterministic decision shaping

---

## Non-Responsibilities

This layer does not:

- perform escalation execution
- notify operators directly
- perform retries
- reopen retry classification
- rewrite source receipts

Those belong to later layers.

---

## Core Rule

An escalation decision is lawful only if:

- the source receipt type is approved
- the source receipt is structurally valid
- the payload class is approved
- the route class is approved
- the execution mode is approved
- relevant adapter classes are approved

If those conditions are not met, decision creation must be rejected.

---

## Classification Rule

For this stage, classification is intentionally narrow:

### From delivery outcome receipt
- result = executed
  -> escalation_required = false
  -> escalation_class = none
  -> escalation_route = none

- result = denied
  -> escalation_required = false
  -> escalation_class = retry_path
  -> escalation_route = retry_governance

- result = failed
  -> escalation_required = true
  -> escalation_class = operator_review
  -> escalation_route = operator_queue

### From retry outcome receipt
- result = retried
  -> escalation_required = true
  -> escalation_class = operator_review
  -> escalation_route = operator_queue

- result = retry_denied
  -> escalation_required = true
  -> escalation_class = policy_block
  -> escalation_route = operator_queue

Any other approved terminal state defaults to:

- escalation_required = false
- escalation_class = none
- escalation_route = none

---

## Role in System

This layer establishes the lawful boundary between:

governed outcome receipts
and
governed escalation posture