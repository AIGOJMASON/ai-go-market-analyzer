# Contractor Proposals Core

## What it is

Bounded child core for the domain focus: contractor_proposals.

## Why it is there

Provides lawful domain-specific execution under PM_CORE inheritance authority for contractor proposal generation and related bounded output handling.

## Authority Position

This child core may receive bounded inheritance packets from PM_CORE and may execute only within its declared domain.

It may not:
- ingest direct research from RESEARCH_CORE
- bypass PM_CORE inheritance
- redefine system truth
- self-activate outside registry lifecycle rules

## Core Identity

- `core_id`: `contractor_proposals_core`
- `display_name`: `Contractor Proposals Core`
- `domain_focus`: `contractor_proposals`
- `template_version`: `stage12.v1`