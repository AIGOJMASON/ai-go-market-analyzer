# RESEARCH TO PM INTERFACE

## What it is

Governed handoff contract from RESEARCH_CORE into PM_CORE.

## Why it is there

Defines when a research packet is eligible for PM interpretation and prevents raw runtime payloads or degraded research artifacts from bypassing the research boundary.

## Where it connects

- `AI_GO/core/runtime/router.py`
- `AI_GO/PM_CORE/refinement/pm_refinement.py`
- `AI_GO/RESEARCH_CORE/packets/packet_builder.py`
- `AI_GO/docs/contracts/RESEARCH_COMMAND_CONTRACT.md`

---

## Core Rule

PM_CORE receives only a governed research packet plus its bounded research metadata.

PM_CORE does not receive:
- raw command payloads
- unverified packet attempts
- unresolved runtime failures
- continuity-skipped routes

---

## Eligibility Requirements

A research packet may be handed to PM_CORE only when all of the following are true:

1. packet persistence succeeded
2. watcher verification status is `verified`
3. SMI continuity status is `recorded`
4. screening status is `passed`
5. trust class is eligible for PM interpretation

---

## Current Conservative Trust Rule

Until trust escalation policy is separately versioned, PM handoff is allowed only for trust classes in:

- `screened`
- `verified`

All other trust classes remain in RESEARCH_CORE state and do not escalate automatically.

This keeps PM handoff conservative and prevents weak signals from becoming planning directives.

---

## Handoff Output

The PM handoff surface returns one of:

- `accepted`
- `deferred`
- `failed`

### `accepted`
The packet entered PM_CORE and a PM receipt was written.

### `deferred`
The packet remained below PM escalation threshold.
This is not a runtime failure.
It is a lawful non-escalation.

### `failed`
The packet was eligible but PM ingress or receipt writing failed.

---

## Boundary Rule

RESEARCH_CORE decides research truth.
PM_CORE decides planning interpretation.

RESEARCH_CORE does not perform PM reasoning.
PM_CORE does not rewrite research packet truth.