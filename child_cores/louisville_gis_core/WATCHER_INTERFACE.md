# LOUISVILLE GIS CORE WATCHER INTERFACE

## What it is

Governed watcher contract for `louisville_gis_core`.

## Why it is there

Defines how Louisville GIS verifies its own bounded execution artifacts after ingress activation so child-core state does not rely on unchecked output.

## Where it connects

- `AI_GO/child_cores/louisville_gis_core/watcher/core_watcher.py`
- `AI_GO/child_cores/louisville_gis_core/execution/ingress_processor.py`
- `AI_GO/child_cores/louisville_gis_core/OUTPUT_POLICY.md`
- `AI_GO/child_cores/louisville_gis_core/outputs/`
- `AI_GO/child_cores/louisville_gis_core/execution/`
- `AI_GO/child_cores/louisville_gis_core/inheritance_state/`

---

## Core Rule

Louisville GIS watcher verifies only child-core artifacts produced inside Louisville GIS boundaries.

It does not:
- re-run PM logic
- re-run research packet screening
- mutate execution artifacts
- create new planning authority

---

## Verification Scope

The watcher verifies:

1. inheritance state exists
2. execution record exists
3. output artifact exists
4. output artifact satisfies Louisville GIS output policy
5. domain action remains allowed by Louisville GIS domain policy

---

## Output

Watcher returns one of:
- `verified`
- `failed`