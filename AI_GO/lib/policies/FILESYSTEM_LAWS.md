# FILESYSTEM LAWS

## PURPOSE

Defines lawful filesystem behavior for AI_GO.

The filesystem is a persistence surface.

Persistence = Mutation.

No filesystem write is neutral.

## CHILD-CORE FLOW LAW

Any child-core artifact stored or read from the filesystem must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ bounded child-core processing  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core artifacts are bounded records, not authority.

## READ LAW

Filesystem reads may:

- expose existing governed artifacts
- support operator review
- support canon validation
- support advisory context

Reads may not:

- mutate state
- create authority
- trigger execution
- alter workflow truth

## WRITE LAW

Filesystem writes are mutation.

Persistence = Mutation.

Every write must be explicit, classified, traceable, and governed.

## REQUIRED WRITE GOVERNANCE

All filesystem mutation must pass:

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

Filesystem activity cannot trigger execution.

## SUMMARY

The filesystem is governed persistence.

Nothing may write, persist, or produce receipts outside classified governance.