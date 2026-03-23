# PM to Routing Interface

## Interface role
This interface formalizes the handoff from PM strategic decision to routing preparation.

## Source
- PM_STRATEGY

## Destination
- PM_ROUTING

## Allowed source artifact
- `pm_decision_packet`

## Allowed destination artifacts
- `pm_routing_packet`
- `pm_routing_failure_receipt`

## Interface guarantees
PM_STRATEGY guarantees:
- intent is explicit
- target shape is explicit
- rationale is bounded enough for validation
- upstream references are present

PM_ROUTING guarantees:
- readiness is binary
- invalid packets terminate
- ambiguity is preserved only in structured form
- no execution leakage occurs

## Interface prohibition
This interface does not:
- execute child-core dispatch
- mutate PM decision state
- reinterpret research or arbitrator outcomes