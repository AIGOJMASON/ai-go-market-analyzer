# PM Decision to Routing Contract

## Purpose
Define the lawful interface between Stage 18 PM_STRATEGY and Stage 19 PM_ROUTING.

## Inbound artifact
Stage 19 accepts only:

- `pm_decision_packet`

## Acceptance conditions
Stage 19 may accept a packet only if:
- packet type is `pm_decision_packet`
- required fields are present
- target shape conforms to `single` or `candidate_set`
- routing readiness evaluates to TRUE

If any condition fails:
- Stage 19 must reject the packet
- emit `pm_routing_failure_receipt`
- stop propagation

## Inbound fields

### required for all packets
- `decision_id`
- `intent`
- `target_mode`
- `rationale_summary`
- `upstream_refs`
- `timestamp`

### additional if `target_mode = single`
- `target`

### additional if `target_mode = candidate_set`
- `candidate_targets`
- `candidate_set_controls.max_candidates`
- `candidate_set_controls.ranking_required`

## Outbound artifact
If accepted, Stage 19 emits:

- `pm_routing_packet`

## Routing packet purpose
A `pm_routing_packet` is a compressed dispatch-ready handoff.

It preserves:
- source decision identity
- routing intent
- target specification
- bounded rationale
- upstream references
- handoff timestamp

It does not preserve:
- full strategic reasoning
- continuity history
- execution results

## Failure artifact
If rejected, Stage 19 emits:

- `pm_routing_failure_receipt`

The failure receipt must include:
- `decision_id` if available
- failure reason
- failure timestamp
- stage identity
- propagation status = terminated

## Handoff law
Stage 19 is a translator, not an executor.

Emission of `pm_routing_packet` grants routing preparation visibility only.
It does not authorize execution.