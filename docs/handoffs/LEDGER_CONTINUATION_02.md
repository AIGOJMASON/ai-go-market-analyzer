# MARKET_ANALYZER_V1 — LEDGER CONTINUATION (DOMAIN PROOF PHASE)

This ledger continues from the previous entry and records all files created for:

- scenario validation layer
- domain proof testing
- historical replay framework

Format:
[PATH]
What it is:
Why it is there:
Where it connects:

---

AI_GO/child_cores/market_analyzer_v1/ui/scenario_packets.py  
What it is: scenario input generator containing structured synthetic test cases.  
Why it is there: provides deterministic, repeatable domain inputs to validate strategy logic beyond structural correctness.  
Where it connects: scenario_runner.py, execution/run.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/scenario_expectations.py  
What it is: expectation mapping for each scenario case.  
Why it is there: defines pass/fail criteria for domain behavior validation.  
Where it connects: scenario_runner.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/scenario_runner.py  
What it is: scenario execution engine.  
Why it is there: runs all scenarios through the core, evaluates outputs, and compares against expectations.  
Where it connects: execution/run.py, output_builder.py, watcher/core_watcher.py, scenario_packets.py, scenario_expectations.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/scenario_cli_report.py  
What it is: human-readable CLI renderer for scenario results.  
Why it is there: provides immediate inspection of domain behavior without needing JSON parsing.  
Where it connects: scenario_runner.py.

---

AI_GO/tests/stage_market_analyzer_v1_scenario_probe.py  
What it is: formal probe validating scenario correctness.  
Why it is there: enforces that all scenario cases match expected behavior before advancing system state.  
Where it connects: scenario_runner.py.

---

AI_GO/child_cores/market_analyzer_v1/SCENARIO_TEST_PLAN.md  
What it is: documentation of scenario test design and expected outcomes.  
Why it is there: establishes domain validation methodology and provides interpretive guidance for results.  
Where it connects: development workflow, validation phase, system documentation.

---

AI_GO/child_cores/market_analyzer_v1/ui/historical_replay_packets.py  
What it is: historical-style replay input generator simulating real-world event patterns.  
Why it is there: introduces semi-realistic test conditions to evaluate strategy behavior under plausible historical scenarios.  
Where it connects: historical_replay_runner.py, execution/run.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/historical_replay_expectations.py  
What it is: expectation definitions for historical replay cases.  
Why it is there: defines expected system behavior for replay scenarios to allow structured evaluation.  
Where it connects: historical_replay_runner.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/historical_replay_runner.py  
What it is: replay execution engine for historical scenarios.  
Why it is there: runs replay packets through the core and evaluates results against expectations.  
Where it connects: execution/run.py, output_builder.py, watcher/core_watcher.py, historical_replay_packets.py, historical_replay_expectations.py.

---

AI_GO/child_cores/market_analyzer_v1/ui/historical_replay_cli_report.py  
What it is: CLI renderer for historical replay results.  
Why it is there: enables readable inspection of replay outcomes and strategy behavior under simulated historical conditions.  
Where it connects: historical_replay_runner.py.

---

# END OF LEDGER CONTINUATION