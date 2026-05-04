# AI_GO/core/visibility/SYSTEM_EYES_PACKET_CONTRACT.md

# SYSTEM EYES PACKET CONTRACT
## AI_GO — Visibility Layer Canon Specification

---

## 1. PURPOSE

System Eyes is the **governed perception layer** for AI_GO.

It converts internal system truth into a single bounded, read-only packet so the AI can understand:

- what exists
- what is active
- what happened
- what was verified
- what is being remembered
- what unresolved pressure is building

System Eyes does NOT provide filesystem access.

System Eyes provides **lawful visibility**.

---

## 2. CORE PRINCIPLE
state + lineage + pressure


NOT:


files + logs + raw outputs


---

## 3. CANONICAL ARTIFACT


AI_GO/state/system_visibility/SYSTEM_EYES_PACKET.latest.json


This is the **single perception artifact** for AI consumption.

---

## 4. NON-NEGOTIABLE RULES


read_only = true
structured_output_only = true
raw_file_dump_allowed = false
mutation_allowed = false
dynamic_query_allowed = false
auditable_generation = true
bounded_recentness_windows = true


---

## 5. TOP-LEVEL CONTRACT

```json
{
  "packet_type": "system_eyes_packet",
  "contract_version": "1.0.0",
  "generated_at": "UTC ISO-8601",
  "system_version": "string",
  "visibility_mode": "read_only",
  "generation_receipt": {},
  "summary": {},
  "runtime_view": {},
  "watcher_view": {},
  "smi_view": {},
  "receipt_view": {},
  "external_memory_view": {},
  "inventory_view": {},
  "pm_workflow_view": {},
  "canon_view": {},
  "anomaly_flags": [],
  "open_pressure": {},
  "next_observable_targets": []
}
6. GENERATION RECEIPT

System Eyes MUST emit its own receipt.

{
  "receipt_id": "eyes_rcpt_...",
  "collector_version": "1.0.0",
  "normalizer_version": "1.0.0",
  "source_windows": {
    "receipts": 10,
    "watcher": 10,
    "smi": 10,
    "external_memory": 10
  },
  "collector_status": "passed",
  "warnings": []
}
7. SUMMARY BLOCK

Fast orientation layer.

{
  "current_stage": "string",
  "system_status": "stable|warning|degraded|unknown",
  "active_child_core_count": 0,
  "recent_failure_count": 0,
  "recent_watcher_failures": 0,
  "recent_unresolved_count": 0,
  "recent_quarantine_count": 0,
  "top_pressure_class": "string|null",
  "most_recent_success_path": "string|null"
}
8. RUNTIME VIEW

What is active now.

{
  "runtime_status": "active|idle|degraded|unknown",
  "current_stage": "string",
  "active_layers": [],
  "active_child_cores": [],
  "active_api_surfaces": [],
  "last_route_mode": "string|null",
  "last_execution_mode": "string|null",
  "last_successful_run": {
    "run_id": "string|null",
    "core_id": "string|null",
    "timestamp": "string|null",
    "status": "string|null",
    "summary": "string|null"
  },
  "runtime_flags": {},
  "open_targets": []
}
9. WATCHER VIEW

Verification truth.

{
  "recent_window_size": 10,
  "pass_count": 0,
  "fail_count": 0,
  "latest_validations": [],
  "failure_classes": [],
  "quarantine_indicators": {
    "count": 0,
    "latest_ids": []
  },
  "closeout_status_summary": {
    "accepted": 0,
    "quarantined": 0,
    "rejected": 0
  }
}
10. SMI VIEW (INTERNAL MEMORY)

Continuity truth.

{
  "continuity_status": "healthy|pressured|degraded|unknown",
  "current_state_summary": {
    "continuity_key_count": 0,
    "active_session_markers": 0,
    "tracked_threads": 0
  },
  "recent_accepted_events": [],
  "recent_change_ledger_entries": [],
  "unresolved_queue": {
    "count": 0,
    "top_classes": [],
    "oldest_open_timestamp": null,
    "latest_entries": []
  },
  "continuity_pressure": {
    "level": "low|medium|high",
    "primary_driver": null
  }
}
11. RECEIPT VIEW

Lineage and causality.

{
  "recent_window_size": 15,
  "latest_runtime_receipts": [],
  "latest_watcher_receipts": [],
  "latest_closeout_receipts": [],
  "latest_external_memory_receipts": [],
  "latest_pm_receipts": [],
  "latest_child_core_receipts": [],
  "lineage_chain_examples": []
}
12. EXTERNAL MEMORY VIEW

Learned world-state.

{
  "record_count": 0,
  "recent_records": [],
  "top_symbols": [],
  "top_event_themes": [],
  "last_retrieval_summary": {},
  "last_promotion_summary": {},
  "strongest_pattern_detected": {}
}
13. INVENTORY VIEW

Bounded structural awareness.

{
  "child_cores_present": [],
  "tests_present": [],
  "handoff_docs_present": [],
  "templates_present": [],
  "key_directories": [],
  "key_registries": [],
  "inventory_counts": {
    "child_cores": 0,
    "tests": 0,
    "handoffs": 0,
    "templates": 0
  }
}
14. PM WORKFLOW VIEW

Unified PM posture surface.

strategy → review → planning → queue → dispatch
{
  "workflow_status": "active|idle|unknown",
  "strategy": {},
  "review": {},
  "planning": {},
  "queue": {},
  "dispatch": {}
}
15. CANON VIEW

Structural truth.

{
  "root_canon_present": true,
  "core_definitions_present": true,
  "child_core_registry_present": true,
  "current_milestone": null,
  "key_timestamps": {},
  "key_hashes": {},
  "canon_health": "aligned|warning|unknown"
}
16. ANOMALY FLAGS
[
  {
    "flag_id": "string",
    "severity": "low|medium|high",
    "class": "string",
    "summary": "string"
  }
]
17. OPEN PRESSURE
{
  "overall_level": "low|medium|high",
  "drivers": []
}
18. NEXT OBSERVABLE TARGETS
[
  {
    "target_type": "string",
    "target_id": "string",
    "reason": "string"
  }
]
19. EMPTY STATE RULE
All sections MUST exist
Use empty arrays or nulls
Never omit fields
20. PROHIBITED CONTENT

System Eyes MUST NOT expose:

raw file contents
full raw receipts
environment variables
secrets
filesystem traversal paths
mutable state blobs
unbounded history
21. PHASE 1 MINIMUM CONTRACT

Required for initial implementation:

{
  "packet_type": "system_eyes_packet",
  "contract_version": "1.0.0",
  "generated_at": "...",
  "system_version": "...",
  "visibility_mode": "read_only",
  "generation_receipt": {},
  "summary": {},
  "runtime_view": {},
  "watcher_view": {},
  "smi_view": {},
  "external_memory_view": {},
  "inventory_view": {}
}
22. FINAL DEFINITION

System Eyes is:

AI_GO self-perception layer

It exposes:

runtime truth
verification truth
continuity truth
lineage truth
structural truth
learned-world truth

Without breaking:

authority boundaries
mutation constraints
governance rules
END OF FILE