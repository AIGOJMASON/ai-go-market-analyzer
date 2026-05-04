# CHILD CORE REVIEW POLICY

## PURPOSE

Defines lawful child-core review behavior.

Review is validation only.

Review is not execution.

Review is not persistence by default.

Review does not create authority.

## REQUIRED FLOW

All child-core review context must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  
→ child-core output  
→ child-core review  

Provider retrieval is reserved for RESEARCH_CORE only.

## REVIEW MAY

- inspect bounded output
- verify lineage
- verify adapter identity
- verify authority boundary
- verify execution_allowed = false
- prepare validation evidence

## REVIEW MAY NOT

- execute actions
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- create recommendation authority
- create decision authority

## MUTATION LAW

Persistence = Mutation.

If review evidence, receipt, review trace, dashboard packet, memory record, outcome reference, or latest snapshot is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## OUTCOME LAW

Outcome references are advisory only.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

Review cannot trigger execution.

## SUMMARY

Child-core review validates bounded output only.