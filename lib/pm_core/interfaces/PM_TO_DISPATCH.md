# PM TO DISPATCH

## PURPOSE

Defines lawful transition from PM routing into dispatch.

Dispatch is bounded handoff preparation.

Dispatch is not execution.

Dispatch is not persistence by default.

## REQUIRED FLOW

All child-core-bound dispatch must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM routing  
→ dispatch  

Provider retrieval is reserved for RESEARCH_CORE only.

## DISPATCH ROLE

Dispatch may:

- package bounded context
- preserve target identity
- preserve lineage
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false

Dispatch may not:

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority

## MUTATION LAW

Persistence = Mutation.

If dispatch evidence, receipt, trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

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

PM-to-dispatch cannot trigger execution.

## SUMMARY

PM-to-dispatch moves bounded routing posture into dispatch without mutation or execution.