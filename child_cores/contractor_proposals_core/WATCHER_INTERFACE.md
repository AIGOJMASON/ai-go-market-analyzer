# WATCHER INTERFACE

## What it is

Child-core watcher contract for `contractor_proposals_core`.

## Why it is there

Defines how this child core verifies its own execution artifacts before continuity is recorded.

## Verification Rule

The watcher must verify:
- execution record exists
- output artifact exists
- both artifacts share the same `packet_id`
- both artifacts declare `core_id = contractor_proposals_core`
- output declares `domain_focus = contractor_proposals`

Unchecked execution artifacts may not become continuity truth.