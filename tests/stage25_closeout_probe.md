# Stage 25 Closeout Probe

## Purpose
Validate that Stage 25 CHILD_CORE_WATCHER performs lawful watcher intake
and watcher execution from routed review state without leaking into continuity
or publication.

## Required pass conditions

1. A valid `output_disposition_receipt` targeted to `watcher_intake` emits:
   - `watcher_result`
   - `watcher_receipt`

2. A disposition receipt with `selected_target != watcher_intake` emits:
   - `watcher_failure_receipt`

3. A crashing watcher handler is contained locally and emits:
  