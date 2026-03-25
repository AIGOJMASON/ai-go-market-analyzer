# AI_GO/api/_PM_INFLUENCE_LAYER.md

---

## PURPOSE

Define the lawful boundary between governed refinement outputs and user-visible product output for Market Analyzer V1.

This layer exists to ensure that refinement does **not** directly control recommendation behavior, recommendation generation, or PM authority. Instead, refinement may only create a **bounded influence record** that PM-owned output surfaces may consume when assembling visible insight.

---

## CORE RULE

Refinement may influence output only through a constrained PM influence layer.

Illegal:
- refinement → direct recommendation mutation
- refinement → direct recommendation generation
- refinement → direct execution gating
- refinement → hidden score override
- refinement → silent confidence drift

Lawful:
- refinement → bounded PM influence record
- PM-owned output assembly consumes influence record
- visible refinement insight is explicit
- original PM recommendation remains preserved in lineage

---

## INPUTS

This layer accepts:

1. recommendation_panel
   - PM-owned recommendation surface
   - contains recommendation_count and recommendation entries

2. refinement_packets
   - governed refinement signals
   - may originate from promoted learning / refinement intake / refinement output routing
   - must already be bounded and safe for output influence use

---

## OUTPUT

This layer emits:

- pm_influence_record

The pm_influence_record may contain:
- visibility status
- influence action
- confidence adjustment class
- bounded visible insight lines
- lineage-safe influence notes
- recommendation-level display confidence changes only

The pm_influence_record must never:
- rewrite entry/exit logic
- invent symbols
- suppress PM recommendations without explicit PM-layer rule
- mutate original recommendation lineage

---

## APPROVED INFLUENCE ACTIONS

- none
- annotation_only
- confidence_reduction
- confidence_increase
- filter_reinforcement

Definitions:

- none
  No visible influence is applied.

- annotation_only
  Adds visible refinement insight without changing displayed confidence.

- confidence_reduction
  Lowers displayed confidence by at most one bounded step.

- confidence_increase
  Raises displayed confidence by at most one bounded step.

- filter_reinforcement
  Adds visible note that an existing PM filter or caution remains supported by historical refinement signals.

---

## HARD CONSTRAINTS

1. Recommendation ownership remains PM-owned.
2. Refinement may not create or remove symbols.
3. Refinement may not change entry/exit logic.
4. Confidence adjustment is bounded to one step only.
5. Original confidence must remain visible in lineage.
6. Visible insight must be explicit and human-readable.
7. Hidden internal fields may not leak into output.

---

## PRODUCT RULE

The user may see:

- recommendation
- displayed confidence
- refinement insight
- influence summary

The user may not see:

- raw learning candidates
- arbitration internals
- promotion internals
- hidden weights
- internal scoring traces
- private refinement fields

---

## WHY THIS LAYER EXISTS

Without this layer, refinement would either:
- remain invisible and product value would be lost, or
- bypass PM authority and become unlawful hidden behavior

This layer prevents both failure modes.

---

## WHERE IT CONNECTS

- pm_influence.py
- operator_dashboard_runner.py
- operator_dashboard_builder.py
- market_analyzer_response.py
- future refinement-intake or refinement-routing surfaces
- Market Analyzer V1 user-visible dashboard assembly

---

## END