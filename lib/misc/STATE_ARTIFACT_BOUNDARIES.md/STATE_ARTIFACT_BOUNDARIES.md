# State Artifact Boundaries

## state/
Current mutable working system state only.

Examples:
- active continuity
- unresolved queues
- runtime session state
- sentinel working state

## packets/
Formal governed transfer artifacts only.

Examples:
- research packets
- refinement bundles
- inheritance packets

## telemetry/
Historical operational records only.

Examples:
- receipts
- audits
- transition logs
- event streams

## lib/
Canon and reference authority only.

Examples:
- definitions
- contracts
- policies
- naming canon
- handoffs
- archives

## Prohibitions
- state/ must not act as archive
- packets/ must not hold mutable working state
- telemetry/ must not become canon
- lib/ must not hold live mutable runtime state