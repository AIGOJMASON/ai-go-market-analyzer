# CHILD CORE LAYER

## What it is

The child-core layer contains bounded domain execution units that operate under
PM_CORE inheritance authority.

## Why it is there

This layer exists so AI_GO can perform lawful domain-specific work without
collapsing all execution into PM_CORE or allowing uncontrolled domain drift.

Each child core is a nested governed system with its own:
- identity
- inheritance boundary
- output policy
- domain policy
- watcher verification
- local continuity recording
- bounded execution surface

## Authority Boundaries

Child cores may:
- receive inheritance packets from PM_CORE
- execute within declared domain scope
- emit bounded outputs
- verify local artifacts
- record local continuity after watcher success

Child cores may not:
- accept direct RESEARCH_CORE ingress
- bypass PM_CORE activation rules
- redefine system or PM truth
- self-authorize lifecycle transitions
- act as autonomous agents
- activate refinement engines as authority sources

## Stage 12 Rule

As of Stage 12, no child core is considered lawful merely because it exists on disk.

A lawful child core must:
1. conform to `CHILD_CORE_TEMPLATE_CONTRACT.md`
2. be created through governed creation logic or be brought into compliance
3. pass structural validation
4. pass semantic validation
5. be registered in PM_CORE state
6. be activated through explicit lifecycle transition

## Registry Relationship

Two registry surfaces exist:

### PM_CORE/state/child_core_registry.json
Authoritative lifecycle registry for creation, validation, activation, and retirement.

### child_cores/child_core_registry.json
Mirror inventory of child-core presence for structural inspection and discovery.
This mirror does not override PM_CORE lifecycle truth.

## Required Template Surface

See:
- `CHILD_CORE_TEMPLATE_CONTRACT.md`

## Current Proven Instance

- `louisville_gis_core`

This core is the first proven governed child core and the canonical structural
reference for future child-core instantiation.

## Where it connects

- `AI_GO/PM_CORE/child_core_management/child_core_registry.py`
- `AI_GO/PM_CORE/child_core_management/core_creation.py`
- `AI_GO/PM_CORE/child_core_management/core_retirement.py`
- `AI_GO/PM_CORE/refinement/pm_refinement.py`
- `AI_GO/PM_CORE/interfaces/PM_TO_CHILD_CORE.md`
- child-core-local watcher, SMI, research, execution, and output surfaces