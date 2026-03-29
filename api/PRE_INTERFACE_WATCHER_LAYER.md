# AI_GO/api/_PRE_INTERFACE_WATCHER_LAYER.md

# PRE INTERFACE WATCHER LAYER

## Purpose

This layer is the final watcher boundary before operator-facing interface exposure.

It verifies the fully assembled Market Analyzer V1 system_view payload after runtime, refinement, external-memory return-path, and output-merge work are complete, but before the payload is exposed through the API or operator dashboard.

## Core Rule

This layer is verification only.

It may:
- validate structure
- validate advisory posture
- validate required panels
- detect internal-field leakage
- emit a watcher receipt
- reject unlawful payloads

It may not:
- rescore signals
- mutate recommendations
- mutate PM workflow
- mutate governance state
- mutate refinement or external-memory content
- replan runtime behavior

## Input

One fully assembled operator-facing dashboard payload.

## Output

One `pre_interface_watcher_receipt` artifact.

### Passed outcome
The payload is lawful for interface exposure.

### Failed outcome
The payload is rejected before interface exposure.

## Required invariants

- payload must be dict-like
- required panels must exist
- execution must remain disabled
- mode must remain advisory when present
- internal fields must not leak
- refinement, PM workflow, and external-memory panels are additive only

## Why this exists

Earlier watcher surfaces prove execution truth and runtime closeout truth.

This layer proves interface truth.

Without this layer, the final operator-facing payload could drift even if upstream execution and memory layers were lawful.

## Where it connects

- `AI_GO/api/pre_interface_watcher.py`
- `AI_GO/child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py`
- `AI_GO/tests/stage_market_analyzer_v1_pre_interface_watcher_probe.py`
- `AI_GO/tests/stage_market_analyzer_v1_pre_interface_chain_probe.py`
