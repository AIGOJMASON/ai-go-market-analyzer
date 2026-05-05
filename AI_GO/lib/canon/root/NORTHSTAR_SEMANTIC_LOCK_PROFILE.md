# NORTHSTAR SEMANTIC LOCK PROFILE

## PURPOSE

Defines the Northstar semantic lock for AI_GO.

This profile preserves the legal grammar of AI_GO.

No layer in the system may create authority independently.

## LOCK CONDITION

failed_count = 0  
global_concepts = passed  
review_count is governed complexity  
Review_count is not failure  

## SOURCE FLOW LOCK

All source and child-core movement must preserve:

source or provider signal  
→ RESEARCH_CORE  
→ engine curation  
→ adapter shaping  
→ PM interpretation  
→ routing  
→ dispatch  
→ child-core ingress  

## EXECUTION LOCK

execution_allowed = false by default.

## MUTATION LOCK

Persistence = Mutation.

All mutation must pass:

State Authority  
→ Watcher  
→ Canon  
→ Request Governor  
→ Execution Gate  
→ Cross-Core Integrity  

## REVIEW POLICY

review_count does not indicate failure.

review_count indicates governed complexity.

## AUTHORITY LOCK

No layer in the system may create authority independently.

No layer may self-execute or self-mutate.

## SUMMARY

Northstar semantic lock is active only when failed_count = 0 and global_concepts = passed.