# MARKET ANALYZER V1
# STAGE 25 — SOURCE INTAKE + DISSEMINATION HANDOFF

## 1. Purpose

Stage 25 adds the missing front-half product layer for Market Analyzer V1:

- source intake
- source normalization
- signal clustering
- candidate suggestion
- operator inbox visibility

This stage exists because the current live operator page is primarily a governed case runner and result viewer.

That surface is correct, but it does not yet function as a source-driven operator desk.

---

## 2. What This Stage Adds

### New governed backend surfaces

- `source_registry.py`
- `source_ingress_schema.py`
- `source_normalizer.py`
- `source_clusterer.py`
- `source_dissemination.py`
- `source_signal_desk.py`

### New operator-facing UI surface

- `/operator/signal-desk`

### New validation probes

- `stage_market_analyzer_v1_source_intake_probe.py`
- `stage_market_analyzer_v1_source_dissemination_probe.py`

---

## 3. Operator Problem Solved

Before Stage 25:

- operator manually builds one case
- system analyzes that case
- system returns governed advisory output

After Stage 25:

- operator can ingest bounded source items
- system normalizes incoming source items
- system groups related source records
- system surfaces candidate cases
- system suggests bounded workflow posture:
  - monitor
  - review
  - analyze
  - dismiss

This turns the product from a manual analysis runner into a source-aware operator desk.

---

## 4. Governance Posture

Stage 25 does not change the core invariants.

The following remain true:

- `execution_influence = false`
- `recommendation_mutation_allowed = false`
- `runtime_mutation_allowed = false`

This stage only creates suggestion artifacts and operator visibility.

No trade authority is introduced.

---

## 5. Canonical Flow

```text
source item
    ↓
source registry validation
    ↓
source normalization
    ↓
signal clustering
    ↓
candidate dissemination
    ↓
operator inbox visibility
    ↓
optional downstream governed analysis
6. Output Artifacts

This stage emits four bounded artifacts:

source_signal_record
source_cluster_record
source_candidate_record
source_inbox_record

All are sealed, explicit, and advisory-only.

7. Operator UI Role

The /operator/signal-desk page is intended to expose:

Source Intake
Incoming Signals
Candidate Cases
Governance State
Raw Inbox Record

The page is readable by design and preserves bounded wording.

It does not expose execution, hidden learning, or recommendation mutation.

8. Relationship to Existing /operator Page

The existing /operator page remains the governed manual analysis surface.

The new /operator/signal-desk page is the governed source-driven intake and dissemination surface.

These two pages are complementary:

/operator = analyze a case
/operator/signal-desk = discover candidate cases
9. What Still Remains Outside This Stage

This stage does not yet:

mount itself into the root app automatically
connect source candidates directly into /market-analyzer/run/live
persist source artifacts to a durable receipt store
perform cross-session retention

Those are later hardening and routing steps.

Stage 25 is specifically the additive governed source desk.

10. Final Outcome

Stage 25 closes the product gap between:

governed analysis
governed discovery

That gap was the main reason the current UI felt like a polished runner rather than a real operator desk.

This stage fixes that without violating system law.