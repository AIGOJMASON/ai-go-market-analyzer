# Implementation Mapping

## CORE
canon:
- lib/canon/root/CORE_DEFINITION.md
runtime:
- core/runtime/cli.py
- core/runtime/router.py
- core/runtime/lifecycle.py
- core/runtime/loader.py
- core/runtime/status.py
state:
- state/runtime/
packets:
- none by default

## SMI
canon:
- lib/canon/root/SMI_DEFINITION.md
runtime:
- core/continuity/smi.py
- core/continuity/continuity_state.py
- core/continuity/unresolved_queue.py
state:
- state/smi/current/
- state/smi/unresolved/
- state/smi/snapshots/

## WATCHER
canon:
- lib/canon/root/WATCHER_DEFINITION.md
runtime:
- core/monitoring/watcher.py
- core/monitoring/verification.py
- core/monitoring/transitions.py
telemetry:
- telemetry/receipts/
- telemetry/transitions/

## SENTINEL
canon:
- lib/canon/root/SENTINEL_DEFINITION.md
runtime:
- core/monitoring/sentinel.py
state:
- state/sentinel/
telemetry:
- telemetry/audits/

## RESEARCH_CORE
canon:
- lib/canon/root/RESEARCH_DEFINITION.md
runtime:
- core/research/intake.py
- core/research/screening.py
- core/research/trust.py
- core/research/packet_builder.py
packets:
- packets/research/

## REFINEMENT
canon:
- lib/canon/contracts/CONTRACT_REFINEMENT_GATE.md
runtime:
- core/refinement/refinement_gate.py
- core/refinement/pm_refinement.py
- core/refinement/reasoning_refinement.py
- core/refinement/narrative_refinement.py
packets:
- packets/refinement/

## PM_CORE
canon:
- lib/canon/root/PM_DEFINITION.md
runtime:
- core/strategy/pm.py
- core/strategy/inheritance.py
- core/strategy/child_core_registry.py
packets:
- packets/inheritance/

## CHILD_CORES
canon:
- lib/canon/root/CHILD_CORE_DEFINITION.md
runtime:
- child_cores/
rule:
- conceptually governed by PM_CORE
- physically implemented in child_cores/