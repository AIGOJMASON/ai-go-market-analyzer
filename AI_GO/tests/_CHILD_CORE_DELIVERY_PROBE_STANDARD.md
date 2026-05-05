# CHILD CORE DELIVERY PROBE STANDARD

## Purpose

This document defines the minimum probe ladder for any AI_GO child core that adopts the standard single-surface delivery pattern.

It exists to ensure that outward delivery is not considered complete merely because one route appears to work.

A lawful delivery surface must be validated from schema through mounted app.

---

## Probe Ladder

A compliant child core should provide the following probe classes.

---

## 1. Response Contract Probe

### Purpose
Validate the canonical outward response model at the schema or response-builder level.

### What it should prove
- top-level shape is correct
- `system_view` exists
- required sections exist
- state defaults behave correctly
- empty and rejected cases preserve stable shape
- PM workflow collapse behaves as intended

### Typical naming pattern
```text
stage_<child_core>_system_view_response_probe.py
2. Operator UI Contract Probe
Purpose

Validate that the standalone operator UI surface renders the intended single-system presentation.

What it should prove
operator page renders
required visible sections are present
unified system phrasing exists
governed live endpoint is referenced
the UI does not visibly split PM posture into multiple products
Typical naming pattern
stage_<child_core>_operator_ui_system_view_probe.py
3. API Integration Probe
Purpose

Validate that the routed API returns the unified outward contract end-to-end.

What it should prove
/run works
/run/live works when relevant
system_view survives actual route integration
cognition and governance projections survive
rejected cases retain stable outward shape
Typical naming pattern
stage_<child_core>_api_system_view_integration_probe.py
4. App-Level Integration Probe
Purpose

Validate that the mounted FastAPI app still preserves the delivery pattern when the full app is exercised.

What it should prove
app boots
root or health route exists
run routes function through mounted app
unified system_view survives through the real app path
cognition, PM workflow, and governance remain present
rejected cases remain stable
Typical naming pattern
stage_<child_core>_app_system_view_probe.py
5. Golden Cases Probe
Purpose

Validate product truth, not just structural truth.

What it should prove
positive case behaves correctly
rejection case behaves correctly
blocked or empty case behaves correctly
review-required case preserves governance truth
zero-record fallback preserves stable outward shape
Typical naming pattern
stage_<child_core>_system_view_golden_cases_probe.py
6. Operator Route Probe
Purpose

Validate the canonical /operator entrypoint.

What it should prove
/operator loads
visible unified sections are present
governed live API route is referenced
root advertises /operator if root advertises service routes
Typical naming pattern
stage_<child_core>_operator_route_probe.py
Minimum Passing Standard

A child core should not be considered delivery-complete until:

all applicable probe classes exist
all applicable probes pass
the probe results cover both structural and behavioral truth
Stable Shape Rule

Probes should verify that the same outward contract shape survives across:

positive cases
rejected cases
empty cases
review-required cases
fallback cases

The child core may vary values.
It should not vary outward system shape without justification.

Governance Rule

Delivery probes must confirm that outward unification does not erase governance.

At minimum, they should verify where applicable:

advisory mode remains intact
execution blocking remains intact
approval requirements remain visible
watcher truth survives
closeout state survives
no outward mutation path is introduced
Reuse Rule

Future child cores adopting the standard delivery pattern should reuse this ladder rather than inventing ad hoc probe stacks.

Domain-specific cases can change.
The ladder itself should remain stable.

Summary

A child core delivery surface is only truly complete when it passes the full probe ladder from response schema to mounted app and operator route.

This standard turns delivery validation into a reusable system pattern rather than a one-off effort.