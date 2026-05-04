# CHILD CORE RUNTIME POLICY

## PURPOSE

This document defines lawful runtime behavior for AI_GO child-core processing.

Runtime is computation only.

Runtime does not create authority.

Runtime does not create execution permission.

Runtime does not persist state by default.

## CHILD-CORE FLOW LAW

All child-core runtime context must originate through lawful upstream flow:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core runtime  

Provider retrieval is reserved for RESEARCH_CORE only.

Child-core runtime begins after engine curation and adapter shaping.

## RUNTIME ROLE

Child-core runtime may:

- consume adapter-shaped context
- apply bounded domain logic
- produce bounded output
- preserve authority metadata
- preserve execution_allowed = false

Child-core runtime may not:

- call external systems
- access raw provider material
- reinterpret source material outside curated context
- mutate workflow
- mutate project truth
- write memory
- write outcome feedback
- create recommendation authority
- override governance

## REQUIRED RUNTIME METADATA

A lawful runtime packet should expose:

- RESEARCH_CORE lineage
- engine curation marker
- adapter identity
- child-core target
- domain scope
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## MUTATION LAW

Persistence = Mutation.

Runtime computation is not mutation by default.

If runtime evidence, runtime trace, receipt, output, memory record, or outcome reference is persisted, that persistence must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document runtime posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth.

A receipt may not become child-core authority.

## OUTCOME LAW

Outcome references produced near runtime are advisory only.

Outcome persistence is classified mutation and cannot alter workflow, routing, decision, or execution authority.

## EXECUTION LAW

execution_allowed = false by default.

Runtime cannot trigger execution.

Runtime cannot authorize downstream action.

Runtime output remains bounded until governed review and routing.

## SUMMARY

Child-core runtime is bounded computation over curated, adapter-shaped context.

It cannot mutate, execute, retrieve providers, or create authority.