# LOUISVILLE GIS CORE DOMAIN POLICY

## What it is

Domain-boundary policy for `louisville_gis_core`.

## Why it is there

Defines what Louisville GIS may lawfully treat as domain work so the child core does not drift into unrelated business, PM, or system authority.

## Where it connects

- `AI_GO/child_cores/louisville_gis_core/DOMAIN_REGISTRY.json`
- `AI_GO/child_cores/louisville_gis_core/research/research_interface.py`
- `AI_GO/child_cores/louisville_gis_core/watcher/core_watcher.py`
- `AI_GO/child_cores/louisville_gis_core/execution/ingress_processor.py`

---

## Allowed Domain Actions

- `prepare_louisville_gis_review`
- `review_louisville_gis_opportunity`
- `assess_location_intelligence`
- `assess_local_mapping_signal`

---

## Forbidden Domain Actions

- autonomous proposal generation
- PM policy mutation
- child-core creation
- broad business strategy outside Louisville GIS scope
- silent escalation to system-level planning

---

## Core Rule

If an action is not in the allowed set, it is out of domain until versioned explicitly.