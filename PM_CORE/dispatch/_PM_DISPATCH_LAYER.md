# PM Dispatch Layer
## Stage 20 — Routing-to-Dispatch Execution Boundary

### What it is
Stage 20 is the bounded PM routing-to-dispatch execution boundary.

### Why it exists
Stage 19 determines whether a PM decision is routing-ready.
Stage 20 determines whether that routing packet is execution-eligible for dispatch.

This layer converts a valid `pm_routing_packet` into a dispatch-ready artifact for a lawful downstream destination surface.

### What it does
- accepts a `pm_routing_packet`
- validates dispatch readiness
- validates target and destination surface
- emits:
  - `dispatch_packet`, or
  - `dispatch_failure_receipt`

### What it does not do
- does not create PM strategy
- does not rewrite PM routing
- does not reinterpret arbitrator truth
- does not execute child-core internal work
- does not perform open-ended orchestration
- does not fan out to multiple cores
- does not mutate canon

### Authority boundary
This layer has dispatch-boundary authority only.

It may:
- validate execution eligibility
- resolve a lawful destination surface for a single target
- emit a dispatch artifact
- terminate invalid propagation

It may not:
- infer a new target
- silently resolve ambiguity
- activate multiple targets
- perform child-core work after dispatch handoff

### Core law
No routing packet may cross into dispatch unless dispatch readiness is TRUE.

If readiness fails:
- no dispatch packet is produced
- a failure receipt is emitted
- propagation terminates at Stage 20

### Inputs
- `pm_routing_packet`

### Outputs
- `dispatch_packet`
- `dispatch_failure_receipt`

### State
This layer keeps only minimal live state:
- `last_dispatch_id`
- `last_target`
- `last_timestamp`

No memory, analytics, or orchestration state belongs here.

### Relationship to adjacent layers
- Stage 19 PM_ROUTING prepares a routing-ready handoff
- Stage 20 PM_DISPATCH authorizes dispatch preparation
- later child-core ingress/runtime layers receive the dispatch packet and perform their own bounded work