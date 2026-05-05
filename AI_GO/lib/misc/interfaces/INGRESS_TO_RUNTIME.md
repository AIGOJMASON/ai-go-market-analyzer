# INGRESS TO RUNTIME INTERFACE

## PURPOSE

This document defines the general interface rule for moving from ingress posture into runtime posture.

This file exists as a compatibility interface reference.

The authoritative child-core runtime policy remains:

AI_GO/lib/child_cores/runtime/CHILD_CORE_RUNTIME_POLICY.md

## REQUIRED FLOW

Any child-core-related ingress-to-runtime interface must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child-core ingress  
→ child-core runtime  

Provider retrieval is reserved for RESEARCH_CORE only.

Runtime begins after lawful curation and adapter shaping.

## INTERFACE ROLE

The interface may:

- transfer bounded context
- preserve lineage metadata
- preserve authority boundary
- preserve execution_allowed = false

The interface may not:

- fetch external material
- carry raw provider material as authority
- mutate workflow
- mutate project truth
- write memory
- write outcome feedback
- create execution permission

## MUTATION LAW

Persistence = Mutation.

The interface does not persist by default.

If interface evidence, trace, receipt, or runtime snapshot is persisted, that persistence must be explicit, classified, traceable, and governed.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## RECEIPT LAW

A receipt is a persisted artifact.

A receipt may document interface movement.

A receipt may not authorize execution.

A receipt may not become runtime authority.

## EXECUTION LAW

execution_allowed = false by default.

Ingress-to-runtime interface movement cannot trigger execution.

It only preserves bounded context transfer.

## SUMMARY

This interface moves lawful curated context from ingress posture into runtime posture.

It does not mutate, execute, or create authority.