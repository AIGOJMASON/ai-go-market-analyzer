# AI_GO/api/_EVENT_CLASSIFIER_LAYER.md

---

## PURPOSE

Define the governed event classifier layer for Market Analyzer V1.

This layer exists to separate event interpretation from ingress normalization.

The classifier is responsible only for:
- reading bounded ingress context
- assigning one approved event theme
- emitting one auditable classification artifact

It is not responsible for:
- recommendation generation
- PM authority
- confidence mutation
- refinement application
- execution control

---

## CORE RULE

Event interpretation must be explicit, bounded, and inspectable.

Lawful:

raw bounded ingress context
→ classifier
→ event_classification artifact
→ ingress packet assembly

Illegal:
- hidden event interpretation inside downstream logic
- direct recommendation generation from classifier
- undeclared event themes
- non-auditable classification side effects

---

## APPROVED EVENT THEMES

- energy_rebound
- supply_expansion
- geopolitical_shock
- confirmation_failure
- speculative_move
- unknown

---

## CLASSIFIER INPUTS

The classifier accepts bounded normalized ingress context:

- request_id
- symbol
- headline
- price_change_pct
- sector
- confirmation

Optional:
- observed_at
- source

---

## CLASSIFIER OUTPUT

The classifier emits one `event_classification` artifact containing:

- artifact_type
- request_id
- event_theme
- classification_confidence
- signals
- bounded
- sealed

Definitions:

- event_theme
  One approved event category

- classification_confidence
  A bounded label:
  - low
  - medium
  - high

- signals
  Explicit reasons supporting the classification, such as:
  - keyword:mine
  - keyword:chile
  - sector:energy
  - confirmation:none
  - sector:non_necessity

---

## HARD CONSTRAINTS

1. Classifier output must use only approved event themes.
2. Classifier must emit explicit signals.
3. Classifier must remain deterministic.
4. Classifier must not assign recommendation confidence.
5. Classifier must not emit PM output.
6. Classifier must remain auditable and probeable.

---

## PRODUCT INTENT

This layer makes event interpretation visible and testable.

It allows the system to:
- inspect why an event was categorized a certain way
- evolve classifier logic without rewriting ingress
- preserve governance as intelligence expands

---

## WHERE IT CONNECTS

- event_classifier.py
- live_ingress.py
- live_ingress_policy.py
- stage_market_analyzer_v1_event_classifier_b2_probe.py

---

## END