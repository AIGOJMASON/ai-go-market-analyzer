# CHILD CORE UI INTERFACE

## PURPOSE

Defines lawful UI interaction with AI_GO child-core surfaces.

UI is visibility only unless a separate governed mutation route is invoked.

UI does not create authority.

UI does not execute.

UI does not mutate by default.

## REQUIRED FLOW

Any child-core data shown through UI must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ bounded child-core processing  
→ UI visibility  

Provider retrieval is reserved for RESEARCH_CORE only.

## UI MAY

- display bounded child-core posture
- display lineage metadata
- display advisory output
- display execution_allowed = false
- display mutation status
- support operator understanding

## UI MAY NOT

- execute actions by visibility alone
- mutate workflow by display alone
- mutate project truth by display alone
- write memory outside governance
- write outcome feedback outside governance
- create child-core authority
- create recommendation authority

## MUTATION LAW

Persistence = Mutation.

If UI evidence, dashboard packet, receipt, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## DASHBOARD LAW

Dashboard visibility is advisory.

A dashboard packet may display system state.

A dashboard packet may not authorize execution.

A dashboard packet may not mutate workflow truth by itself.

## EXECUTION LAW

execution_allowed = false by default.

UI visibility cannot trigger execution.

## SUMMARY

Child-core UI exposes bounded visibility only.