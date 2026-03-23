# DOMAIN LAYER — market_analyzer_v1

## What it is

The market_analyzer_v1 domain layer defines the bounded market domain in which this child core may operate.

This domain is limited to necessity-driven rebound recommendation work after shock events.

---

## Why it is there

This layer exists so the child core can apply domain logic without drifting into general market prediction, unrestricted trading logic, or upstream authority functions.

---

## Domain Focus

necessity-driven rebound market intelligence

Core pattern:

SHOCK
→ STABILIZATION
→ RECLAIM
→ CONFIRMATION
→ ENTRY
→ QUICK EXIT

---

## Allowed Domain Scope

This core may operate on:

- validated shock-event market cases
- market regime classification
- event propagation classification
- necessity-sector candidate filtering
- rebound validation
- recommendation packet generation
- approval-gated trade setup presentation

---

## Forbidden Domain Scope

This core may not operate as:

- a general discretionary trading engine
- a long-horizon portfolio allocator
- a raw research ingestion surface
- an autonomous execution bot
- a self-learning market optimizer

---

## Necessity Filter Scope

Allowed necessity sectors:

- energy
- agriculture
- fertilizer
- infrastructure
- critical_technology

Anything outside those sectors is outside domain scope for recommendation generation.

---

## Output Focus

This domain ends at structured, receipted recommendation output for human review.

Execution remains external to the child core.

---

## Where it connects

- DOMAIN_POLICY.md
- OUTPUT_POLICY.md
- execution/*
- outputs/*
- watcher/core_watcher.py
- smi/core_smi.py