# AI_GO/api/_PRE_INTERFACE_SMI_LAYER.md

# PRE INTERFACE SMI LAYER

## Purpose

This layer is the final continuity boundary before operator-facing interface exposure.

It records one lawful continuity event after the final pre-interface watcher passes, preserving what was actually shown to the operator without reopening runtime or recommendation authority.

## Core Rule

This layer is continuity only.

It may:
- record verified interface exposure
- record visible panel composition
- record advisory posture
- record recommendation count
- record rejection presence
- emit a continuity record

It may not:
- decide visibility policy
- mutate payload structure
- alter recommendations
- re-run refinement
- re-run external-memory promotion
- grant new runtime influence

## Input

- one fully assembled operator-facing dashboard payload
- one passed `pre_interface_watcher_receipt`

## Output

One `pre_interface_smi_record` artifact.

## Required invariants

- watcher receipt must be passed
- continuity record must preserve advisory-only posture
- continuity record must be additive only
- continuity record must not mutate source payload
- continuity record must remain bounded to interface exposure facts

## Why this exists

Earlier SMI surfaces preserve runtime and child-core continuity.

This layer preserves interface continuity.

It records what the operator actually saw, under what posture, and after what final watcher status.

## Where it connects

- `AI_GO/api/pre_interface_smi.py`
- `AI_GO/child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py`
- `AI_GO/tests/stage_market_analyzer_v1_pre_interface_smi_probe.py`
- `AI_GO/tests/stage_market_analyzer_v1_pre_interface_chain_probe.py`