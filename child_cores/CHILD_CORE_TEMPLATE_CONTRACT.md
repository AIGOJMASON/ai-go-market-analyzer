# CHILD CORE TEMPLATE CONTRACT

## Purpose

This document defines the minimum lawful structure for any AI_GO child core.

A child core is not a loose folder and not a direct execution shortcut.
A child core is a bounded governed unit that may receive inherited PM output,
perform domain-scoped execution, verify its own artifacts, and record its own
verified continuity without absorbing parent authority.

This contract exists so future child cores are created through one repeatable
pattern rather than by manual drift.

## Authority Position

Parent authority remains with PM_CORE.

A child core may:
- receive bounded inheritance packets from PM_CORE
- execute within its declared domain
- emit bounded outputs
- verify its own execution artifacts
- record local continuity after verification

A child core may not:
- self-activate outside PM_CORE creation and activation flow
- ingest raw research directly from RESEARCH_CORE
- bypass PM_CORE inheritance boundaries
- redefine system-wide truth
- activate refinement engines as authority sources
- mutate registry truth outside lawful lifecycle functions

## Minimum Required Surface

A valid child core must contain all of the following files.

### Root governance files
- `CORE_IDENTITY.md`
- `INHERITANCE_CONTRACT.md`
- `RESEARCH_INTERFACE.md`
- `SMI_INTERFACE.md`
- `WATCHER_INTERFACE.md`
- `OUTPUT_POLICY.md`
- `DOMAIN_POLICY.md`
- `DOMAIN_REGISTRY.json`

### Runtime and execution files
- `execution/ingress_processor.py`
- `outputs/output_builder.py`
- `watcher/core_watcher.py`
- `smi/core_smi.py`
- `research/research_interface.py`

### Required directories
- `inheritance_state/`
- `execution/`
- `outputs/`
- `watcher/`
- `smi/`
- `research/`
- `state/current/`
- `constraints/`
- `domains/`

### Required domain-layer file
- `domains/_DOMAIN_LAYER.md`

## Required Registry Shape

Each child core must be represented in PM_CORE registry state with:

- `core_id`
- `display_name`
- `domain_focus`
- `status`
- `template_version`
- `created_at`
- `updated_at`
- `core_path`
- `domain_registry_path`
- `required_files_verified`
- `structural_validation`
- `semantic_validation`
- `activation_receipt_path`
- `retirement_receipt_path`
- `notes`

## Lifecycle States

A child core may exist only in one of the following states:

- `draft`
- `active`
- `retired`

### Meaning

#### draft
The child core has been scaffolded but is not yet lawful for runtime routing.

#### active
The child core has passed structural validation and semantic validation and may
receive PM child-core delivery.

#### retired
The child core is preserved for continuity and audit but may not receive new work.

## Validation Requirements

A child core must pass two forms of validation before activation.

### Structural validation
Confirms:
- required files exist
- required directories exist
- JSON files parse
- required registry entry fields exist

### Semantic validation
Confirms:
- `DOMAIN_REGISTRY.json` contains required keys
- declared `core_id` matches registry entry
- declared `domain_focus` is present
- allowed actions exist
- forbidden actions exist
- domain focus does not collide with another active child core

## Activation Rule

No child core becomes active without:
1. creation through governed code
2. successful structural validation
3. successful semantic validation
4. registry update to `active`
5. persisted activation receipt

## Retirement Rule

Retirement must:
- preserve registry history
- write a retirement receipt
- change state to `retired`
- prevent future PM routing to that core

Retirement may not:
- silently delete the core
- erase historical receipts
- rewrite prior activation truth

## Louisville GIS Status

`louisville_gis_core` is the first proven instance of this contract.

Stage 12 formalizes that pattern so Louisville GIS is no longer a special case.
It becomes the first validated member of a governed child-core class.