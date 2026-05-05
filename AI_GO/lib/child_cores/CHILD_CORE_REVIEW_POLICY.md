# CHILD CORE REVIEW POLICY

## PURPOSE

This document defines lawful review behavior for AI_GO child-core output.

Review is validation only.

Review is not execution.

Review is not persistence by default.

Review is not authority creation.

## CHILD-CORE FLOW LAW

All child-core review context must preserve lawful upstream lineage:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  
→ child-core output  
→ child-core review  

Provider retrieval is reserved for RESEARCH_CORE only.

Review may only evaluate bounded output created from curated, adapter-shaped context.

## REVIEW ROLE

Child-core review may:

- evaluate bounded output
- check lineage metadata
- check scope compliance
- check authority boundaries
- check execution_allowed = false
- check mutation_allowed = false unless governed
- prepare review evidence for watcher or routing

Child-core review may not:

- execute actions
- mutate workflow
- mutate project truth
- write memory
- write outcome feedback
- create recommendation authority
- override governance
- become decision authority

## REQUIRED REVIEW METADATA

A lawful review artifact should expose:

- RESEARCH_CORE lineage
- engine curation marker
- adapter identity
- child-core target
- output scope
- review status
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## MUTATION LAW

Persistence = Mutation.

Review evaluation is not mutation by default.

If review evidence, review artifact, receipt, memory record, outcome reference, dashboard packet, or latest snapshot is persisted, that persistence must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document review posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth.

A receipt may not become review authority.

## OUTCOME LAW

Review may reference outcomes only as advisory evidence.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## WATCHER HANDOFF LAW

Review may move to watcher validation.

Watcher handoff does not create authority.

Watcher handoff must preserve:

- lineage
- scope
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## EXECUTION LAW

execution_allowed = false by default.

Review cannot trigger execution.

Review cannot authorize downstream action.

Review remains bounded until watcher validation, request governance, and execution gating.

## SUMMARY

Child-core review validates bounded output created from curated, adapter-shaped runtime context.

It cannot mutate, execute, retrieve providers, or create authority.