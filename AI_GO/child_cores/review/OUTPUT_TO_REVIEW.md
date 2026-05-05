# Output to Review Contract

## Purpose
Define the lawful interface between Stage 23 CHILD_CORE_OUTPUT and
Stage 24 CHILD_CORE_REVIEW.

## Boundary definition
Stage 24 is a review and downstream-routing boundary only.

It begins with:
- `output_artifact`

It ends with one of:
- `output_disposition_receipt`
- `review_hold_receipt`
- `review_failure_receipt`

No watcher execution, continuity mutation, or publication may occur in this stage.

## Inbound artifact
Stage 24 accepts only:
- `output_artifact`

plus:
- bounded `review_context`

## Acceptance conditions
Stage 24 may accept a packet only if:
- packet type is `output_artifact`
- output status is `constructed`
- target core exists
- requested downstream target exists and is lawful for that core
- review readiness evaluates to TRUE

If any condition fails:
- Stage 24 must reject the packet
- emit `review_failure_receipt`
- stop propagation

## Inbound fields

### required output fields
- `artifact_type`
- `output_id`
- `source_runtime_id`
- `target_core`
- `output_surface`
- `output_status`
- `timestamp`

### required review context fields
- `requested_target`

## Outbound artifacts
If routed, Stage 24 emits:
- `output_disposition_receipt`

If held, Stage 24 emits:
- `review_hold_receipt`

## Disposition receipt purpose
An `output_disposition_receipt` is a bounded artifact proving lawful
post-output review and downstream routing.

It preserves:
- review id
- source output id
- target core
- requested target
- selected target
- disposition status
- timestamp

It does not preserve:
- PM strategy detail
- routing history before Stage 24
- full output payload
- watcher internals
- SMI internals

## Failure artifact
If rejected, Stage 24 emits:
- `review_failure_receipt`

The failure receipt must include:
- `output_id` if available
- `target_core` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Hold artifact
If held, Stage 24 emits:
- `review_hold_receipt`

The hold receipt must include:
- `output_id`
- `target_core`
- hold reason
- requested target
- timestamp
- propagation status = held

## Terminal law
Stage 24 terminates at review receipt emission.

Stage 24 must not:
- execute watcher logic
- update continuity
- publish or deliver artifacts
- reconstruct output artifacts
- rerun execution

## Handoff law
Emission of `output_disposition_receipt` proves:
- lawful review completion
- lawful downstream target selection

It does not prove:
- watcher execution
- continuity update
- publication
- delivery