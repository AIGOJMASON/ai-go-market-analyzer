# PM CORE STRATEGIC INTERPRETATION POLICY

## Purpose

Defines how PM interprets system context and directs action.

---

## Source Law

All interpretation must originate from:

source or provider signal  
→ RESEARCH_CORE  
→ engine refinement  
→ adapter  
→ PM  

PM must not interpret raw provider data.

---

## Interpretation Role

PM:

- interprets curated data
- defines strategy
- directs routing

PM does NOT:

- execute actions
- mutate state directly

---

## Child-Core Interaction

All child-core interaction must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine  
→ adapter  
→ PM  
→ routing  
→ dispatch  

Child cores never receive raw provider data.

---

## Mutation Clarification

Any:

- outcome creation
- persistence
- state change

is classified as **mutation**

---

## Mutation Enforcement

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-core enforcement  

---

## Prohibited Behavior

- direct execution by PM
- bypass of routing
- mutation without governance

---

## Summary

PM interprets.

PM routes.

PM does not execute.