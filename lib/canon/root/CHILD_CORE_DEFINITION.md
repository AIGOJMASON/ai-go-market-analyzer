# CHILD CORE DEFINITION

## PURPOSE

A child core is a bounded domain subsystem within AI_GO.

A child core performs domain-specific work only inside a governed, inherited context.

A child core is not root authority.

A child core is not an autonomous system.

A child core is not allowed to fetch providers directly.

## CHILD-CORE FLOW RULE

All child-core input must follow lawful upstream flow:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child core  

The adapter shapes bounded context for the child core.

The child core consumes that bounded context only.

## ALLOWED BEHAVIOR

A child core may:

- consume curated adapter-shaped context
- process domain-specific inputs
- produce bounded outputs
- expose read surfaces
- request governed mutation
- emit classified receipts or artifacts when governed

## FORBIDDEN BEHAVIOR

A child core may not:

- redefine root authority
- fetch providers directly
- treat raw provider material as authority
- bypass PM Core
- bypass Watcher
- bypass Canon
- bypass Request Governor
- bypass Execution Gate
- bypass State Authority
- bypass Cross-Core Integrity
- mutate workflow truth without governance
- create undeclared persistence
- treat memory as command authority
- treat outcome feedback as decision authority

## MUTATION LAW

Persistence = Mutation.

Any child-core persistence must be explicit, classified, traceable, and governed.

Examples of classified persistence include:

- visibility_persistence
- receipt
- project_creation
- source_signal_persistence
- outcome_persistence
- memory_persistence

## EXECUTION LAW

execution_allowed = false by default.

A child core cannot execute on its own authority.

Any execution or mutation requires:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## OUTPUT LAW

Child-core outputs must remain bounded to their domain.

Outputs must expose:

- artifact type
- source context
- authority boundary
- classification when persisted
- sealed status when required

## SUMMARY

A child core is a bounded domain organ.

It receives lawful context from upstream governance, performs scoped work, and returns bounded output.

It never becomes root authority.