# AI_GO/api/_LIVE_INGRESS_LAYER.md

---

## PURPOSE

Define the governed live ingress layer for Market Analyzer V1.

This layer exists to convert bounded external-style market event input into the canonical internal case packet shape already used by the governed PM route and dashboard response system.

The layer is intentionally narrow.

It does not:
- perform execution
- perform model inference
- mutate PM authority
- bypass refinement
- consume raw feeds directly into recommendation logic

It only:
- validate bounded ingress payloads
- normalize raw event-style input
- classify the event into approved internal categories
- emit one governed live_ingress_packet
- hand that packet downstream to the existing PM-owned output path

---

## CORE RULE

All external-style input must become a normalized internal packet before it can influence PM-owned recommendation or dashboard output.

Lawful:

raw external payload
→ schema validation
→ policy validation
→ event classification
→ normalized live_ingress_packet
→ PM route / dashboard

Illegal:
- raw headline directly changing recommendations
- raw price field directly mutating PM confidence
- hidden event classification
- undeclared event themes
- unconstrained external payloads entering the route layer

---

## ACCEPTED INPUT FIELDS

The live ingress layer accepts these bounded fields:

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

## APPROVED SECTORS

- energy
- materials
- utilities
- staples
- industrials
- unknown

---

## APPROVED CONFIRMATION VALUES

- none
- partial
- full

---

## APPROVED EVENT THEMES

- energy_rebound
- supply_expansion
- geopolitical_shock
- confirmation_failure
- speculative_move
- unknown

---

## NORMALIZATION OUTPUT

This layer emits a `live_ingress_packet` containing:

- artifact_type
- request_id
- source
- case_panel
- market_panel
- candidate_panel
- recommendation_seed
- refinement_packets
- rejection_panel
- bounded
- sealed

This packet is the lawful boundary between raw ingress and PM-owned recommendation assembly.

---

## HARD CONSTRAINTS

1. Raw ingress does not create execution authority.
2. Raw ingress does not create learning.
3. Raw ingress does not directly assign recommendation confidence.
4. Raw ingress must use only approved event themes.
5. Raw ingress must preserve explicit rejection state when recommendation conditions are not met.
6. Raw ingress must remain deterministic and auditable.
7. Raw ingress must emit the same shape every time for the same bounded inputs.

---

## PRODUCT INTENT

This layer replaces fixed fixtures as the first real external-style input surface while preserving the governed product architecture already proven in Phase 6.

It allows:
- manual event entry
- future replay ingestion
- future live feed adapter inputs

without changing PM authority, refinement boundaries, or dashboard shape.

---

## WHERE IT CONNECTS

- live_ingress_schema.py
- live_ingress_policy.py
- live_ingress.py
- market_analyzer_api.py
- stage_market_analyzer_v1_live_ingress_b1_probe.py

---

## END