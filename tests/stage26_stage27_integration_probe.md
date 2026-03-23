AI_GO/core/child_flow/continuity_mutation/_CHILD_CORE_CONTINUITY_MUTATION_LAYER.md

What it is: Stage 27 boundary definition for lawful continuity mutation.
Why it is there: establishes that Stage 27 is the first write boundary after Stage 26 intake and prevents continuity write authority from collapsing back into intake or watcher logic.
Where it connects: consumes Stage 26 continuity_intake_receipt artifacts and feeds downstream continuity readers.

AI_GO/core/child_flow/continuity_mutation/CHILD_CORE_CONTINUITY_MUTATION_POLICY.md

What it is: policy document governing Stage 27 continuity write behavior.
Why it is there: defines the mutation classes, required receipt checks, lineage enforcement, duplicate handling, and bounded write rules so Stage 27 remains deterministic and auditable.
Where it connects: enforced by child_core_continuity_mutation.py and anchored to the Stage 26 → Stage 27 contract.

AI_GO/core/child_flow/continuity_mutation/CONTINUITY_INTAKE_TO_MUTATION.md

What it is: contract document for the Stage 26 to Stage 27 handoff.
Why it is there: freezes the mutation input interface and clarifies that the incoming policy_version is the upstream Stage 26 intake policy version, while Stage 27 records its own mutation policy version separately.
Where it connects: Stage 26 continuity intake upstream and Stage 27 mutation runtime downstream.

AI_GO/core/child_flow/continuity_mutation/continuity_mutation_registry.py

What it is: registry for allowed mutation targets, scopes, and compatible upstream intake policy versions.
Why it is there: prevents unlawful continuity writes and fixes the earlier contract mismatch by separating upstream intake-policy compatibility from Stage 27’s own mutation-policy version.
Where it connects: used by the Stage 27 mutation runtime for target, scope, and policy validation.

AI_GO/core/child_flow/continuity_mutation/continuity_store.py

What it is: bounded continuity persistence store for Stage 27.
Why it is there: provides the first lawful continuity write surface while keeping mutation state narrowly scoped and resettable for testing.
Where it connects: used exclusively by child_core_continuity_mutation.py and Stage 27 probe execution.

AI_GO/core/child_flow/continuity_mutation/continuity_mutation_receipt_builder.py

What it is: receipt builder for successful and failed Stage 27 mutation outcomes.
Why it is there: standardizes mutation receipts and records both upstream intake-policy version and Stage 27 mutation-policy version distinctly.
Where it connects: called by child_core_continuity_mutation.py and validated by the Stage 27 probe.

AI_GO/core/child_flow/continuity_mutation/child_core_continuity_mutation.py

What it is: Stage 27 runtime for lawful continuity write decisions.
Why it is there: validates Stage 26 intake receipts, separates structure, lineage, registry, and upstream policy checks, writes bounded continuity state, and emits deterministic mutation receipts without reinterpreting prior stages.
Where it connects: consumes Stage 26 continuity_intake_receipt, writes to continuity_store.py, and emits receipts via continuity_mutation_receipt_builder.py.

AI_GO/core/child_flow/continuity_mutation/__init__.py

What it is: package export surface for Stage 27 mutation runtime utilities.
Why it is there: exposes the mutation entrypoint and store reset helper cleanly for tests and runtime integration.
Where it connects: imported by the Stage 27 probe and future runtime surfaces.

AI_GO/tests/stage27_closeout_probe.md

What it is: closeout probe definition for Stage 27.
Why it is there: states the full mutation-boundary test set, including created, no-op, invalid input, invalid target, invalid scope, upstream policy mismatch, and broken lineage cases.
Where it connects: governs expected behavior for stage27_child_core_continuity_mutation_closeout_probe.py.

AI_GO/tests/stage27_child_core_continuity_mutation_closeout_probe.py

What it is: executable closeout probe for Stage 27 mutation behavior.
Why it is there: verifies that Stage 27 now accepts valid Stage 26 intake receipts, rejects unlawful or incompatible mutation inputs, and resolves duplicate intake deterministically without relying on the old policy-version mismatch behavior.
Where it connects: tests child_core_continuity_mutation.py, continuity_mutation_registry.py, and continuity_store.py.