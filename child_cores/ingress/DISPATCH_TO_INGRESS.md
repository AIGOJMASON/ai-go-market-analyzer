# Dispatch to Ingress Contract

## Purpose
Define the lawful interface between Stage 20 PM_DISPATCH and Stage 21 CHILD_CORE_INGRESS.

## Inbound artifact
Stage 21 accepts only:

- `dispatch_packet`

## Acceptance conditions
Stage 21 may accept a packet only if:
- packet type is `dispatch_packet`
- target core exists
- destination surface exists and is lawful for that target core
- dispatch intent is present
- ingress readiness evaluates to TRUE

If any condition fails:
- Stage 21 must reject the packet
- emit `ingress_failure_receipt`
- stop propagation

## Inbound fields

### required for all packets
- `artifact_type`
- `dispatch_id`
- `source_decision_id`
- `dispatch_intent`
- `target_core`
- `destination_surface`
- `upstream_refs`
- `timestamp`

## Outbound artifact
If accepted, Stage 21 emits:

- `ingress_receipt`

## Ingress receipt purpose
An `ingress_receipt` is a compressed handoff artifact proving lawful arrival at the target child-core ingress surface.

It preserves:
- ingress id
- source dispatch id
- source decision id
- target core
- destination surface
- handoff status
- timestamp

It does not preserve:
- PM strategy detail
- routing history
- child-core execution results

## Failure artifact
If rejected, Stage 21 emits:

- `ingress_failure_receipt`

The failure receipt must include:
- `dispatch_id` if available
- `target_core` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Handoff law
Stage 21 is an ingress boundary, not a domain executor.

Emission of `ingress_receipt` proves lawful ingress transfer only.
It does not prove domain execution success.