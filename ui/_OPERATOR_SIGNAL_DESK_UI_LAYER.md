AI_GO/ui/_OPERATOR_SIGNAL_DESK_UI_LAYER.md

# OPERATOR SIGNAL DESK UI LAYER

## Purpose

The Operator Signal Desk UI is the human-facing source-intake and dissemination surface for Market Analyzer V1.

It exists because the current operator page is primarily a manual case runner and result viewer.

This new UI layer adds:

- incoming signal visibility
- candidate case visibility
- suggested next steps
- governance-preserving operator readability

---

## Responsibilities

The UI layer is responsible for:

1. collecting bounded source records
2. calling the governed source intake endpoints
3. rendering incoming signals
4. rendering candidate cases
5. surfacing suggestion classes
6. preserving provenance and governance wording

---

## Non-Responsibilities

The UI must never:

- execute trades
- hide governance state
- mutate recommendation logic
- imply autonomy
- fabricate source provenance
- replace the canonical market analyzer analysis route

---

## Primary Sections

The Operator Signal Desk UI should present four sections:

### 1. Source Intake
A bounded form for source record submission.

### 2. Incoming Signals
A readable feed of normalized incoming source records.

### 3. Candidate Cases
Grouped and ranked suggestions derived from the dissemination layer.

### 4. Governance State
A stable reminder that all outputs remain advisory, non-executing, and approval-bound.

---

## Operator Action Model

Allowed visible operator next steps:

- monitor
- review
- analyze
- dismiss

These are workflow postures only.

They are not execution commands.

---

## Design Rule

The UI must favor:

- readability
- explicit provenance
- stable wording
- bounded controls
- compression over raw structural overload

It must not regress into exposing internal PM cognition as a second product.

---

## Relationship to Existing /operator UI

The existing operator page remains the governed manual analysis surface.

This new UI is the governed source-driven intake surface.

Both are lawful.

They solve different operator tasks.

---

## Completion Rule

This UI layer is complete when:

- source intake is human-usable
- signal feed is visible
- candidate suggestions are understandable
- governance remains explicit
- no execution pathway exists