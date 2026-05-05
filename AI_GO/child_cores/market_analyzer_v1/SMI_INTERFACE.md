# SMI_INTERFACE — market_analyzer_v1

## Purpose

This document defines the local SMI surface for market_analyzer_v1.

SMI in this child core is a bounded surface for structured local state inspection,
summary shaping, and continuity-safe reporting.
It is not an authority source and not a learning engine.

---

## Authority Position

Parent authority remains with PM_CORE.

Local SMI may:

- summarize recent child-core execution
- expose structured current-state snapshots
- support watcher-approved continuity recording
- prepare bounded status information for PM-facing inspection

Local SMI may not:

- authorize execution
- rewrite PM truth
- learn from runtime activity
- mutate upstream artifacts
- create activation authority

---

## Allowed Inputs

Local SMI may read:

- watcher-verified execution outputs
- watcher receipts
- state/current/ continuity snapshots
- inheritance_state/ references
- output artifact summaries

All reads are bounded to this child core.

---

## Forbidden Inputs

Local SMI may not rely on:

- raw research streams
- direct user authority
- unverified outputs
- registry mutation requests
- autonomous route decisions

---

## Allowed Outputs

Local SMI may emit:

- child_core_status_summary
- recent_execution_summary
- current_state_snapshot
- continuity_summary

These are informational only.

---

## Runtime Rule

SMI is read-only with respect to prior truth.
It may aggregate and summarize validated local artifacts, but may not alter them.

---

## Final Rule

market_analyzer_v1 SMI exists to expose lawful local clarity, not to create new authority.