# PM TO CHILD CORE MARKET ANALYZER V1

## PURPOSE

Defines lawful PM handoff to Market Analyzer v1.

Market Analyzer v1 is a child-core surface.

PM may route bounded context to Market Analyzer v1.

PM does not execute.

PM does not mutate directly.

PM does not create Market Analyzer authority.

## REQUIRED FLOW

All PM-to-Market-Analyzer movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ PM dispatch  
→ child-core ingress  
→ bounded Market Analyzer processing  

Provider retrieval is reserved for RESEARCH_CORE only.

Market Analyzer v1 receives curated, adapter-shaped context only.

## PM MAY

- select Market Analyzer v1 as lawful target
- preserve lineage metadata
- preserve adapter identity
- preserve authority boundary
- preserve execution_allowed = false
- prepare bounded dispatch context

## PM MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create Market Analyzer authority
- create recommendation authority
- override governance

## MARKET ANALYZER MAY

- consume bounded context
- produce advisory output
- preserve lineage
- preserve execution_allowed = false
- request governed mutation when required

## MARKET ANALYZER MAY NOT

- retrieve providers
- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- create decision authority

## MUTATION LAW

Persistence = Mutation.

If PM handoff evidence, Market Analyzer evidence, routing trace, dispatch trace, receipt, dashboard packet, memory record, outcome reference, latest snapshot, or artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## DASHBOARD LAW

Dashboard visibility is advisory.

A dashboard packet may display posture.

A dashboard packet may not authorize execution.

A dashboard packet may not mutate workflow truth by itself.

## EXECUTION LAW

execution_allowed = false by default.

PM-to-Market-Analyzer handoff cannot trigger execution.

## SUMMARY

PM-to-Market-Analyzer routes bounded, curated, adapter-shaped context only.

It cannot mutate, execute, retrieve providers, or create authority.