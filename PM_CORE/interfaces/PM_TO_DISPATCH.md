# PM to Dispatch Interface

## Interface role
This interface formalizes the handoff from PM routing preparation to PM dispatch authorization.

## Source
- PM_ROUTING

## Destination
- PM_DISPATCH

## Allowed source artifact
- `pm_routing_packet`

## Allowed destination artifacts
- `dispatch_packet`
- `dispatch_failure_receipt`

## Interface guarantees
PM_ROUTING guarantees:
- routing intent is explicit
- target shape is explicit
- routing readiness is explicit
- upstream references are present

PM_DISPATCH guarantees:
- dispatch readiness is binary
- invalid dispatch attempts terminate
- ambiguity is not executed
- no multi-core fanout occurs
- no child-core internal execution leakage occurs

## Interface prohibition
This interface does not:
- execute child-core internal logic
- mutate PM routing state
- reinterpret research or PM strategy