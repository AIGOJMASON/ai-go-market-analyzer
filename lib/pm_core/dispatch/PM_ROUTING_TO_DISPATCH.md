# PM ROUTING TO DISPATCH

## PURPOSE

Defines lawful transition from PM routing into PM dispatch.

Routing-to-dispatch is bounded handoff preparation.

It is not execution.

It is not mutation by default.

It does not create authority.

## REQUIRED FLOW

Any PM routing-to-dispatch path involving child-core context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ PM dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core dispatch context must be curated, adapter-shaped, bounded, and advisory unless governed mutation is explicitly approved.

## ROUTING MAY

- select a lawful target
- preserve lineage metadata
- preserve authority boundaries
- preserve execution_allowed = false
- prepare bounded dispatch context

## ROUTING MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority

## DISPATCH MAY

- package bounded context
- preserve target identity
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false

## DISPATCH MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- override governance

## MUTATION LAW

Persistence = Mutation.

If routing evidence, dispatch evidence, receipt, routing trace, dispatch trace, dashboard packet, memory record, outcome reference, latest snapshot, or artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document governed routing-to-dispatch posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth by itself.

## EXECUTION LAW

execution_allowed = false by default.

PM routing-to-dispatch cannot trigger execution.

## SUMMARY

PM routing-to-dispatch moves bounded advisory routing posture into dispatch only.

It cannot mutate, execute, retrieve providers, or create authority.