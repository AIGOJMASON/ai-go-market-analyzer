# PM CORE CHILD CORE INHERITANCE CONTRACT

## PURPOSE

Defines how PM Core may coordinate with child cores without transferring root authority.

PM Core may route bounded context.

Child cores may consume bounded context.

Neither layer may create execution authority by handoff alone.

## REQUIRED FLOW

All PM-to-child-core inheritance movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ PM dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

## PM CORE MAY

- select lawful child-core target
- preserve lineage
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false
- route bounded context

## PM CORE MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- transfer root authority to child cores

## CHILD CORE MAY

- receive bounded context
- process within declared domain scope
- produce bounded output
- request governed mutation

## CHILD CORE MAY NOT

- execute independently
- mutate workflow directly
- mutate project truth directly
- create authority from PM routing
- treat memory or receipts as command authority

## MUTATION LAW

Persistence = Mutation.

If handoff evidence, receipt, routing trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

PM-to-child-core inheritance cannot trigger execution.

## SUMMARY

PM Core coordinates child-core use without transferring authority.