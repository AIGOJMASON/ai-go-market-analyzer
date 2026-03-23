# PM Routing Policy

## Purpose
Define the lawful conditions under which a PM decision becomes routing-ready.

## Policy stance
Routing readiness is binary.

A packet is either:
- ready for routing handoff
or
- not ready and terminated

No partial readiness state is allowed.

## Binary readiness contract

`routing_ready = TRUE` only if all conditions below are satisfied:

1. `intent_defined == true`
2. `target_mode` is one of:
   - `single`
   - `candidate_set`
3. `target_specification_valid == true`
4. `rationale_bounded == true`
5. `no_unresolved_dependencies == true`

If any condition fails:

`routing_ready = FALSE`

Required outcome:
- emit `pm_routing_failure_receipt`
- emit no routing packet
- stop propagation

## Required decision fields
A valid inbound `pm_decision_packet` must contain:

- `decision_id`
- `intent`
- `target_mode`
- `rationale_summary`
- `upstream_refs`
- `timestamp`

And additionally:

If `target_mode = single`
- `target`

If `target_mode = candidate_set`
- `candidate_targets`
- `candidate_set_controls`

## Target-mode enforcement

### single
Allowed shape:

- `target_mode: single`
- `target: <child_core_id>`

Constraints:
- exactly one target
- target must exist in child-core registry
- `candidate_targets` must be absent

### candidate_set
Allowed shape:

- `target_mode: candidate_set`
- `candidate_targets: [<child_core_id>, ...]`
- `candidate_set_controls`

Constraints:
- minimum candidates: 1
- maximum candidates: `max_candidates`
- no duplicates
- every candidate must exist in child-core registry

## Candidate-set controls
Required structure:

- `max_candidates: N`
- `ranking_required: true | false`

Rules:

If `ranking_required = true`
- candidate list must be ordered highest-priority-first
- Stage 19 preserves order but does not generate ranking

If `ranking_required = false`
- candidate list is treated as unordered
- Stage 19 must not imply a hidden ranking

## Rationale bounding
`rationale_summary` must be small, operational, and routing-relevant.

It must:
- summarize why routing should proceed
- avoid narrative spillover
- avoid strategic re-argument
- preserve source references separately

## Dependency rule
`no_unresolved_dependencies == true` means:
- no required upstream artifact is missing
- no required source reference is absent
- no unresolved blocker is marked as execution-critical

If unresolved dependency exists:
- packet is not routing-ready

## Ambiguity rule
Ambiguity may be preserved only through `candidate_set`.

Ambiguity may not be:
- hidden in prose
- expressed through vague target labels
- converted into false certainty

## Disallowed behavior
Stage 19 must not:
- create new strategy
- infer unstated target preference
- expand candidate set beyond declared maximum
- score candidates unless scoring already exists upstream
- activate child cores
- call runtime router directly as part of validation

## Compression rule
The routing packet must be smaller and more operational than the decision packet.

Preserve:
- decision identity
- intent
- target specification
- bounded rationale
- upstream references

Discard:
- non-routing narrative detail
- strategic exposition not required for dispatch preparation