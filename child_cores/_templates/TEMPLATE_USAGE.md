# TEMPLATE USAGE

## Step 1 — Create new core
Copy scaffold into:

AI_GO/child_cores/{{NEW_CORE_ID}}/

## Step 2 — Replace tokens

Required:
- {{CORE_ID}}
- {{DISPLAY_NAME}}
- {{DOMAIN_FOCUS}}
- {{APPROVAL_RECORD_TYPE}}

## Step 3 — Implement domain logic

Modify:
- execution/*
- outputs/*
- constraints/constraints.json
- DOMAIN_POLICY.md
- DOMAIN_REGISTRY.json

## Step 4 — Register core

Add entries to:
- child_core_registry.json
- PM registry

## Step 5 — Run probes

Must pass:
- structure
- ingress
- runtime
- output
- approval
- CLI/UI

## Step 6 — Set status

draft → validated → ready_for_activation → active