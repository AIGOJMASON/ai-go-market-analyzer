# REPORT BUNDLE LAYER (STAGE 36)

## What it is
The report bundle layer is the governed runtime packaging surface that groups approved watcher-facing reports into a bounded bundle and index structure.

## Why it exists
Stages 32 through 35 established runtime status reporting, operator summary aggregation, CLI presentation, and watcher-safe report export.
Stage 36 establishes a canonical report bundle surface so approved exports can be grouped, indexed, and handed off without exposing raw internals or creating new authority.

## Core Principles
- read-only
- package-only
- no mutation authority
- no raw internal state exposure
- no inference beyond governed upstream report truth
- no authority escalation through bundling

## Allowed Functions
- group approved watcher reports into a bundle
- generate a bundle index of included reports
- provide bounded bundle metadata
- preserve source truth while reducing report fragmentation

## Prohibited Functions
- creating source truth
- modifying report truth
- exposing undeclared internal fields
- bypassing Stage 35 policy
- triggering upstream processes
- accepting write actions

## Bundle Model
This layer accepts only:
- shaped Stage 35 watcher reports

It packages them into:
- runtime report bundles
- report indexes
- bounded bundle summaries

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
- packet archives
- state history

## Where it connects
- report_bundle_registry.py
- report_bundle_policy.py
- report_bundle_interface.py
- Stage 35 watcher report views
- Stage 36 probe surface