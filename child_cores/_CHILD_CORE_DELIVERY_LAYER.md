# CHILD CORE DELIVERY LAYER

## Purpose

This layer defines the standard outward delivery pattern for AI_GO child cores.

It exists to ensure that future child cores do not invent new outward product shapes, UI entrypoints, or validation logic from scratch once a lawful and tested delivery pattern has already been proven.

This layer is derived from the frozen Market Analyzer V1 single-surface milestone.

---

## Core Doctrine

A child core may be internally layered, governed, audited, and domain-specific.

Outwardly, it must feel like **one coherent system**.

That means:

- governed internals
- singular outward experience
- stable operator entrypoint
- stable response contract
- stable validation ladder

---

## Canonical Outward Model

Every operator-facing child core should expose one unified outward object:

```json
{
  "status": "ok|rejected|error",
  "request_id": "string",
  "system_view": {
    "case": {},
    "runtime": {},
    "recommendation": {},
    "cognition": {},
    "pm_workflow": {},
    "governance": {}
  }
}

This is the default delivery model unless a child core has a clearly justified reason to diverge.

Required Outward Sections
1. Case

The operator-visible identity of the submitted or evaluated case.

Typical fields:

case_id
title
observed_at
input_mode
2. Runtime

The domain runtime state visible to the operator.

Typical fields:

regime or operating context
event or situation theme
candidate or relevant entity set
bounded runtime summary fields
3. Recommendation

The bounded outward product recommendation or decision-state surface.

Typical fields:

state
count
items
summary

This section must still exist even when no recommendation is present.

4. Cognition

The visible interpretation layer.

Typical fields:

refinement signals
confidence adjustment
risk markers
insight summary
bounded narrative or explanation

This section exposes lawful interpretation, not hidden chain-of-thought.

5. PM Workflow

The outward projection of PM posture.

This section collapses later workflow posture stages into one visible surface.

Typical subsections:

strategy
review
plan
queue
dispatch

These may remain internally separate, but they should not appear outwardly as separate products.

6. Governance

The visible governed state of the child core response.

Typical fields:

mode
route_mode
execution_allowed
approval_required
watcher_passed
closeout_status
receipt lineage
requires_review
Stable Shape Rule

A child core delivery surface must preserve the same top-level shape across:

positive recommendation cases
empty recommendation cases
rejected cases
review-required cases
fallback or zero-record cases

The values may change.
The operator-visible system shape should not fragment.

Delivery Compression Rule

A child core may have many internal layers.

The outward product surface must compress those layers into one coherent operator view.

This is especially important where later internal stages represent:

workflow transformation
posture projection
queue projection
dispatch projection

If those stages do not introduce new outward authority, they should not be shown as separate outward systems.

Canonical Operator Route Rule

Every operator-facing child core should expose a canonical operator entrypoint:

/operator

This creates:

a stable route for testing
a stable route for operator usage
separation between service identity and operator interface
lower ambiguity at app level

Root (/) may remain a service descriptor.
It does not need to be the operator UI.

Root Route Recommendation

The root route should generally provide service identity and route discovery, for example:

{
  "status": "ok",
  "service": "child-core service name",
  "operator_route": "/operator",
  "health_route": "/healthz"
}

This keeps root simple and preserves /operator as the explicit human interface.

UI Doctrine

The operator UI must show one product, not the internal architecture.

The UI should present:

Case
Runtime
Recommendation
Cognition
PM Workflow
Governance

The operator should not be forced to reconstruct the system from multiple screens or internal artifact names.

Governance Invariants

This layer does not weaken governance.

The following must remain preserved in outward delivery:

advisory-only mode where applicable
execution blocking unless explicitly and lawfully changed at system level
no runtime mutation through outward delivery
no PM mutation through outward delivery
watcher and closeout truth remain visible where relevant
no hidden authority escalation through UI or response shape
Non-Responsibilities

This layer does not:

define domain-specific runtime logic
define domain-specific recommendation logic
remove internal PM or governance layering
replace child-core registries or contracts
grant authority
permit execution

It defines delivery shape only.

When to Reuse This Layer

Use this layer when a child core needs:

operator-facing output
API-facing output
a bounded UI
stable human-readable delivery
PM-aware visible state
a reusable testable presentation standard
When to Diverge

A child core may diverge only if:

its domain cannot be represented by the standard sections
the operator-facing workflow would become misleading under the standard model
a different outward model is justified by authority, not aesthetics

Divergence should be explicit and documented.

Minimum Compliance

A child core complies with the delivery layer when it provides:

canonical or justified outward system_view
canonical /operator route
stable section shape
visible governance state
visible cognition layer when present
collapsed PM workflow view when PM workflow exists
matching probe coverage
Summary

This layer turns Market Analyzer’s proven outward delivery pattern into a reusable AI_GO standard.

Future child cores may differ internally.

Outwardly, they should deliver one governed system, not a collection of internal layers.