# Child Core Ingress Layer
## Stage 21 — Child-Core Ingress / Runtime Boundary

### What it is
Stage 21 is the bounded child-core ingress boundary.

### Why it exists
Stage 20 authorizes dispatch preparation.
Stage 21 determines whether a dispatch packet may lawfully arrive at a target child core and be transferred to that core's declared ingress surface.

This layer is the controlled arrival point between PM dispatch and child-core-local execution.

### What it does
- accepts a `dispatch_packet`
- validates target core and destination surface
- validates ingress readiness
- emits:
  - `ingress_receipt`, or
  - `ingress_failure_receipt`
- hands control to the declared child-core ingress surface

### What it does not do
- does not create PM strategy
- does not rewrite PM routing
- does not rewrite PM dispatch
- does not reinterpret arbitrator truth
- does not perform domain execution beyond ingress transfer
- does not generate final outputs
- does not perform watcher or SMI behavior
- does not mutate canon

### Authority boundary
This layer has ingress-boundary authority only.

It may:
- validate ingress eligibility
- resolve a declared child-core ingress surface
- emit ingress receipts
- terminate invalid propagation
- hand off to lawful ingress surface

It may not:
- invent a new target core
- guess a different destination surface
- perform child-core domain logic after handoff
- coordinate multi-core workflows
- become a runtime orchestrator

### Core law
No dispatch packet may cross into child-core ingress unless ingress readiness is TRUE.

If readiness fails:
- no ingress handoff is performed
- a failure receipt is emitted
- propagation terminates at Stage 21

### Inputs
- `dispatch_packet`

### Outputs
- `ingress_receipt`
- `ingress_failure_receipt`

### State
This layer keeps only minimal live state:
- `last_ingress_id`
- `last_target_core`
- `last_timestamp`

No memory, analytics, routing, strategy, or domain state belongs here.

### Relationship to adjacent layers
- Stage 20 PM_DISPATCH authorizes dispatch
- Stage 21 CHILD_CORE_INGRESS accepts and transfers dispatch into the child-core ingress surface
- later child-core-local runtime layers perform bounded domain execution