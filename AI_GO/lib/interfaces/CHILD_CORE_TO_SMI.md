# CHILD CORE TO SMI

## PURPOSE

Defines lawful child-core-to-SMI handoff.

SMI receives advisory continuity context only.

SMI does not execute.

SMI does not mutate by default.

## REQUIRED FLOW

All child-core-to-SMI movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  
→ child-core output  
→ child-core review  
→ watcher  
→ SMI  

Provider retrieval is reserved for RESEARCH_CORE only.

## HANDOFF MAY

- preserve bounded continuity context
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
- create SMI authority

## MUTATION LAW

Persistence = Mutation.

If SMI handoff evidence, receipt, memory record, outcome reference, dashboard packet, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## MEMORY LAW

Memory is advisory.

Memory persistence is classified mutation.

Memory may preserve context, but it may not decide.

## EXECUTION LAW

execution_allowed = false by default.

Child-core-to-SMI handoff cannot trigger execution.

## SUMMARY

Child-core-to-SMI preserves advisory continuity context only.