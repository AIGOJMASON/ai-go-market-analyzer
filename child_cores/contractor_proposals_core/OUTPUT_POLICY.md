# OUTPUT POLICY

## What it is

Output validation policy for `contractor_proposals_core`.

## Why it is there

Defines the minimum bounded output structure for the contractor proposals domain.

## Output Rule

Every emitted output must:
- preserve packet linkage
- preserve inheritance linkage
- remain domain-bounded
- be inspectable
- be verifiable by child-core watcher

## Minimum Output Shape

A lawful output artifact must include:
- `output_id`
- `core_id`
- `packet_id`
- `domain_focus`
- `proposal_type`
- `client_request_summary`
- `recommended_sections`
- `next_action`