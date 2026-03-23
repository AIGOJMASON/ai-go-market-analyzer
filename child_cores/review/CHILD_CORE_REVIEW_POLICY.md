# Child Core Review Policy

## Purpose
Define the lawful conditions under which a constructed child-core output
becomes review-ready for downstream disposition.

## Policy stance
Review readiness is binary.

A packet is either:
- review-ready
or
- not review-ready and terminated

A review-ready packet may still be:
- routed
or
- held

No partial review state is allowed.

## Boundary definition
Stage 24 is a bounded review and downstream-routing layer.

It begins with:
- validated `output_artifact`

It ends with exactly one of:
- `output_disposition_receipt`
- `review_hold_receipt`
- `review_failure_receipt`

## Binary review contract

`review_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == output_artifact`
2. `output_status == constructed`
3. `target_core` exists
4. review policy exists for target core
5. downstream target is declared and lawful
6. no review blockers are present

If any condition fails:

`review_ready = FALSE`

Required outcome:
- emit `review_failure_receipt`
- stop propagation

## Required output fields
A valid inbound `output_artifact` must contain:
- `artifact_type`
- `output_id`
- `source_runtime_id`
- `target_core`
- `output_surface`
- `output_status`
- `timestamp`

Optional bounded fields may include:
- `payload`
- `payload_ref`

## Required review context
A valid `review_context` must contain:
- `requested_target`

Optional bounded fields may include:
- `review_flags`
- `route_overrides`

The review context must stay small and operational.

## Target-core rule
The target core must:
- exist
- be declared in the valid child-core registry

Stage 24 must not guess or replace target core identity.

## Downstream-target rule
The downstream target must:
- be explicitly declared
- be lawful for the target core
- be routing-only at this stage

Stage 24 may name watcher as a downstream target.
Stage 24 must not execute watcher logic.

## Blocker rule
If any blocker exists:
- packet is not review-ready
- downstream routing must not begin

## Hold rule
A packet may be held if:
- review policy requires hold for the requested target
- review flags explicitly request hold
- route override resolves to `hold`

If held:
- emit `review_hold_receipt`
- do not emit downstream disposition

## Compression rule
The disposition receipt must preserve only:
- review identity
- source output id
- target core
- selected downstream target
- disposition status
- timestamp

Do not preserve:
- PM strategy detail
- full runtime payload
- watcher state
- SMI state
- publication state

## Disallowed behavior
Stage 24 must not:
- trigger watcher execution inline
- update continuity
- publish or deliver artifacts
- rerun output construction
- rerun runtime execution
- coordinate multi-core execution
- mutate PM or canon state