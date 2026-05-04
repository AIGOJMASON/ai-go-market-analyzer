# PM TO CHILD CORE

## PURPOSE

Defines lawful PM-to-child-core handoff.

PM does not send raw source material to child cores.

PM may only route bounded, curated, adapter-shaped context.

## REQUIRED FLOW

All PM-to-child-core movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM routing  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

## PM ROLE

PM may:

- select lawful target child core
- preserve lineage
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false

PM may not:

- execute actions
- mutate workflow directly
- bypass governance
- create child-core authority

## MUTATION LAW

Persistence = Mutation.

If PM handoff evidence, receipt, routing trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

PM-to-child-core handoff cannot trigger execution.

## SUMMARY

PM-to-child-core is routing of lawful bounded context only.