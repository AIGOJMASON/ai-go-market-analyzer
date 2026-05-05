# INGRESS TO RUNTIME

## PURPOSE

This document defines the transition from child-core ingress into child-core runtime.

Ingress-to-runtime is a bounded internal handoff.

It is not execution.

It is not persistence.

It is not authority creation.

## REQUIRED FLOW

All ingress-to-runtime movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  

Provider retrieval is reserved for RESEARCH_CORE only.

Runtime begins only after engine curation, adapter shaping, and ingress validation.

## INGRESS RESPONSIBILITY

Ingress may hand runtime only:

- adapter-shaped context
- child-core target identity
- domain scope
- authority boundary
- execution_allowed = false
- mutation_allowed = false unless governed

## RUNTIME RESPONSIBILITY

Runtime may:

- consume bounded context
- apply domain logic
- prepare bounded output

Runtime may not:

- fetch external material
- inspect raw provider material
- mutate workflow
- mutate project truth
- write memory
- write outcome feedback
- authorize execution

## MUTATION LAW

Persistence = Mutation.

Ingress-to-runtime handoff does not persist by default.

If handoff evidence, runtime trace, receipt, or context snapshot is persisted, that persistence must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document ingress-to-runtime movement.

A receipt may not authorize execution.

A receipt may not create runtime authority.

## EXECUTION LAW

execution_allowed = false by default.

Ingress-to-runtime cannot trigger execution.

It only moves bounded context into computation.

## SUMMARY

Ingress-to-runtime is a controlled internal handoff from validated ingress to bounded computation.

It preserves upstream lineage and keeps runtime non-authoritative.