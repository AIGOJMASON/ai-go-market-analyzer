# PM CORE IDENTITY

## PURPOSE

Defines the lawful identity of PM Core inside AI_GO.

PM Core coordinates interpretation, routing, and dispatch posture.

PM Core does not execute.

PM Core does not mutate directly.

PM Core does not create authority by itself.

## REQUIRED FLOW

Any PM Core path that touches child-core context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ PM routing  
→ PM dispatch  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core context remains curated, adapter-shaped, bounded, and advisory unless governed mutation is explicitly approved.

## PM CORE MAY

- interpret governed context
- select lawful routing posture
- prepare dispatch posture
- preserve lineage metadata
- preserve authority boundaries
- preserve execution_allowed = false
- preserve mutation_allowed = false unless governed

## PM CORE MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- create decision authority by itself
- override governance

## MUTATION LAW

Persistence = Mutation.

If PM evidence, routing trace, dispatch trace, receipt, memory record, outcome reference, dashboard packet, latest snapshot, or packet artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## MEMORY LAW

Memory is advisory.

Memory may preserve governed context.

Memory may not decide.

Memory may not override governance.

Memory persistence is classified mutation.

## EXECUTION LAW

execution_allowed = false by default.

PM Core cannot trigger execution.

PM Core can only prepare governed posture for downstream validation.

## SUMMARY

PM Core coordinates bounded interpretation and routing.

It cannot execute, mutate directly, retrieve providers, or create authority.