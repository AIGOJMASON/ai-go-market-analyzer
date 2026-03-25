# OPERATOR DASHBOARD UI LAYER

## Purpose

This layer defines the canonical operator-facing UI surface for Market Analyzer V1.

The canonical entrypoint is:

```text
/operator

This route exists so the operator dashboard has an explicit, stable, and testable surface independent from any root-level service page.

The operator UI must present one coherent governed system view, not a scattered set of internal PM layers.

Canonical Route

The operator-facing dashboard is mounted at:

/operator

Optional root-level routes may still exist for service identity or health presentation, but they are not the canonical operator interface.

Outward Model

The UI must render the canonical single-surface response object:

{
  "status": "ok",
  "request_id": "string",
  "system_view": {
    "case": {},
    "runtime": {},
    "recommendation": {},
    "cognition": {
      "refinement": {}
    },
    "pm_workflow": {},
    "governance": {}
  }
}
Core Rule

The operator should experience one system.

Stages 19 through 23 may remain internally distinct, but outwardly they are rendered as one unified pm_workflow surface.

Responsibilities

This layer is responsible for:

providing a stable operator entrypoint
collecting bounded operator input
calling the governed live API route
rendering the unified system_view
presenting runtime, cognition, PM workflow, recommendation, and governance in one coherent page
Non-Responsibilities

This layer does not:

perform recommendation logic
perform PM cognition logic
mutate runtime or PM state
grant execution authority
expose internal workflow artifacts as separate visible products
bypass governed ingress contracts
Required Visible Sections

The /operator dashboard must present these sections:

Case
Runtime
Recommendation
Cognition
PM Workflow
Governance
Stable Shape Rule

The operator-facing page must preserve the same top-level sections for:

positive recommendation cases
empty recommendation cases
rejected cases
review-required cases

The values may differ.
The visible system shape should not fragment.

Route Rule

The /operator page is the canonical UI route for app-level testing and operator usage.

App-level probes should validate /operator rather than assuming / serves the same dashboard markup.

Summary

This layer gives the Market Analyzer product one explicit operator entrypoint.

Internal architecture remains governed and layered.
Operator experience becomes stable, singular, and testable.