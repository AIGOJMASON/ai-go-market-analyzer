# OPERATOR CLI LAYER (STAGE 34)

## What it is
The operator CLI layer is the governed runtime presentation surface that renders bounded operator-facing runtime views for command-line use.

## Why it exists
Stages 32 and 33 established governed runtime status views and bounded operator summaries.
Stage 34 establishes a presentation-only CLI layer so operators can read system condition in a usable format without gaining new authority or exposing raw internals.

## Core Principles
- read-only
- presentation-only
- no mutation authority
- no raw internal state exposure
- no inference beyond governed upstream views
- no authority escalation through formatting

## Allowed Functions
- render runtime status views for CLI display
- render operator summary views for CLI display
- format bounded fields into human-readable output
- preserve upstream truth while reducing presentation friction

## Prohibited Functions
- creating source truth
- modifying source truth
- exposing undeclared internal fields
- bypassing status or operator-summary policy
- triggering upstream processes
- accepting write actions

## Presentation Model
This layer accepts only:
- shaped Stage 32 status views
- shaped Stage 33 operator summary views

It renders them into:
- plain text display blocks
- bounded field/value output
- summary-safe CLI presentation

## Authority Boundary
This layer has no write authority over:
- RESEARCH_CORE
- PM_CORE
- STRATEGY_LAYER
- CHILD_CORES
- runtime output
- runtime status
- operator summary layer
- packet archives
- state history

## Where it connects
- cli_view_registry.py
- cli_render_policy.py
- cli_presenter.py
- Stage 32 status views
- Stage 33 operator summary views
- Stage 34 probe surface