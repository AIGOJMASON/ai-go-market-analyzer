# OUTPUT CONSUMPTION LAYER (STAGE 31)

## What it is
The output consumption layer is the governed shaping layer that controls how validated, closed artifacts are presented to approved downstream consumers.

## Why it exists
Stage 30 established what may leave the governed interior.
Stage 31 establishes who may consume exposed artifacts, which fields they may receive, and what rendering depth is allowed.

## Core Principles
- read-only
- no mutation authority
- no truth transformation
- no authority escalation through formatting
- consumer-specific visibility only

## Allowed Functions
- approve or reject a consumer profile
- shape allowed fields for that consumer
- apply rendering depth rules
- preserve artifact truth while limiting exposure

## Prohibited Functions
- creating new artifacts
- modifying artifact truth
- adding interpretation not present in the source artifact
- exposing fields outside approved consumer policy
- bypassing Stage 30 validation

## Consumption Model
An artifact must first pass output-boundary validation.
Then the consumer layer determines:
1. whether the consumer is allowed
2. which fields are visible
3. which rendering mode is allowed

## Rendering Modes
- summary_only
- summary_with_refs
- closed_artifact

## Authority Boundary
This layer has no write authority over:
- RESEARCH_CORE
- PM_CORE
- STRATEGY_LAYER
- CHILD_CORES
- runtime state
- packet archives

## Where it connects
- consumer_profiles.py
- field_policy.py
- render_policy.py
- consumer_interface.py
- watcher_interface.py
- Stage 31 probe surface