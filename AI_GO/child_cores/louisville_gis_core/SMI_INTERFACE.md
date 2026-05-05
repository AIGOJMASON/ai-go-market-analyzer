# LOUISVILLE GIS CORE SMI INTERFACE

## What it is

Governed continuity contract for `louisville_gis_core`.

## Why it is there

Defines how Louisville GIS records its own bounded continuity state after verified execution so the child core can remember lawful domain events without inheriting system-level continuity authority.

## Where it connects

- `AI_GO/child_cores/louisville_gis_core/smi/core_smi.py`
- `AI_GO/child_cores/louisville_gis_core/execution/ingress_processor.py`
- `AI_GO/child_cores/louisville_gis_core/state/current/`
- `AI_GO/child_cores/louisville_gis_core/watcher/core_watcher.py`

---

## Core Rule

Louisville GIS SMI records continuity only after child-core watcher verification succeeds.

It does not:
- replace system continuity
- rewrite PM inheritance truth
- promote child-core outputs upward automatically

---

## Continuity Scope

Louisville GIS SMI records:

1. ingress activation accepted
2. execution record prepared
3. output artifact emitted
4. watcher verification result
5. child-core continuity event