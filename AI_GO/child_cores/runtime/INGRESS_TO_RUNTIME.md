# Ingress to Runtime Contract

## Purpose
Define the lawful interface between Stage 21 CHILD_CORE_INGRESS and Stage 22 CHILD_CORE_RUNTIME.

## Boundary Definition
Stage 22 is a **runtime-start and runtime-completion boundary only**.

It begins with:
- `ingress_receipt`

It ends with:
- `runtime_receipt` OR `runtime_failure_receipt`

No execution may extend beyond this boundary.

## Inbound artifact
Stage 22 accepts only:

- `ingress_receipt`

plus:

- bounded `runtime_context`

## Acceptance conditions
Stage 22 may accept a packet only if:
- packet type is `ingress_receipt`
- handoff status is `accepted`
- target core exists
- execution surface exists and is lawful for that target core
- runtime readiness evaluates to TRUE

If any condition fails:
- Stage 22 must reject the packet
- emit `runtime_failure_receipt`
- stop propagation

## Inbound fields

### required ingress fields
- `artifact_type`
- `ingress_id`
- `source_dispatch_id`
- `source_decision_id`
- `target_core`
- `destination_surface`
- `handoff_status`
- `timestamp`

### required runtime context fields
- `execution_surface`

## Outbound artifact
If accepted, Stage 22 emits:

- `runtime_receipt`

## Runtime receipt purpose
A `runtime_receipt` is a compressed artifact proving lawful start and bounded completion of child-core execution.

It preserves:
- runtime id
- source ingress id
- source dispatch id
- source decision id
- target core
- execution surface
- runtime status
- optional bounded result reference
- timestamp

It does not preserve:
- PM strategy detail
- routing history
- full child-core execution payload
- output artifacts

## Failure artifact
If rejected, Stage 22 emits:

- `runtime_failure_receipt`

The failure receipt must include:
- `ingress_id` if available
- `target_core` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Terminal Law
Stage 22 **terminates at runtime receipt emission**.

Stage 22 must not:
- construct output artifacts
- call output builders
- trigger watchers
- update SMI or continuity
- perform publication

Any attempt to extend beyond runtime_receipt is a boundary violation.

## Handoff Law
Emission of `runtime_receipt` proves:
- lawful execution start
- bounded execution completion status

It does not prove:
- output construction
- output validation
- publication