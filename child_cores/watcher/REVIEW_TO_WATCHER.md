# Review to Watcher Contract

## Purpose
Define the lawful interface between Stage 24 CHILD_CORE_REVIEW and
Stage 25 CHILD_CORE_WATCHER.

## Boundary definition
Stage 25 is a watcher intake and watcher execution boundary only.

It begins with:
- `output_disposition_receipt`

It ends with:
- `watcher_result` plus `watcher_receipt`
or
- `watcher_failure_receipt`

No continuity mutation or publication may occur in this stage.

## Inbound artifact
Stage 25 accepts only:
- `output_disposition_receipt`

plus:
- bounded `watcher_context`

## Acceptance conditions
Stage 25 may accept a packet only if:
- packet type is `output_disposition_receipt`
- disposition status is `routed`
- selected target is `watcher_intake`
- target core exists
- watcher readiness evaluates to TRUE

If any condition fails:
- Stage 25 must reject the packet
- emit `watcher_failure_receipt`
- stop propagation

## Inbound fields

### required disposition fields
- `artifact_type`
- `review_id`
- `source_output_id`
- `source_runtime_id`
- `target_core`
- `requested_target`
- `selected_target`
- `disposition_status`
- `timestamp`

## Outbound artifacts
If accepted, Stage 25 emits:
- `watcher_result`
- `watcher_receipt`

## Watcher result purpose
A `watcher_result` is a bounded artifact proving lawful watcher execution
against a reviewed and routed child-core output.

It preserves:
- watcher id
- source review id
- source output id
- target core
- watcher status
- bounded watcher findings or findings reference
- timestamp

It does not preserve:
- PM strategy detail
- full output payload
- continuity state
- publication state

## Failure artifact
If rejected, Stage 25 emits:
- `watcher_failure_receipt`

The failure receipt must include:
- `review_id` if available
- `target_core` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Terminal law
Stage 25 terminates at watcher artifact / receipt emission.

Stage 25 must not:
- update continuity
- publish or deliver artifacts
- reconstruct output artifacts
- rerun review or execution

## Handoff law
Emission of `watcher_receipt` proves:
- lawful watcher intake
- lawful watcher execution completion status

It does not prove:
- continuity update
- publication
- delivery