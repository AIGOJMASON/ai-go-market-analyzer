# PM Dispatch to Child Core Interface

## Interface role
This interface formalizes the handoff from PM dispatch authorization to child-core ingress acceptance.

## Source
- PM_DISPATCH

## Destination
- CHILD_CORE_INGRESS

## Allowed source artifact
- `dispatch_packet`

## Allowed destination artifacts
- `ingress_receipt`
- `ingress_failure_receipt`

## Interface guarantees
PM_DISPATCH guarantees:
- dispatch intent is explicit
- target core is explicit
- destination surface is explicit
- upstream references are present

CHILD_CORE_INGRESS guarantees:
- ingress readiness is binary
- invalid ingress attempts terminate
- no target rewriting occurs
- no destination-surface guessing occurs
- no domain execution leakage occurs beyond ingress handoff

## Interface prohibition
This interface does not:
- execute child-core domain logic
- mutate PM dispatch state
- reinterpret research, PM strategy, or PM routing