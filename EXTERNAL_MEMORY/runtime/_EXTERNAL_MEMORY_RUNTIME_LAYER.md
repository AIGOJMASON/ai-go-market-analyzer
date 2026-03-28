# EXTERNAL MEMORY RUNTIME LAYER

Purpose:
Provide the lawful runtime-entry surface that allows a live child-core flow
to evaluate governed external information for persistence without mutating
runtime authority, PM authority, or child-core execution authority.

Input -> Output:
live/governed external payload
-> qualification decision
-> persistence result
-> bounded runtime bridge result

This Layer Exists Because:
The admission-side memory gate is now implemented, but the live runtime
still needs a narrow, explicit bridge that can call it without collapsing
the analyzer runtime into storage authority.

Authority Class:
runtime-side bridge only

It May:
- normalize incoming bridge payloads into governed external-memory input
- invoke qualification
- invoke persistence gate
- return bounded receipts and panel-safe summaries

It May Not:
- mutate recommendations
- mutate PM strategy
- mutate SMI continuity
- bypass qualification and write directly to DB
- become the child-core output surface itself

Primary Output:
external_memory_runtime_result

Fields expected in result:
- status
- qualification_decision
- qualification_record
- qualification_receipt
- persistence_receipt
- panel

Panel Purpose:
The panel is a bounded projection only.
It exists so operator-facing responses can display:
- whether the signal was persisted
- why it was rejected
- what source-quality weight and adjusted weight were used

Hard Rule:
Runtime may call EXTERNAL_MEMORY.
Runtime may not absorb EXTERNAL_MEMORY.

This means:
- decision logic remains inside qualification
- storage logic remains inside persistence/db_writer
- runtime only receives the bounded result bundle

Current Phase Scope:
Phase 1 runtime bridge only

Included:
- runtime bridge module
- market-analyzer-specific adapter
- bounded output panel construction

Deferred:
- retrieval-backed reuse
- promotion
- return-path influence into future runtime weighting
- child-core memory retrieval interface