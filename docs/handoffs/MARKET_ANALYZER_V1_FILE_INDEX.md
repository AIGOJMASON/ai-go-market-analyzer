# MARKET_ANALYZER_V1 — FILE INDEX

This document lists every file created for the `market_analyzer_v1` child core using the standardized template:

Format:
[PATH]
What it is:
Why it is there:
Where it connects:

---

AI_GO/child_cores/market_analyzer_v1/CORE_IDENTITY.md  
What it is: identity definition for the market_analyzer_v1 child core.  
Why it is there: establishes the core’s bounded purpose, authority position, and non-autonomous nature.  
Where it connects: PM_CORE registry, DOMAIN_POLICY.md, OUTPUT_POLICY.md.

---

AI_GO/child_cores/market_analyzer_v1/INHERITANCE_CONTRACT.md  
What it is: contract defining how this core receives upstream data.  
Why it is there: enforces PM-only inheritance and blocks raw research ingestion.  
Where it connects: ingress_processor.py, PM dispatch interface.

---

AI_GO/child_cores/market_analyzer_v1/RESEARCH_INTERFACE.md  
What it is: boundary definition for research interaction.  
Why it is there: prevents direct research ingestion and enforces PM-mediated inputs.  
Where it connects: research/research_interface.py, PM_CORE.

---

AI_GO/child_cores/market_analyzer_v1/SMI_INTERFACE.md  
What it is: definition of local SMI behavior.  
Why it is there: allows read-only summaries without creating authority or learning.  
Where it connects: smi/core_smi.py, watcher output.

---

AI_GO/child_cores/market_analyzer_v1/WATCHER_INTERFACE.md  
What it is: definition of watcher verification responsibilities.  
Why it is there: ensures outputs are validated before continuity is recorded.  
Where it connects: watcher/core_watcher.py, outputs.

---

