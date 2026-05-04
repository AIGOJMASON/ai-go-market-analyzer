# ROUTING DECISION CONTRACT

## PURPOSE

Defines the lawful contract between routing posture and routing decision.

A routing decision is bounded selection.

It is not execution.

It is not persistence by default.

## REQUIRED FLOW

Any child-core-bound routing decision must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ routing decision  

Provider retrieval is reserved for RESEARCH_CORE only.

## DECISION MAY

- select a lawful target
- preserve lineage
- preserve authority boundary
- preserve advisory status
- preserve execution_allowed = false

## DECISION MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority

## MUTATION LAW

Persistence = Mutation.

If decision evidence, receipt, routing trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

Routing decision cannot trigger execution.

## SUMMARY

A routing decision selects bounded direction only.