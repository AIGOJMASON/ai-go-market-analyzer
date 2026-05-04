# CHILD CORE RUNTIME POLICY (NORTHSTAR ALIGNED)

## PURPOSE

Defines allowed behavior during processing.

---

## RUNTIME ROLE

Child core runtime:

- consumes adapter context
- performs domain logic
- produces output

---

## HARD CONSTRAINTS

Runtime MUST NOT:

- access external systems
- mutate system state
- write to storage
- execute actions
- override governance

---

## MUTATION LAW

ANY persistence = mutation

Must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Enforcement  

---

## EXECUTION LAW

execution_allowed = false

Runtime cannot execute anything.

---

## SYSTEM RULE

Runtime = PURE COMPUTATION

No authority emerges during runtime.