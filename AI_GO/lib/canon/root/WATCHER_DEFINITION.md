# WATCHER DEFINITION

## PURPOSE

WATCHER is the runtime validation layer for AI_GO.

It checks whether a requested action is safe, lawful, and consistent with current system posture before mutation or execution can proceed.

WATCHER does not execute.

WATCHER does not mutate workflow truth.

WATCHER does not create authority.

## ROLE

WATCHER validates:

- action shape
- project posture
- phase posture
- checklist readiness
- signoff readiness
- state consistency
- child-core boundary posture
- route-level mutation posture
- advisory-layer boundary posture

## CHILD-CORE FLOW RULE

Any child-core action must preserve lawful upstream context flow:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter  
→ child core  

Child cores may not fetch providers directly.

Child cores may not receive raw provider material as authority.

Child-core runtime actions must operate only from bounded, curated, adapter-shaped context.

## AUTHORITY BOUNDARY

WATCHER may:

- pass validation
- block validation
- report errors
- surface risk
- provide governance evidence

WATCHER may not:

- execute
- mutate workflow
- mutate project truth
- override Request Governor
- override Execution Gate
- override State Authority
- override Cross-Core Integrity

## MUTATION LAW

Persistence = Mutation.

Watcher output may be persisted only as classified validation evidence.

Watcher validation does not itself perform mutation.

## EXECUTION LAW

execution_allowed = false unless the full governed chain permits execution.

The governed chain is:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

WATCHER is necessary but not sufficient for execution.

## SUMMARY

WATCHER is a validation authority.

It blocks or validates posture, but it does not execute or mutate.