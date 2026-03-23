# Child Core Watcher Layer

## Purpose
Stage 25 is the governed watcher intake and watcher execution boundary for child cores.

It transforms a lawful Stage 24 `output_disposition_receipt` targeted to
`watcher_intake` into bounded watcher artifacts under strict watcher policy.

## Position in flow
The execution chain is:

PM decision
→ routing
→ dispatch
→ ingress
→ runtime
→ output construction
→ review and downstream routing
→ watcher intake and execution

Stage 25 begins only after Stage 24 has emitted a lawful
`output_disposition_receipt` with `selected_target = watcher_intake`.

## Core rule
Watcher intake is not continuity. Watcher execution is not publication.

Stage 25 may:
- validate watcher readiness
- resolve a declared watcher handler
- invoke watcher execution
- emit `watcher_result`
- emit `watcher_receipt`
- emit `watcher_failure_receipt`

Stage 25 must not:
- rebuild outputs
- rerun execution
- rerun review routing
- update SMI or continuity
- publish or deliver artifacts
- change target core
- reinterpret upstream decisions

## Input
Stage 25 accepts:
- `output_disposition_receipt`
- bounded `watcher_context`

## Output
On success, Stage 25 emits:
- `watcher_result`
- `watcher_receipt`

On failure, Stage 25 emits:
- `watcher_failure_receipt`

## Minimal state
Stage 25 stores only:
- `last_watcher_id`
- `last_target_core`
- `last_timestamp`
- `last_watcher_status`

No continuity state, publication state, or payload history
may accumulate here.

## Authority boundary
Stage 25 owns:
- watcher readiness validation
- watcher handler selection
- watcher execution
- watcher receipt emission

Stage 25 does not own:
- runtime execution
- output reconstruction
- review routing
- continuity mutation
- publication or delivery