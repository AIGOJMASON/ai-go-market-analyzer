# SYSTEM VIEW RESPONSE LAYER

## Purpose

This layer defines the canonical outward response surface for operator-facing child-core products that expose governed runtime, refinement, and PM workflow state.

For Market Analyzer V1, the outward response must feel like **one coherent governed system**, not a stack of loosely related layers.

The response surface therefore collapses visible redundancy by presenting:

- case
- runtime
- recommendation
- cognition
- pm_workflow
- governance

as one unified object:

```json
{
  "status": "ok",
  "request_id": "live-001",
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

Key Insight

Stages 19 through 23 do not introduce new authority.
They are progressive transformations of the same PM posture established by earlier PM cognition stages.

Therefore, the outward response must not render them as separate systems.

Instead, they are collapsed into a single visible object:

{
  "pm_workflow": {
    "strategy": "...",
    "review": "...",
    "plan": "...",
    "queue": "...",
    "dispatch": "..."
  }
}
Responsibilities

This layer is responsible for:

defining the canonical outward response envelope
reducing visible redundancy across PM workflow stages
preserving explicit governance and refinement visibility
keeping runtime, cognition, and workflow structurally distinct without making the operator experience fragmented
Non-Responsibilities

This layer does not:

mutate runtime recommendations
grant execution authority
replace internal PM workflow artifacts
remove internal audit lineage
compress or hide governance truth

Internal stages may remain fully separated and receipted.
This layer only governs the outward surface.

Canonical Envelope

All operator-facing responses must follow this shape:

{
  "status": "ok|rejected|error",
  "request_id": "string",
  "system_view": {
    "case": {
      "case_id": "string",
      "title": "string",
      "observed_at": "string|null",
      "input_mode": "fixture|live"
    },
    "runtime": {
      "market_regime": "string",
      "event_theme": "string",
      "macro_bias": "string",
      "headline": "string",
      "candidate_count": 0,
      "candidates": []
    },
    "recommendation": {
      "state": "present|none|rejected",
      "count": 0,
      "items": [],
      "summary": "string"
    },
    "cognition": {
      "refinement": {
        "state": "present|none",
        "signal": "string|null",
        "confidence_adjustment": "up|down|none|null",
        "risk_flag": "string|null",
        "insight": "string|null",
        "narrative": "string|null"
      }
    },
    "pm_workflow": {
      "state": "present|none",
      "strategy": {
        "class": "string|null",
        "strength": "string|null",
        "trend": "string|null",
        "posture": "string|null"
      },
      "review": {
        "class": "string|null",
        "priority": "string|null"
      },
      "plan": {
        "class": "string|null",
        "next_step": "string|null",
        "priority": "string|null"
      },
      "queue": {
        "lane": "string|null",
        "status": "string|null",
        "target": "string|null",
        "priority": "string|null"
      },
      "dispatch": {
        "class": "string|null",
        "target": "string|null",
        "status": "string|null",
        "ready": false
      }
    },
    "governance": {
      "mode": "advisory",
      "route_mode": "string",
      "execution_allowed": false,
      "approval_required": true,
      "watcher_passed": true,
      "closeout_status": "string|null",
      "receipt_id": "string|null",
      "watcher_validation_id": "string|null",
      "closeout_id": "string|null",
      "requires_review": false
    }
  }
}
Display Rule

The operator should see one system.

That system may internally contain:

runtime outputs
refinement packet
PM continuity memory
PM strategy record
PM review record
PM planning record
PM queue record
PM queue index
PM workflow dispatch record

But outwardly, only these surfaces must be presented:

runtime
recommendation
cognition.refinement
pm_workflow
governance
Rejection Handling

Rejected or empty cases must retain the same top-level shape.

The operator must not experience a different contract simply because no recommendation was issued.

Example:

{
  "recommendation": {
    "state": "none",
    "count": 0,
    "items": [],
    "summary": "No recommendation issued."
  }
}
Governance Rule

The single-surface model is a presentation compression only.

It must preserve these invariants:

execution_influence = false
recommendation_mutation_allowed = false
runtime_mutation_allowed = false
Connection Points

This layer connects to:

AI_GO/api/schemas/market_analyzer_response.py
AI_GO/child_cores/market_analyzer_v1/ui/operator_dashboard_builder.py
AI_GO/child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py
AI_GO/ui/_OPERATOR_DASHBOARD_UI_LAYER.md
AI_GO/ui/operator_dashboard_ui.py
AI_GO/api/market_analyzer_api.py
Summary

This layer turns multiple internal governed records into one outward system view.

Internal discipline remains layered.
External experience becomes unified.