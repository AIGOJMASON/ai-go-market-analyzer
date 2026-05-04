# PM Routing to Dispatch Contract

## Purpose
Define the lawful interface between Stage 19 PM_ROUTING and Stage 20 PM_DISPATCH.

## Inbound artifact
Stage 20 accepts only:

- `pm_routing_packet`

## Acceptance conditions
Stage 20 may accept a packet only if:
- packet type is `pm_routing_packet`
- routing readiness is `ready`
- target mode is `single`
- target exists
- destination surface exists and is lawful
- dispatch readiness evaluates to TRUE

If any condition fails:
- Stage 20 must reject the packet
- emit `dispatch_failure_receipt`
- stop propagation

## Inbound fields

### required for all packets
- `artifact_type`
- `source_decision_id`
- `intent`
- `target_mode`
- `rationale_summary`
- `upstream_refs`
- `timestamp`
- `routing_readiness`

### additional required for dispatch
- `target`

### not accepted for execution
If `target_mode = candidate_set`
- packet must be rejected for dispatch

## Outbound artifact
If accepted, Stage 20 emits:

- `dispatch_packet`

## Dispatch packet purpose
A `dispatch_packet` is a compressed execution-boundary artifact.

It preserves:
- source decision identity
- source routing identity if available
- dispatch intent
- target core
- destination surface
- upstream references
- dispatch timestamp

It does not preserve:
- full PM strategy
- routing ambiguity
- child-core execution results

## Failure artifact
If rejected, Stage 20 emits:

- `dispatch_failure_receipt`

The failure receipt must include:
- `source_decision_id` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Handoff law
Stage 20 is a dispatch boundary, not a child-core executor.

Emission of `dispatch_packet` grants dispatch visibility only.
It does not perform internal target-core work.