AI_GO/child_cores/market_analyzer_v1/OUTPUT_POLICY.md  
What it is: output rules for the child core.  
Why it is there: enforces structured, non-narrative, approval-gated outputs.  
Where it connects: outputs/*, recommendation_builder.py.

---

AI_GO/child_cores/market_analyzer_v1/DOMAIN_POLICY.md  
What it is: domain-specific behavioral rules.  
Why it is there: constrains the core to necessity-driven rebound analysis only.  
Where it connects: execution pipeline, DOMAIN_REGISTRY.json.

---

AI_GO/child_cores/market_analyzer_v1/DOMAIN_REGISTRY.json  
What it is: domain registration definition.  
Why it is there: declares allowed actions, forbidden actions, and required artifacts.  
Where it connects: PM registry, execution layer, watcher validation.

---

AI_GO/child_cores/market_analyzer_v1/domains/_DOMAIN_LAYER.md  
What it is: domain layer documentation.  
Why it is there: explains domain boundaries and allowed market behavior.  
Where it connects: DOMAIN_POLICY.md, execution modules.

---

AI_GO/child_cores/market_analyzer_v1/constraints/constraints.json  
What it is: runtime constraint enforcement file.  
Why it is there: enforces non-autonomy, approval gating, and domain limits.  
Where it connects: execution/*, watcher/core_watcher.py.

---

AI_GO/child_cores/market_analyzer_v1/execution/ingress_processor.py  
What it is: ingress validation processor.  
Why it is there: validates PM packets and rejects invalid inputs.  
Where it connects: INHERITANCE_CONTRACT.md, runtime entry.

---

AI_GO/child_cores/market_analyzer_v1/execution/refinement_conditioning.py  
What it is: refinement conditioning adapter.  
Why it is there: applies PM refinement context without mutating truth.  
Where it connects: PM refinement outputs, execution pipeline.

---

AI_GO/child_cores/market_analyzer_v1/execution/market_regime_classifier.py  
What it is: market regime classifier.  
Why it is there: determines normal, volatile, or crisis state.  
Where it connects: event propagation, recommendation builder.

---

AI_GO/child_cores/market_analyzer_v1/execution/event_propagation_classifier.py  
What it is: propagation classifier.  
Why it is there: classifies speed and depth of shock events.  
Where it connects: regime classifier, necessity filter.

---

AI_GO/child_cores/market_analyzer_v1/execution/necessity_filter.py  
What it is: candidate filtering engine.  
Why it is there: restricts candidates to necessity sectors.  
Where it connects: DOMAIN_POLICY.md, rebound validator.

---

AI_GO/child_cores/market_analyzer_v1/execution/rebound_validator.py  
What it is: rebound validation engine.  
Why it is there: enforces stabilization, reclaim, and confirmation phases.  
Where it connects: necessity filter, recommendation builder.

---

AI_GO/child_cores/market_analyzer_v1/execution/recommendation_builder.py  
What it is: trade recommendation builder.  
Why it is there: produces structured, non-executable trade packets.  
Where it connects: output_builder.py, watcher.

---

AI_GO/child_cores/market_analyzer_v1/execution/run.py  
What it is: execution orchestrator.  
Why it is there: coordinates the full runtime pipeline.  
Where it connects: all execution modules, outputs.

---

AI_GO/child_cores/market_analyzer_v1/outputs/output_builder.py  
What it is: output assembler.  
Why it is there: composes all required artifacts into final output.  
Where it connects: execution/run.py, watcher.

---

AI_GO/child_cores/market_analyzer_v1/outputs/market_regime_view.py  
What it is: regime visualization layer.  
Why it is there: presents regime classification.  
Where it connects: market_regime_classifier.py.

---

AI_GO/child_cores/market_analyzer_v1/outputs/active_event_view.py  
What it is: event display layer.  
Why it is there: shows active market shock context.  
Where it connects: event_propagation_classifier.py.

---

AI_GO/child_cores/market_analyzer_v1/outputs/watchlist_view.py  
What it is: filtered candidate view.  
Why it is there: presents necessity-filtered assets.  
Where it connects: necessity_filter.py.

---

AI_GO/child_cores/market_analyzer_v1/outputs/trade_recommendation_view.py  
What it is: recommendation visualization.  
Why it is there: displays structured trade outputs.  
Where it connects: recommendation_builder.py.

---

AI_GO/child_cores/market_analyzer_v1/outputs/receipt_trace_view.py  
What it is: trace visualization layer.  
Why it is there: exposes receipt lineage.  
Where it connects: output_builder.py.

---

AI_GO/child_cores/market_analyzer_v1/outputs/approval_request_view.py  
What it is: approval interface view.  
Why it is there: surfaces human approval requirement.  
Where it connects: recommendation_builder.py.

---

AI_GO/child_cores/market_analyzer_v1/watcher/core_watcher.py  
What it is: output verification engine.  
Why it is there: validates artifacts and enforces approval rules.  
Where it connects: execution outputs, continuity.

---

AI_GO/child_cores/market_analyzer_v1/smi/core_smi.py  
What it is: local summary interface.  
Why it is there: produces bounded status summaries.  
Where it connects: watcher outputs, state/current.

---

AI_GO/child_cores/market_analyzer_v1/research/research_interface.py  
What it is: research validation interface.  
Why it is there: ensures research inputs are PM-inherited only.  
Where it connects: ingress layer.

---

AI_GO/child_cores/child_core_registry.json  
What it is: mirror registry entry.  
Why it is there: tracks child core presence for system visibility.  
Where it connects: PM registry, lifecycle tracking.

---

AI_GO/PM_CORE/state/child_core_registry.json  
What it is: authoritative registry.  
Why it is there: controls lifecycle and activation state.  
Where it connects: PM dispatch, system routing.

---

AI_GO/PM_CORE/interfaces/PM_TO_CHILD_CORE_MARKET_ANALYZER_V1.md  
What it is: PM dispatch contract.  
Why it is there: defines lawful routing into the child core.  
Where it connects: PM_CORE, ingress_processor.py.

---

# END OF FILE INDEX