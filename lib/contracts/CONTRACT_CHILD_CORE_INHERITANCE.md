# CONTRACT CHILD CORE INHERITANCE

## PURPOSE

Defines what every AI_GO child core inherits from root governance.

A child core is bounded domain logic.

A child core is not root authority.

A child core is not execution authority.

## REQUIRED FLOW

Every child-core inheritance path must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core scope begins after engine curation and adapter shaping.

## INHERITED AUTHORITY LIMITS

Every child core inherits:

- execution_allowed = false by default
- mutation_allowed = false unless governed
- advisory status unless governance approves mutation
- bounded domain scope
- root governance dependency
- lineage preservation requirement

## PROHIBITED AUTHORITY

A child core may not:

- create root authority
- execute independently
- mutate workflow directly
- mutate project truth directly
- write memory outside governance
- write outcome feedback outside governance
- treat receipt output as approval
- treat memory as command authority

## MUTATION LAW

Persistence = Mutation.

If child-core evidence, receipt, dashboard packet, memory record, outcome reference, latest snapshot, or artifact is persisted, it must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document governed action.

A receipt may not authorize execution.

A receipt may not mutate workflow truth by itself.

## EXECUTION LAW

execution_allowed = false by default.

A child core cannot trigger execution on inherited authority.

## SUMMARY

Child-core inheritance means bounded context, governed mutation, and no independent authority.