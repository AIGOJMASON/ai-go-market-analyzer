# AI_GO/api/_SIGNAL_STACK_LAYER.md

---

## PURPOSE

Define the governed B3 signal stack layer for Market Analyzer V1.

This layer exists to gather already-bounded upstream signals into one explicit artifact before downstream recommendation, refinement, or UI-facing interpretation uses them.

The signal stack is a consolidation layer.

It is responsible for:
- collecting classifier signals
- collecting confirmation signals
- collecting legality signals
- collecting price-direction signals
- emitting one auditable `signal_stack_record`

It is not responsible for:
- recommendation generation
- PM authority
- refinement application
- execution control
- learning

---

## CORE RULE

Distributed bounded signals must be consolidated into one explicit surface before downstream use.

Lawful:

live ingress context
→ classifier artifact
→ signal stack
→ packet assembly
→ PM / refinement / UI

Illegal:
- hidden signal fusion across multiple layers
- undeclared signal weighting
- recommendation logic inside the signal stack
- side-effectful signal interpretation

---

## INPUTS

The signal stack layer accepts bounded upstream context:

1. normalized ingress context
- request_id
- symbol
- headline
- price_change_pct
- sector
- confirmation

2. event classification artifact
- artifact_type
- event_theme
- classification_confidence
- signals
- bounded
- sealed

---

## OUTPUT

The signal stack layer emits one `signal_stack_record` containing:

- artifact_type
- request_id
- event_theme
- classification_confidence
- stack_signals
- stack_summary
- bounded
- sealed

Definitions:

- stack_signals
  A flattened ordered list of bounded signals from all lawful upstream sources

- stack_summary
  A small structured summary showing:
  - price_direction
  - confirmation_state
  - legality_state
  - signal_count

---

## HARD CONSTRAINTS

1. The signal stack must remain deterministic.
2. The signal stack may not generate recommendations.
3. The signal stack may not mutate classifier output.
4. The signal stack may not invent hidden weights.
5. The signal stack must preserve explicit upstream signal lineage.
6. The signal stack must emit a stable artifact for the same bounded input.

---

## PRODUCT INTENT

This layer creates the first governed multi-signal reasoning surface.

It allows the system to:
- inspect all active bounded signals in one place
- expose cleaner downstream interpretation
- expand toward analog reasoning and future stacking without hidden logic

---

## WHERE IT CONNECTS

- signal_stack.py
- live_ingress.py
- market_analyzer_api.py
- stage_market_analyzer_v1_signal_stack_b3_probe.py
- stage_market_analyzer_v1_live_ingress_b3_integration_probe.py

---

## END