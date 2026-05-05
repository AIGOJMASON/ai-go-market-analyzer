# OUTPUT POLICY

## Visibility Rules
- Only CLOSED artifacts may be exposed
- Only validated + accepted artifacts allowed

## Rejection Rules
Reject if:
- lifecycle_state != CLOSED
- missing validation_receipt_ref
- schema mismatch
- invalid artifact_type

## Filtering
- By artifact_type
- By consumer (watcher, CLI)

## Enforcement
All outputs must pass:
1. Schema validation
2. Policy validation

Failure at any step → reject