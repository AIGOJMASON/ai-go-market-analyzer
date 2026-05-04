# LOUISVILLE GIS CORE INHERITANCE CONTRACT

## What it is

Governed ingress contract for inheritance packets received by `louisville_gis_core`.

## Why it is there

Defines the bounded conditions under which a PM inheritance packet may enter Louisville GIS execution state and prevents raw PM artifacts or malformed ingress receipts from becoming domain execution.

## Where it connects

- `AI_GO/PM_CORE/interfaces/PM_TO_CHILD_CORE.md`
- `AI_GO/PM_CORE/refinement/pm_refinement.py`
- `AI_GO/child_cores/louisville_gis_core/execution/ingress_processor.py`
- `AI_GO/child_cores/louisville_gis_core/inheritance_state/`
- `AI_GO/child_cores/louisville_gis_core/execution/`
- `AI_GO/child_cores/louisville_gis_core/outputs/`

---

## Core Rule

Louisville GIS receives only a governed child-core ingress receipt plus a persisted PM inheritance packet path.

Louisville GIS does not receive:
- raw research packets
- raw PM interpretation artifacts
- unresolved runtime failures
- degraded inheritance attempts
- unpersisted inheritance packets

---

## Eligibility Requirements

A Louisville GIS ingress may activate bounded execution only when all of the following are true:

1. ingress receipt `receiving_authority` is `louisville_gis_core`
2. ingress receipt contains a persisted `inheritance_packet_path`
3. inheritance packet `packet_type` is `pm_inheritance_packet`
4. inheritance packet `inheritance_target` is `child_core_candidate`
5. alignment result is present in the ingress receipt
6. execution remains inside Louisville GIS domain constraints

---

## Execution Rule

Ingress activation does not perform full autonomous domain work.

It only:
- records inheritance state
- creates a bounded execution record
- emits a structured child-core output artifact

Any later domain-specific execution must be versioned separately.

---

## Boundary Rule

PM_CORE decides inheritance truth.
Louisville GIS decides Louisville GIS execution posture inside its own boundary.

Louisville GIS does not rewrite PM inheritance truth.
Louisville GIS does not re-run PM refinement logic.