# PM TO SMI

## PURPOSE

Defines lawful PM interaction with SMI.

SMI provides advisory system memory and posture context.

SMI is not execution.

SMI is not mutation by default.

SMI does not create authority.

## REQUIRED FLOW

Any PM-to-SMI path involving child-core context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ PM interpretation  
→ SMI advisory context  
→ PM routing  
→ child-core ingress when routed  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core context remains curated, adapter-shaped, bounded, and advisory unless governed mutation is explicitly approved.

## PM MAY

- request advisory SMI posture
- preserve lineage metadata
- preserve authority boundaries
- preserve execution_allowed = false
- use SMI context for interpretation

## PM MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- override governance

## SMI MAY

- expose advisory posture
- expose governed memory context
- support pattern interpretation
- support operator understanding

## SMI MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- decide routing authority by itself
- override PM governance
- override Watcher
- override Execution Gate

## MUTATION LAW

Persistence = Mutation.

If SMI evidence, PM evidence, receipt, memory record, outcome reference, dashboard packet, latest snapshot, or posture artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## MEMORY LAW

Memory is advisory.

Memory may preserve context.

Memory may not decide.

Memory may not override governance.

Memory persistence is classified mutation.

## OUTCOME LAW

Outcome references are advisory only.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

PM-to-SMI interaction cannot trigger execution.

## SUMMARY

PM-to-SMI is advisory context exchange only.

It cannot mutate, execute, retrieve providers, or create authority.