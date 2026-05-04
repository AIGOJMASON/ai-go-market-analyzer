# WATCHER CONTRACT

## Role
Watcher is a downstream observer of system outputs.

## Permissions
- Read validated artifacts
- Read closed lifecycle outputs

## Prohibited Actions
- Cannot create artifacts
- Cannot modify artifacts
- Cannot trigger any upstream process
- Cannot write to any system layer

## Access Scope
- Limited to output registry only
- No direct access to core, state, or packets

## Authority Level
- NONE (read-only entity)

## Enforcement
Any attempt to:
- mutate
- trigger
- bypass output policy

must be rejected.