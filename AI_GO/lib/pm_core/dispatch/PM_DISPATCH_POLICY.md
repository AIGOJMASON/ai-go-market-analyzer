# PM DISPATCH POLICY

## PURPOSE

Defines lawful PM dispatch behavior.

Dispatch moves bounded context toward the correct system boundary.

Dispatch is not execution.

Dispatch is not persistence by default.

## REQUIRED FLOW

Any child-core-bound dispatch must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM routing  
→ dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

## DISPATCH MAY

- preserve lineage
- preserve adapter identity
- preserve target identity
- preserve authority boundary
- preserve execution_allowed = false
- prepare bounded context for ingress

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

## OUTCOME LAW

Outcome references are advisory only.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

Dispatch cannot trigger execution.

## SUMMARY

PM dispatch is bounded context movement only.