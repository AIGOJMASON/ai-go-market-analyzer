# Runtime to Output Contract

## Purpose
Define the lawful interface between Stage 22 CHILD_CORE_RUNTIME and
Stage 23 CHILD_CORE_OUTPUT.

## Boundary definition
Stage 23 is an output-construction and output-completion boundary only.

It begins with:
- `runtime_receipt`

It ends with:
- `output_artifact` plus `output_receipt`
or
- `output_failure_receipt`

No watcher, continuity, or publication activity may occur in this stage.

## Inbound artifact
Stage 23 accepts only:
- `runtime_receipt`

plus:
- bounded `output_context`

## Acceptance conditions
Stage 23 may accept a packet only if:
- packet type is `runtime_receipt`
- runtime status is `completed`
- target core exists
- output surface exists and is lawful for that target core
- output readiness evaluates to TRUE

If any condition fails:
- Stage 23 must reject the packet
- emit `output_failure_receipt`
- stop propagation

## Inbound fields

### required runtime fields
- `artifact_type`
- `runtime_id`
- `source_ingress_id`
- `source_dispatch_id`
- `source_decision_id`
- `target_core`
- `execution_surface`
- `runtime_status`
- `timestamp`

### required output context fields
- `output_surface`

## Outbound artifacts
If accepted, Stage 23 emits:
- `output_artifact`
- `output_receipt`

## Output artifact purpose
An `output_artifact` is a bounded artifact proving lawful construction of
child-core output from completed runtime state.

It preserves:
- output id
- source runtime id
- target core
- output surface
- output status
- bounded output payload or payload reference
- timestamp

It does not preserve:
- PM strategy detail
- routing history
- full runtime internals
- watcher artifacts
- SMI artifacts

## Failure artifact
If rejected, Stage 23 emits:
- `output_failure_receipt`

The failure receipt must include:
- `runtime_id` if available
- `target_core` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Terminal law
Stage 23 terminates at output artifact / receipt emission.

Stage 23 must not:
- publish output artifacts
- trigger watchers
- update SMI or continuity
- rerun execution
- perform downstream routing

## Handoff law
Emission of `output_receipt` proves:
- lawful output construction
- bounded output completion status

It does not prove:
- watcher review
- continuity recording
- publication
- delivery