# PM TO ROUTING

## PURPOSE

Defines lawful transition from PM interpretation into routing.

Routing is advisory selection logic.

Routing is not execution.

Routing is not persistence by default.

## REQUIRED FLOW

Any child-core-bound routing must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  

Provider retrieval is reserved for RESEARCH_CORE only.

## ROUTING ROLE

Routing may:

- select lawful target
- preserve lineage
- preserve authority boundaries
- preserve execution_allowed = false
- prepare bounded dispatch context

Routing may not:

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create recommendation authority

## MUTATION LAW

Persistence = Mutation.

If routing evidence, receipt, routing trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## OUTCOME LAW

Outcome references are advisory only.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

PM-to-routing cannot trigger execution.

## SUMMARY

PM-to-routing prepares bounded routing posture without mutation or execution.