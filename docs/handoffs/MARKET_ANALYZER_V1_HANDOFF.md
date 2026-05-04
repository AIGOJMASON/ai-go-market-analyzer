# AI_GO HANDOFF DOCUMENT

## Project: `market_analyzer_v1` Child Core

## Phase Transition: Reasoning → Build

---

# 1. OBJECTIVE

Design and implement a **contract-compliant child core** inside AI_GO:

> **`market_analyzer_v1` = governed market intelligence child core that produces receipted, necessity-driven rebound trade recommendations for human approval**

This system:

* DOES NOT execute trades autonomously
* DOES NOT learn or reweight data
* DOES NOT ingest raw unapproved data

It:

* consumes **validated upstream artifacts**
* applies a **domain template**
* outputs **receipted recommendation artifacts**
* feeds a **human decision surface (dashboard)**

---

# 2. CORE DOCTRINE (LOCKED)

### Authority Separation

* AI_GO upstream = truth, validation, weighting, learning
* Child core = application only
* Human = final decision

### Execution Rule

> No execution without `human_trade_approval_record`

### Data Rule

> No unsealed or unverified data enters runtime

### Refinement Rule

> Runtime refinement is read-only (conditioning only)

### Output Rule

> Every output must include receipts + provenance

---

# 3. SYSTEM IDENTITY

> A **necessity-driven rebound recommendation engine** that exploits short-term mispricing after shock events while minimizing market exposure.

Strategy characteristics:

* short duration (hours → 1–2 days)
* small repeatable gains (“nickel slots”)
* strict exit discipline
* selective participation (not always in market)

---

# 4. CORE LOGIC MODEL

### Trade Lifecycle

```
SHOCK
→ STABILIZATION
→ RECLAIM
→ CONFIRMATION
→ ENTRY
→ QUICK EXIT
```

### Filters

1. **Market Participation Gate**

   * determines if trading is allowed

2. **Macro Filter**

   * bias only (never triggers trades)

3. **Necessity Filter**

   * only system-critical sectors:

     * energy
     * agriculture / fertilizer
     * infrastructure
     * critical tech

4. **Propagation Model**

   * fast / medium / slow ripple
   * primary / secondary / tertiary effects

5. **Rebound Validation**

   * required for all trades

---

# 5. DASHBOARD (TARGET OUTPUT)

The child core must support these panels:

### 1. Market Regime

* normal / volatile / crisis
* trade posture

### 2. Active Events

* event classification
* propagation speed
* ripple depth

### 3. Watchlist

* filtered assets only (necessity + liquidity)

### 4. Recommendations (CORE)

* structured trade setup
* no narrative, no hype

### 5. Approval Gate

* approve / reject / hold

### 6. Outcome Panel

* result tracking + archive

### 7. Receipt / Trace Layer (GLOBAL)

* full provenance for every item

---

# 6. ARTIFACTS (REQUIRED OUTPUTS)

```
market_case_record
market_regime_record
event_propagation_record
necessity_filtered_candidate_set
rebound_validation_record
trade_recommendation_packet
receipt_trace_packet
approval_request_packet
```

---

# 7. CHILD CORE ARCHITECTURE

## Location

```
AI_GO/child_cores/market_analyzer_v1/
```

## Required Structure

```
CORE_IDENTITY.md
INHERITANCE_CONTRACT.md
RESEARCH_INTERFACE.md
SMI_INTERFACE.md
WATCHER_INTERFACE.md
OUTPUT_POLICY.md
DOMAIN_POLICY.md
DOMAIN_REGISTRY.json

domains/
constraints/
execution/
outputs/
watcher/
smi/
research/
inheritance_state/
state/current/
```

---

# 8. EXECUTION MODULES

Inside `/execution/`:

* ingress_processor.py
* refinement_conditioning.py
* market_regime_classifier.py
* event_propagation_classifier.py
* necessity_filter.py
* rebound_validator.py
* recommendation_builder.py
* run.py

---

# 9. OUTPUT MODULES

Inside `/outputs/`:

* output_builder.py
* market_regime_view.py
* active_event_view.py
* watchlist_view.py
* trade_recommendation_view.py
* receipt_trace_view.py
* approval_request_view.py

---

# 10. WHAT THE CHILD CORE MUST NEVER DO

* reweight sources
* learn or mutate rules
* bypass PM_CORE
* ingest raw research
* execute trades autonomously
* produce unreceipted output

---

# 11. REGISTRATION STEPS (POST BUILD)

1. Add to:

```
child_cores/child_core_registry.json
```

2. Add to:

```
PM_CORE/state/child_core_registry.json
```

3. Ensure PM dispatch routing is wired

---

# 12. TESTING (MANDATORY)

## Required Probe Categories

* structure probe
* ingress validation probe
* runtime behavior probe
* output compliance probe
* approval gate probe

## Key Failure Conditions

* unapproved data accepted
* missing receipts
* invalid recommendation structure
* execution without approval
* domain leakage

---

# 13. SUCCESS CRITERIA

The system is complete when:

* child core builds successfully
* registry + routing confirmed
* all probes pass
* dashboard outputs are correct
* recommendations are receipted and structured
* approval gate enforced

---

# 14. NEXT BUILD ORDER

1. CORE_IDENTITY.md
2. INHERITANCE_CONTRACT.md
3. DOMAIN_POLICY.md
4. constraints.json
5. execution modules
6. output modules
7. watcher
8. registry + routing
9. probes

---

# FINAL LOCK

> **`market_analyzer_v1` is not a trading bot.
> It is a governed market intelligence surface that proposes receipted, validated opportunities under strict system control and human authority.**

---

END OF HANDOFF
