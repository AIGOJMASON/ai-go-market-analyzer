# EXPORT INDEX LAYER (STAGE 38)

## What it is
The export index layer is the governed runtime dispatch-prep surface that creates a bounded export index for approved bundle manifests.

## Why it exists
Stages 36 and 37 established canonical report bundling and formal bundle manifests.
Stage 38 establishes a dispatch-prep export index so governed manifests can be referenced, organized, and prepared for downstream export without exposing raw internal state or creating new authority.

## Core Principles
- read-only
- index-only
- no mutation authority
- no raw internal state exposure
- no inference beyond governed upstream manifest truth
- no authority escalation through export indexing

## Allowed Functions
- create an export index view for an approved bundle manifest
- record bounded export metadata
- expose dispatch-ready index structure
- preserve manifest truth while reducing downstream ambiguity

## Prohibited Functions
- creating source truth
- modifying manifest truth
- exposing undeclared internal fields
- bypassing Stage 37 policy
- triggering upstream processes
- accepting write actions

## Export Index Model
This layer accepts only:
- shaped Stage 37 bundle manifest views

It emits:
- export indexes
- dispatch-prep index views
- bounded export summaries

## Authority Boundary
This layer has no write authority over:
- RESEARCH_CORE
- PM_CORE
- STRATEGY_LAYER
- CHILD_CORES
- runtime output
- runtime status
- operator summary layer
- operator CLI layer
- watcher report layer
- report bundle layer
- bundle manifest layer
- packet archives
- state history

## Where it connects
- export_index_registry.py
- export_index_policy.py
- export_index_interface.py
- Stage 37 bundle manifest views
- Stage 38 probe surface