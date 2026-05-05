# PM CORE PACKET SCHEMA

## PURPOSE

Defines lawful PM packet structure.

PM packets carry bounded advisory context.

PM packets do not execute.

PM packets do not mutate by default.

PM packets do not create authority.

## REQUIRED FLOW

Any PM packet involving child-core context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ PM dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core packet context must be curated, adapter-shaped, bounded, and advisory unless governed mutation is explicitly approved.

## REQUIRED PACKET FIELDS

A lawful PM packet should expose:

- packet_id
- source_lineage
- RESEARCH_CORE lineage
- engine curation marker
- adapter identity
- PM interpretation scope
- routing scope
- child-core target when applicable
- authority boundary
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## PACKET MAY

- carry bounded context
- preserve lineage
- support routing
- support dispatch
- support validation

## PACKET MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- create decision authority by itself

## MUTATION LAW

Persistence = Mutation.

If packet evidence, packet trace, receipt, memory record, outcome reference, dashboard packet, latest snapshot, or packet artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

A PM packet cannot trigger execution.

## SUMMARY

PM packets carry bounded advisory context only.

They cannot mutate, execute, retrieve providers, or create authority.