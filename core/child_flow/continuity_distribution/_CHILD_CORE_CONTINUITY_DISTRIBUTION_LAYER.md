# Stage 28 — Child Core Continuity Distribution Layer

## What this layer is

Stage 28 is the first lawful continuity read and distribution boundary.

It consumes:
- `continuity_read_request`

It reads from:
- bounded continuity state written by Stage 27

And it produces:
- `continuity_distribution_artifact`
- `continuity_distribution_receipt`
- `continuity_distribution_hold_receipt`
- `continuity_distribution_failure_receipt`

This layer is the governed read surface for downstream continuity use.

---

## Core Law

Continuity mutation is not continuity distribution.

Stage 27 writes continuity.
Stage 28 reads and packages continuity for lawful downstream use.

Only bounded read requests may access continuity through this layer.

Named consumer profiles do not change that law.
They refine who may read what, and in what shaped form.

---

## Responsibilities

- validate read-request structure
- verify requester legality
- verify target legality
- verify continuity-scope legality
- verify requested view legality
- resolve the requester's named consumer profile
- enforce consumer-profile access rules
- read only allowed continuity records
- shape the returned records according to profile + requested view
- build bounded continuity distribution artifact
- emit fulfilled / hold / failure receipt
- update minimal distribution state
- stop

---

## Named Consumer Profiles

Stage 28 now supports named consumer profiles.

A consumer profile is a bounded read identity that defines:
- allowed requesting surfaces
- allowed target cores
- allowed scopes
- allowed views
- default view
- maximum record count
- shaping rules

Profiles are read controls only.
They do not add strategy authority.
They do not mutate continuity.

---

## Hard Prohibitions

Stage 28 must NOT:
- mutate continuity state
- rerun watcher
- reinterpret execution semantics
- expose raw continuity-store internals
- generate unrestricted store dumps
- publish externally
- execute child-core runtime logic
- bypass distribution policy
- widen scope beyond the request contract
- let profile logic become strategy logic

---

## Boundary Definition

Upstream:
- Stage 27 continuity state / continuity store

Input surface:
- continuity read request

Downstream:
- future continuity consumption layers
- PM / strategy readers
- child-core read surfaces authorized by policy

---

## Design Principle

Stage 28 is a read membrane, not a mutation layer and not a reasoning engine.

It packages approved continuity into bounded artifacts for lawful use.

It does not alter continuity.
It does not create new continuity.
It only serves allowed views of already-governed continuity state.

Named consumer profiles tighten lawful access.
They do not broaden authority.