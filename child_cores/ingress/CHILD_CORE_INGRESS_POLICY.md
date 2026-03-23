# Child Core Ingress Policy

## Purpose
Define the lawful conditions under which a dispatch packet becomes ingress-ready for a child core.

## Policy stance
Ingress readiness is binary.

A packet is either:
- ingress-ready
or
- not ingress-ready and terminated

No partial ingress state is allowed.

## Binary ingress contract

`ingress_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == dispatch_packet`
2. `target_core` exists
3. `destination_surface` is declared
4. `destination_surface` is lawful for `target_core`
5. `dispatch_intent` is present
6. `upstream_refs` are present
7. `no_ingress_blockers == true`

If any condition fails:

`ingress_ready = FALSE`

Required outcome:
- emit `ingress_failure_receipt`
- emit no ingress handoff
- stop propagation

## Required dispatch fields
A valid inbound `dispatch_packet` must contain:

- `artifact_type`
- `dispatch_id`
- `source_decision_id`
- `dispatch_intent`
- `target_core`
- `destination_surface`
- `upstream_refs`
- `timestamp`

## Target-core rule
The target core must:
- exist
- be declared in the valid child-core registry
- match the destination surface provided in the dispatch packet

Stage 21 must not guess or replace target core identity.

## Destination-surface rule
The destination surface must:
- be explicitly declared in the dispatch packet
- be mapped lawfully to the target core
- be ingress-only
- be reachable through a declared handler

Stage 21 must not guess a fallback destination surface.

## Ingress blocker rule
`no_ingress_blockers == true` means:
- required packet fields are present
- target core is declared
- destination surface is declared and valid
- no explicit ingress blocker is present
- ingress handler exists for the target core

If a blocker exists:
- packet is not ingress-ready

## Receipt rule
If ingress succeeds:
- emit `ingress_receipt`

If ingress fails:
- emit `ingress_failure_receipt`

Receipts must remain small and operational.

## Compression rule
The ingress receipt must preserve only:
- ingress identity
- dispatch identity
- target core
- destination surface
- handoff status
- timestamp

Do not preserve:
- PM strategy detail
- routing ambiguity
- domain execution output

## Disallowed behavior
Stage 21 must not:
- reinterpret dispatch intent
- change target core
- change destination surface
- run domain logic after ingress handoff
- generate final output artifacts
- coordinate multi-core execution
- mutate PM or canon state