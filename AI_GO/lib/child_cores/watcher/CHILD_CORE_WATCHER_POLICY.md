# CHILD CORE WATCHER POLICY

## PURPOSE

This document defines lawful watcher interaction with AI_GO child-core review output.

Watcher is validation authority only.

Watcher may pass, block, or escalate posture.

Watcher is not execution.

Watcher is not persistence by default.

Watcher is not workflow mutation.

## CHILD-CORE FLOW LAW

All child-core watcher context must preserve lawful upstream lineage:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  
→ child-core output  
→ child-core review  
→ child-core watcher  

Provider retrieval is reserved for RESEARCH_CORE only.

Watcher may only validate bounded review context created from curated, adapter-shaped upstream flow.

## WATCHER ROLE

Child-core watcher may validate:

- lineage
- scope boundary
- review posture
- mutation request shape
- execution_allowed = false
- mutation_allowed = false unless governed
- workflow readiness
- authority boundary
- escalation requirement

## WATCHER LIMITS

Child-core watcher may not:

- execute actions
- mutate workflow
- mutate project truth
- write memory
- write outcome feedback
- create recommendation authority
- become decision authority
- override Request Governor
- override Execution Gate
- override State Authority
- override Cross-Core Integrity

## REQUIRED WATCHER METADATA

A lawful watcher artifact should expose:

- RESEARCH_CORE lineage
- engine curation marker
- adapter identity
- child-core target
- review scope
- watcher status
- validation result
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## MUTATION LAW

Persistence = Mutation.

Watcher validation is not mutation by default.

If watcher evidence, watcher artifact, receipt, memory record, outcome reference, dashboard packet, or latest snapshot is persisted, that persistence must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document watcher posture.

A receipt may not authorize execution.

A receipt may not mutate workflow truth.

A receipt may not become watcher authority.

## OUTCOME LAW

Watcher may reference outcomes only as advisory evidence.

Outcome persistence is classified mutation.

Outcome references cannot alter workflow, routing, decision, or execution authority.

## GOVERNANCE HANDOFF LAW

Watcher may hand validated posture to governance layers.

Watcher handoff does not create execution authority.

Watcher handoff must preserve:

- lineage
- scope
- validation result
- advisory status
- execution_allowed = false
- mutation_allowed = false unless governed

## EXECUTION LAW

execution_allowed = false by default.

Watcher cannot trigger execution.

Watcher cannot authorize downstream action alone.

Watcher is necessary but not sufficient for mutation or execution.

## SUMMARY

Child-core watcher validates bounded review context from lawful upstream flow.

It can pass, block, or escalate posture, but it cannot mutate, execute, retrieve providers, or create authority.