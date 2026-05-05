AI_GO/lib/child_cores/market_analyzer_v1/SCENARIO_TEST_PLAN.md


## PURPOSE

Defines lawful <domain> behavior for Market Analyzer v1.

Market Analyzer v1 is a child-core surface.

It is advisory by default.

It does not execute.

It does not mutate by default.

It does not create authority.

## REQUIRED FLOW

All Market Analyzer v1 context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ bounded Market Analyzer processing  

Provider retrieval is reserved for RESEARCH_CORE only.

Market Analyzer v1 receives curated, adapter-shaped context only.

## AUTHORITY LIMITS

Market Analyzer v1 may:

- consume bounded context
- produce advisory output
- preserve lineage
- preserve execution_allowed = false
- request governed mutation when required

Market Analyzer v1 may not:

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create recommendation authority
- create decision authority
- bypass governance

## MUTATION LAW

Persistence = Mutation.

If evidence, receipt, dashboard packet, memory record, outcome reference, routing trace, artifact, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## EXECUTION LAW

execution_allowed = false by default.

No Market Analyzer v1 document, output, test plan, activation review, memory path, or PM route may trigger execution by itself.

## SUMMARY

Market Analyzer v1 remains bounded, advisory, non-executing, and governed.