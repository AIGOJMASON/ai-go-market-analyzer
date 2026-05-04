# PM ROUTING POLICY

## PURPOSE

Defines lawful PM routing behavior.

Routing selects bounded next-system direction.

Routing is not execution.

Routing is not persistence by default.

## REQUIRED FLOW

Any child-core-bound route must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  

Provider retrieval is reserved for RESEARCH_CORE only.

## ROUTING MAY

- select target boundary
- preserve lineage
- preserve authority boundary
- preserve execution_allowed = false
- prepare dispatch posture

## ROUTING MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
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

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document routing posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth.

## OUTCOME LAW

Outcome references are advisory only.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

Routing cannot trigger execution.

## SUMMARY

PM routing selects bounded direction without mutation or execution.