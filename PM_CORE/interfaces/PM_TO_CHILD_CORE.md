AI_GO/PM_CORE/refinement/strategic_interpretation.py
What it is: PM strategic interpretation module for accepted research packets.
Why it is there: converts a PM-accepted research packet into a bounded planning interpretation artifact rather than leaving PM meaning implicit.
Where it connects: pm_refinement.py, propagation_rules.py, and AI_GO/PM_CORE/state/active/.

AI_GO/PM_CORE/refinement/propagation_rules.py
What it is: PM propagation decision module.
Why it is there: determines whether a PM interpretation stays inside PM state or becomes eligible for governed inheritance packetization.
Where it connects: strategic_interpretation.py, pm_refinement.py, and inheritance.py.

AI_GO/PM_CORE/inheritance/inheritance_packet_builder.py
What it is: inheritance packet construction and persistence module for PM outputs.
Why it is there: operationalizes PM interpretation into a governed inheritance artifact that can later be handed to child-core interfaces without exposing raw PM state.
Where it connects: inheritance.py, pm_refinement.py, and AI_GO/PM_CORE/state/inheritance/.

AI_GO/PM_CORE/inheritance/inheritance.py
What it is: PM inheritance orchestration surface.
Why it is there: materializes inheritance packets only when PM propagation rules authorize it and keeps inheritance flow separate from PM refinement logic.
Where it connects: inheritance_packet_builder.py, propagation_rules.py, and pm_refinement.py.

AI_GO/PM_CORE/refinement/pm_refinement.py
What it is: PM ingress and refinement orchestration surface for governed research packets.
Why it is there: accepts eligible research packets into PM_CORE, writes PM handoff receipts, triggers strategic interpretation, evaluates propagation, and initiates inheritance packetization when allowed.
Where it connects: RESEARCH_TO_PM.md, strategic_interpretation.py, propagation_rules.py, inheritance.py, router.py, and AI_GO/PM_CORE/state/receipts/.

AI_GO/core/runtime/runtime_receipt.py
What it is: runtime transaction receipt module.
Why it is there: records PM interpretation status, propagation decision, and inheritance packet outputs alongside existing runtime, monitoring, and continuity outcomes.
Where it connects: router.py, pm_refinement.py, strategic_interpretation.py, and inheritance.py.

AI_GO/core/runtime/router.py
What it is: runtime orchestration surface for governed command execution.
Why it is there: composes the full research transaction, triggers bounded PM interpretation after verified handoff, and returns truthful PM and inheritance artifacts without absorbing PM authority.
Where it connects: packet_builder.py, watcher.py, smi.py, unresolved_queue.py, transitions.py, sentinel.py, runtime_receipt.py, pm_refinement.py, and RESEARCH_CORE modules.