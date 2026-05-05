# Child Core Runtime Policy

## Purpose
Define the lawful conditions under which an ingress-approved handoff becomes runtime-ready for a child core.

## Policy stance
Runtime readiness is binary.

A packet is either:
- runtime-ready
or
- not runtime-ready and terminated

No partial runtime state is allowed.

## Binary runtime contract

`runtime_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == ingress_receipt`
2. `target_core` exists
3. `execution_surface` is declared
4. `execution_surface` is lawful for `target_core`
5. `runtime_context` is present
6. `no_runtime_blockers == true`
7. declared execution handler exists

If any condition fails:

`runtime_ready = FALSE`

Required outcome:
- emit `runtime_failure_receipt`
- emit no runtime handoff
- stop propagation

## Required ingress fields
A valid inbound `ingress_receipt` must contain:

- `artifact_type`
- `ingress_id`
- `source_dispatch_id`
- `source_decision_id`
- `target_core`
- `destination_surface`
- `handoff_status`
- `timestamp`

## Required runtime context
A valid `runtime_context` must contain:

- `execution_surface`

Optional bounded fields may include:
- `input_refs`
- `runtime_flags`

The runtime context must stay small and operational.

## Target-core rule
The target core must:
- exist
- be declared in the valid child-core registry
- match the declared execution surface provided by runtime context

Stage 22 must not guess or replace target core identity.

## Execution-surface rule
The execution surface must:
- be explicitly declared in runtime context
- be mapped lawfully to the target core
- be execution-only
- be reachable through a declared handler

Stage 22 must not guess a fallback execution surface.

## Handoff-status rule
`handoff_status` must equal `accepted`.

If ingress was not accepted:
- packet is not runtime-ready

## Runtime blocker rule
`no_runtime_blockers == true` means:
- required fields are present
- target core is declared
- execution surface is declared and valid
- no explicit runtime blocker is present
- execution handler exists for the target core

If a blocker exists:
- packet is not runtime-ready

## Receipt rule
If runtime start succeeds:
- emit `runtime_receipt`

If runtime validation or invocation fails:
- emit `runtime_failure_receipt`

Receipts must remain small and operational.

## Compression rule
The runtime receipt must preserve only:
- runtime identity
- source ingress id
- source dispatch id
- target core
- execution surface
- runtime status
- optional bounded result reference
- timestamp

Do not preserve:
- PM strategy detail
- routing ambiguity
- full domain output payload
- watcher state
- SMI state

## Disallowed behavior
Stage 22 must not:
- reinterpret dispatch or ingress intent
- change target core
- change execution surface
- build final output artifacts
- run watcher logic
- update SMI or continuity state
- coordinate multi-core execution
- mutate PM or canon state