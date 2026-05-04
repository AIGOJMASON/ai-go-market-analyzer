# CHILD CORE TO WATCHER

## PURPOSE

Defines lawful child-core-to-watcher handoff.

Watcher validates bounded posture.

Watcher does not execute.

Watcher does not mutate by default.

## REQUIRED FLOW

All child-core-to-watcher movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  
→ child-core output  
→ child-core review  
→ watcher  

Provider retrieval is reserved for RESEARCH_CORE only.

## HANDOFF MAY

- pass bounded review posture
- preserve lineage
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false

## HANDOFF MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create watcher authority beyond validation

## MUTATION LAW

Persistence = Mutation.

If watcher handoff evidence, receipt, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

Child-core-to-watcher handoff cannot trigger execution.

## SUMMARY

Child-core-to-watcher is validation handoff only.