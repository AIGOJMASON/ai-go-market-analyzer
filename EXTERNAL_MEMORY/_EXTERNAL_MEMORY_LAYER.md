# EXTERNAL MEMORY LAYER
#
# Authority Class:
# Root-adjacent governed memory authority for external informational ingress.
#
# Purpose:
# Convert already-governed external information into persistence decisions
# without collapsing research weighting, PM strategy, runtime execution,
# or SMI self-memory into one surface.
#
# Input -> Output:
# governed external signal
# -> qualification decision
# -> persistence gate result
# -> db commit receipt or rejection receipt
#
# Core Role:
# This layer exists because lawful system use and lawful persistence are
# not the same decision.
#
# Existing upstream layers already answer:
# - may this be used?
# - may this be interpreted?
#
# This layer answers:
# - does this deserve durable storage?
#
# Relationship to Other Authorities:
#
# RESEARCH_CORE
# - provides weighted and governed upstream research packets
# - does not own persistence decisions
#
# PM_CORE
# - governs strategic use posture
# - does not decide durable admission into external memory by itself
#
# ENGINES / REFINEMENT
# - interpret governed signal
# - do not write to storage
#
# SMI
# - governs system self-memory from closed internal history
# - is not the same as external memory
#
# CHILD CORES
# - may consume promoted external memory later
# - do not decide upstream persistence law
#
# What This Layer Is:
# - a pre-DB persistence qualification membrane
# - a bounded storage admission authority
# - a lawful rejection surface for weak external signals
# - a provenance-preserving persistence surface
#
# What This Layer Is Not:
# - not RESEARCH_CORE
# - not PM strategy
# - not runtime execution
# - not SMI self-memory
# - not a general archive of everything observed
#
# Hard Rules:
# 1. No raw external input may persist directly.
# 2. Only governed inputs may enter qualification.
# 3. Persistence is earned, not assumed.
# 4. If source quality is below the minimum floor, persistence is denied.
# 5. If total persistence weight is below threshold, persistence is denied.
# 6. Rejection must be explicit and receipted.
# 7. Durable write must remain separate from qualification decision.
# 8. Stored records are not automatically training-grade memory.
# 9. Retrieval authority will be built later and is out of scope here.
#
# Current Phase Scope:
# Phase 1 - admission side only
#
# Included in this phase:
# - layer identity
# - registry
# - qualification policy
# - qualification runtime
# - receipt builder
# - persistence gate
# - sqlite-backed db writer
#
# Deferred:
# - retrieval
# - continuity indexing
# - promotion
# - child-core memory interfaces
# - PM return path
# - runtime influence return
#
# Canonical Flow:
#
# governed_external_signal
# -> qualification_engine
# -> qualification_receipt
# -> persistence_gate
# -> db_writer commit receipt
# or
# -> rejection receipt
#
# Primary Decision Axes:
# - source_quality_weight
# - signal_quality_weight
# - domain_relevance_weight
# - persistence_value_weight
# - contamination_penalty
# - redundancy_penalty
#
# Source Quality Rule:
# Source quality is a primary weight and a hard floor.
# A signal may be lawful to inspect and still be unlawful to persist.
#
# Persistence Classes:
# 1. rejected
#    - not persisted
# 2. held
#    - not durably persisted in Phase 1
# 3. persisted
#    - committed to external memory db
#
# Output Artifacts:
# - external_memory_qualification_record
# - external_memory_qualification_receipt
# - external_memory_persistence_receipt
# - external_memory_rejection_receipt
#
# State and Storage Boundary:
# This layer may write durable external-memory records only through the
# persistence gate and db writer. It may not mutate SMI continuity, PM
# state, runtime state, or canon.
#
# Future Connection:
# Later phases may consume persisted records through bounded retrieval,
# promotion, and child-core-facing memory interfaces.