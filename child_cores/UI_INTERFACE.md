# UI_INTERFACE — market_analyzer_v1

## Purpose

This document defines the live test CLI/UI surface for market_analyzer_v1.

This surface is for validation and presentation only.
It does not activate production routing and does not create execution authority.

---

## Allowed Functions

The UI test flow may:

- build a lawful PM-style test packet
- run the child core locally
- render dashboard views
- verify watcher status
- print CLI text output
- print UI JSON payload output

---

## Forbidden Functions

The UI test flow may not:

- execute trades
- bypass approval gates
- bypass watcher verification
- ingest raw research directly
- create activation authority
- mutate PM registry status

---

## CLI Test Path

live_test_packet.py
→ execution.run()
→ watcher.verify_runtime_result()
→ outputs.build_output_views()
→ cli_renderer.py
→ terminal output

---

## UI Test Path

live_test_packet.py
→ execution.run()
→ ui_payload_builder.py
→ JSON output

---

## Final Rule

The live CLI/UI flow is a bounded validation harness only.
It is not equivalent to formal activation.