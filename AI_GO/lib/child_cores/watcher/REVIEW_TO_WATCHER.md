# REVIEW → WATCHER BRIDGE POLICY

## Purpose

This document defines how review-stage outputs are passed into watcher validation.

The watcher layer is responsible for determining whether a proposed action is:

- safe
- compliant
- allowed to proceed toward execution

---

## Source Integrity Requirement

All review inputs must originate from the governed ingestion pipeline:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter shaping  
→ PM interpretation  
→ routing  
→ review stage  

Watcher must NEVER receive:

- raw provider data  
- direct child-core generated source assumptions  
- uncurated or unclassified input  

---

## Review Output Contract

Review stage produces:

- structured advisory output
- no execution authority
- no mutation authority

All outputs must be:

- explicitly classified (advisory vs mutation candidate)
- traceable to upstream governed sources
- bounded in scope

---

## Watcher Role

Watcher evaluates:

- policy compliance
- mutation eligibility
- state integrity risk
- cross-core impact

Watcher produces:

- validation result
- severity classification
- execution recommendation

---

## Mutation Enforcement

If review output implies mutation:

Mutation must be treated as a **candidate only**.

All mutation must pass:

State Authority  
→ Watcher validation  
→ Canon validation  
→ Request Governor  
→ Execution Gate  
→ Cross-core enforcement  

No mutation is allowed at review stage.

---

## Prohibited Behavior

The following are forbidden:

- direct execution from review
- implicit mutation through language
- bypass of watcher validation
- provider or source inference without RESEARCH_CORE

---

## Summary

Review is advisory.

Watcher is enforcement.

No action proceeds without watcher validation.