# Child Core Watcher Policy

## Purpose
Define the lawful conditions under which a routed child-core output
becomes watcher-ready for governed watcher execution.

## Policy stance
Watcher readiness is binary.

A packet is either:
- watcher-ready
or
- not watcher-ready and terminated

No partial watcher state is allowed.

## Boundary definition
Stage 25 is a bounded watcher intake and execution layer.

It begins with:
- validated `output_disposition_receipt`

It ends with:
- `watcher_result` plus `watcher_receipt`
or
- `watcher_failure_receipt`

## Binary watcher contract

`watcher_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == output_disposition_receipt`
2. `disposition_status == routed`
3. `selected_target == watcher_intake`
4. `target_core` exists
5. watcher handler exists for target core
6. no watcher blockers are present

If any condition fails:

`watcher_ready = FALSE`

Required outcome:
- emit `watcher_failure_receipt`
- emit no watcher result
- stop propagation

## Required disposition fields
A valid inbound `output_disposition_receipt` must contain:
- `artifact_type`
- `review_id`
- `source_output_id`
- `source_runtime_id`
- `target_core`
- `requested_target`
- `selected_target`
- `disposition_status`
- `timestamp`

## Required watcher context
A valid `watcher_context` may contain:
- `watcher_flags`
- `input_refs`

No large payloads may be carried here.

## Target-core rule
The target core must:
- exist
- be declared in the valid child-core registry

Stage 25 must not guess or replace target core identity.

## Watcher-target rule
The selected target must:
- equal `watcher_intake`
- arrive from lawful Stage 24 review routing

Stage 25 must not accept direct arbitrary watcher invocation.

## Handler rule
The watcher handler must:
- be explicitly declared
- be mapped lawfully to the target core
- be executable
- return bounded watcher data only

Stage 25 must not guess a fallback handler.

## Blocker rule
If any blocker exists:
- packet is not watcher-ready
- watcher execution must not begin

## Artifact rule
If watcher execution succeeds:
- emit `watcher_result`
- emit `watcher_receipt`

If validation or watcher execution fails:
- emit `watcher_failure_receipt`

Artifacts and receipts must remain bounded and operational.

## Compression rule
The watcher receipt must preserve only:
- watcher identity
- source review id
- source output id
- target core
- watcher status
- optional watcher result reference
- timestamp

Do not preserve:
- PM strategy detail
- full output payload
- continuity state
- publication state

## Disallowed behavior
Stage 25 must not:
- update continuity
- publish or deliver artifacts
- rerun review routing
- rebuild output artifacts
- rerun runtime execution
- coordinate multi-core execution
- mutate PM or canon state