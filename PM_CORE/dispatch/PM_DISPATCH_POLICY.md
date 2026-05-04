# PM Dispatch Policy

## Purpose
Define the lawful conditions under which a PM routing packet becomes dispatch-ready.

## Policy stance
Dispatch readiness is binary.

A packet is either:
- dispatch-ready
or
- not dispatch-ready and terminated

No partial readiness state is allowed.

## Binary dispatch contract

`dispatch_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == pm_routing_packet`
2. `routing_readiness == ready`
3. `target_mode == single`
4. `target_specification_valid == true`
5. `destination_surface_valid == true`
6. `no_execution_blockers == true`

If any condition fails:

`dispatch_ready = FALSE`

Required outcome:
- emit `dispatch_failure_receipt`
- emit no dispatch packet
- stop propagation

## Required routing fields
A valid inbound `pm_routing_packet` must contain:

- `artifact_type`
- `source_decision_id`
- `intent`
- `target_mode`
- `rationale_summary`
- `upstream_refs`
- `timestamp`
- `routing_readiness`

And additionally for execution:
- `target`

## Single-target execution rule
Stage 20 permits execution preparation only for `target_mode = single`.

Required shape:
- `target_mode: single`
- `target: <child_core_id>`

Constraints:
- exactly one target
- target must exist in child-core registry
- target must have a lawful destination surface

## Candidate-set execution rule
Stage 20 does not execute ambiguity.

If:
- `target_mode = candidate_set`

Then:
- packet is not dispatch-ready
- Stage 20 must terminate and emit `dispatch_failure_receipt`

Reason:
- unresolved ambiguity may be preserved in routing
- unresolved ambiguity may not be executed in dispatch

## Destination-surface rule
Dispatch requires one known destination surface for the target core.

The destination surface must:
- be explicitly declared
- be valid for the target core
- be execution-ingress only

Stage 20 must not guess a destination surface.

## Execution blocker rule
`no_execution_blockers == true` means:
- no required target is missing
- no required destination surface is missing
- no invalid target mode is present
- no explicit blocker is marked in the routing packet

If a blocker exists:
- packet is not dispatch-ready

## Compression rule
The dispatch packet must remain small and operational.

Preserve:
- source decision identity
- source routing identity if present
- dispatch intent
- target core
- destination surface
- upstream references
- timestamp

Discard:
- non-execution narrative detail
- strategy exposition
- routing-only ambiguity structures

## Disallowed behavior
Stage 20 must not:
- resolve candidate sets through hidden scoring
- change target selection
- re-open PM strategy
- perform child-core internal execution
- dispatch to multiple targets
- create orchestration chains
- call undeclared destination surfaces