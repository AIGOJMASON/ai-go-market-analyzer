# Ingress to Runtime Interface

## Interface role
This interface formalizes the handoff from child-core ingress acceptance to child-core runtime execution.

## Source
- CHILD_CORE_INGRESS

## Destination
- CHILD_CORE_RUNTIME

## Allowed source artifact
- `ingress_receipt`

## Required companion context
- bounded `runtime_context`

## Allowed destination artifacts
- `runtime_receipt`
- `runtime_failure_receipt`

## Interface guarantees
CHILD_CORE_INGRESS guarantees:
- target core is explicit
- ingress was accepted
- destination surface is explicit
- ingress artifact is bounded and lawful

CHILD_CORE_RUNTIME guarantees:
- runtime readiness is binary
- invalid runtime attempts terminate
- no target rewriting occurs
- no execution-surface guessing occurs
- no output-building, watcher, or SMI leakage occurs

## Interface prohibition
This interface does not:
- build final outputs
- run watcher logic
- update continuity state
- reinterpret PM strategy, routing, dispatch, or ingress decisions