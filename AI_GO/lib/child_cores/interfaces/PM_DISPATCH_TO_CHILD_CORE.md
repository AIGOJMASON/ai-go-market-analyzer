# PM DISPATCH TO CHILD CORE

## PURPOSE

Defines lawful dispatch from PM-controlled routing into child-core ingress.

Dispatch is bounded context movement.

Dispatch is not execution.

Dispatch is not persistence by default.

## REQUIRED FLOW

All PM-dispatch-to-child-core movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM routing  
→ PM dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

## DISPATCH MAY

- preserve lineage
- preserve adapter identity
- preserve target identity
- preserve authority boundary
- preserve execution_allowed = false
- prepare bounded context for child-core ingress

## DISPATCH MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- create recommendation authority

## MUTATION LAW

Persistence = Mutation.

If dispatch evidence, receipt, dispatch trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document dispatch posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth.

## EXECUTION LAW

execution_allowed = false by default.

Dispatch-to-child-core handoff cannot trigger execution.

## SUMMARY

PM dispatch moves bounded, curated, adapter-shaped context into child-core ingress only.