# LOUISVILLE GIS CORE OUTPUT POLICY

## What it is

Output validation policy for `louisville_gis_core`.

## Why it is there

Defines the minimum structure and domain limits for Louisville GIS outputs so child-core outputs remain bounded, inspectable, and non-autonomous.

## Where it connects

- `AI_GO/child_cores/louisville_gis_core/watcher/core_watcher.py`
- `AI_GO/child_cores/louisville_gis_core/outputs/output_builder.py`

---

## Required Output Keys

- `output_type`
- `core_id`
- `recorded_at`
- `source_packet_id`
- `execution_id`
- `status`
- `recommended_next_step`
- `domain_focus`
- `notes`

---

## Output Rules

1. `core_id` must equal `louisville_gis_core`
2. `output_type` must equal `child_core_execution_output`
3. `status` must be a bounded child-core status, not a global completion claim
4. `domain_focus` must equal `louisville_gis`
5. output may recommend review, not autonomous execution