# Child Core Output Policy

## Purpose
Define the lawful conditions under which a completed child-core runtime result
becomes output-ready for governed construction.

## Policy stance
Output readiness is binary.

A packet is either:
- output-ready
or
- not output-ready and terminated

No partial output state is allowed.

## Boundary definition
Stage 23 is a bounded output-construction layer.

It begins with:
- validated `runtime_receipt`

It ends with:
- `output_artifact` plus `output_receipt`
or
- `output_failure_receipt`

## Binary output contract

`output_ready = TRUE` only if all conditions below are satisfied:

1. `artifact_type == runtime_receipt`
2. `runtime_status == completed`
3. `target_core` exists
4. output surface is declared
5. output builder exists for target core
6. required bounded result reference is present if builder requires it
7. no output blockers are present

If any condition fails:

`output_ready = FALSE`

Required outcome:
- emit `output_failure_receipt`
- emit no output artifact
- stop propagation

## Required runtime fields
A valid inbound `runtime_receipt` must contain:
- `artifact_type`
- `runtime_id`
- `source_ingress_id`
- `source_dispatch_id`
- `source_decision_id`
- `target_core`
- `execution_surface`
- `runtime_status`
- `timestamp`

Optional bounded fields may include:
- `result_ref`

## Required output context
A valid `output_context` must contain:
- `output_surface`

Optional bounded fields may include:
- `output_flags`
- `input_refs`

The output context must stay small and operational.

## Target-core rule
The target core must:
- exist
- be declared in the valid child-core registry
- match the declared output surface

Stage 23 must not guess or replace target core identity.

## Output-surface rule
The output surface must:
- be explicitly declared
- be mapped lawfully to the target core
- be construction-only
- be reachable through a declared builder

Stage 23 must not guess a fallback output surface.

## Blocker rule
If any blocker exists:
- packet is not output-ready
- output construction must not begin

## Artifact rule
If output construction succeeds:
- emit `output_artifact`
- emit `output_receipt`

If validation or builder invocation fails:
- emit `output_failure_receipt`

Artifacts and receipts must remain bounded and operational.

## Compression rule
The output receipt must preserve only:
- output identity
- source runtime id
- target core
- output surface
- output artifact reference
- output status
- timestamp

Do not preserve:
- PM strategy detail
- routing ambiguity
- full runtime payload
- watcher state
- SMI state

## Disallowed behavior
Stage 23 must not:
- rerun runtime execution
- change target core
- change execution surface
- publish artifacts
- trigger watcher logic
- update SMI or continuity state
- coordinate multi-core execution
- mutate PM or canon state