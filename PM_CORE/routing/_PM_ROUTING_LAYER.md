# PM Routing Layer
## Stage 19 — PM Decision-to-Routing Handoff

### What it is
Stage 19 is the bounded PM decision-to-routing handoff layer.

### Why it exists
PM_STRATEGY forms a governed decision packet.
Stage 19 converts that decision into a routing-ready artifact that downstream routing may consume.

### What it does
- accepts a `pm_decision_packet`
- applies binary routing-readiness validation
- normalizes routing-relevant fields
- emits:
  - `pm_routing_packet`, or
  - `pm_routing_failure_receipt`

### What it does not do
- does not create strategy
- does not rewrite PM continuity
- does not rescore research
- does not reinterpret arbitrator truth
- does not execute routing
- does not activate a child core
- does not mutate canon

### Authority boundary
This layer has translation authority only.

It may:
- validate
- normalize
- compress
- terminate invalid propagation

It may not:
- infer hidden intent
- invent targets
- convert ambiguity into false certainty
- leak into execution

### Core law
No PM decision may propagate into routing unless it satisfies the binary readiness contract.

If readiness fails:
- no routing packet is produced
- a failure receipt is emitted
- propagation terminates at Stage 19

### Inputs
- `pm_decision_packet`

### Outputs
- `pm_routing_packet`
- `pm_routing_failure_receipt`

### State
This layer keeps only minimal live state:
- `last_packet_id`
- `last_timestamp`
- `last_target_set`

No analytics, memory, or long-horizon interpretation belongs here.

### Relationship to adjacent layers
- Stage 18 PM_STRATEGY decides what PM wants
- Stage 19 prepares that intent for routing
- later routing/runtime layers decide how and where execution proceeds