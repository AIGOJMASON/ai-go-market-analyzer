# OPERATOR ROUTE STANDARD

## Purpose

This document defines the standard operator route pattern for AI_GO child cores.

It exists to eliminate ambiguity about where the human operator enters a child-core product and to make operator-facing testing consistent across the system.

---

## Standard Route

The canonical operator entrypoint is:

```text
/operator

This route should be treated as the primary human-facing UI surface for a child core unless there is a documented exception.

Why /operator

Using /operator provides four advantages:

1. Explicit Human Entry

It clearly signals that this route is for a human operating the system, not for service discovery or machine-to-machine integration.

2. Stable Test Target

It gives probes and future deployment checks one explicit route to validate.

3. Separation of Concerns

It separates:

service root
health route
machine API routes
operator UI route
4. Reuse Across Child Cores

It allows future child cores to inherit the same entry strategy without re-arguing route layout every time.

Root Route Guidance

The root route / does not need to be the operator UI.

Recommended behavior for root:

service identity
route advertisement
basic service discovery

Example:

{
  "status": "ok",
  "service": "Child Core Name",
  "operator_route": "/operator",
  "health_route": "/healthz"
}

This keeps root stable and low-friction.

Operator Route Responsibilities

The /operator route should:

load the canonical operator UI
expose bounded operator inputs
use the governed API route for submission
render the unified outward system_view
remain free of hidden authority escalation
Operator Route Non-Responsibilities

The /operator route should not:

perform domain logic directly
mutate runtime state outside governed API pathways
expose internal artifacts as separate visible products
replace API contracts
serve as a raw debugging surface
Expected UI Shape

The operator route should render one coherent system view.

Typical visible sections:

Case
Runtime
Recommendation
Cognition
PM Workflow
Governance

The exact wording may vary if justified, but the experience should remain singular and stable.

Testing Standard

Every child core using this route should have an app-level probe that validates:

/operator returns 200
operator page identity is present
required visible sections are present
governed API route is referenced
root advertises /operator where applicable
Divergence Rule

A child core may use a different operator route only if:

the route difference is justified by domain or authority structure
the difference is documented
matching probes are updated accordingly

Aesthetic preference alone is not a sufficient reason.

Summary

/operator is the default AI_GO human entrypoint for child-core products.

It gives the system one reusable, explicit, and testable operator route pattern.