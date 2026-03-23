AI_GO/RESEARCH_CORE/interfaces/RESEARCH_TO_PM.md
What it is: governed interface contract for RESEARCH_CORE to PM_CORE handoff.
Why it is there: defines when a research packet may lawfully escalate into PM interpretation and prevents degraded or raw runtime data from bypassing research boundaries.
Where it connects: router.py, pm_refinement.py, packet_builder.py, and RESEARCH_COMMAND_CONTRACT.md.

AI_GO/PM_CORE/refinement/pm_refinement.py
What it is: PM ingress and refinement acceptance surface for governed research packets.
Why it is there: evaluates whether a verified research packet is eligible for PM interpretation and writes a PM handoff receipt when accepted.
Where it connects: RESEARCH_TO_PM.md, router.py, and AI_GO/PM_CORE/state/receipts/.

AI_GO/core/runtime/runtime_receipt.py
What it is: runtime transaction receipt module.
Why it is there: records PM handoff status and PM receipt path alongside existing runtime, monitoring, and continuity outcomes.
Where it connects: router.py, pm_refinement.py, watcher.py, smi.py, transitions.py, and sentinel.py.

AI_GO/core/runtime/router.py
What it is: runtime orchestration surface for governed command execution.
Why it is there: composes the full research transaction and triggers bounded PM escalation only after research truth, monitoring truth, and continuity truth are all established.
Where it connects: packet_builder.py, watcher.py, smi.py, unresolved_queue.py, transitions.py, sentinel.py, runtime_receipt.py, pm_refinement.py, and RESEARCH_CORE modules.