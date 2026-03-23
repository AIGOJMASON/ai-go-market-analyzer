# Stage 29 — Continuity Consumption Policy

## Allowed Input

Only:
- `continuity_distribution_artifact`
- `continuity_distribution_receipt`

Both are required for automatic fulfillment.

All other inputs are rejected.

---

## Required Artifact Fields

The incoming `continuity_distribution_artifact` must contain:
- `artifact_type`
- `distribution_id`
- `target_core`
- `continuity_scope`
- `requested_view`
- `consumer_profile`
- `records`
- `record_count`
- `timestamp`

---

## Required Receipt Fields

The incoming `continuity_distribution_receipt` must contain:
- `receipt_type`
- `distribution_receipt_id`
- `request_id`
- `target_core`
- `requesting_surface`
- `consumer_profile`
- `requested_view`
- `artifact_id`
- `policy_version`
- `timestamp`

---

## Consumer Profiles

Stage 29 uses named consumer profiles to govern lawful downstream transformation.

A profile defines:
- allowed requesting surfaces
- allowed target cores
- allowed continuity scopes
- allowed requested views
- allowed transformation types
- allowed output packet classes

Profiles are transformation controls only.

They may not:
- mutate continuity
- create new access rights
- trigger execution
- replace PM or strategy judgment with undeclared logic

---

## Allowed Outcomes

### 1. fulfilled
The artifact and receipt are lawful and a bounded downstream packet is emitted.

### 2. held
The artifact is structurally valid but the requested transformation requires review or is not yet supported for automatic fulfillment.

### 3. rejected
The artifact is invalid, unlawful, misaligned with the receipt, or unsupported for the consumer profile.

---

## Required Checks

### 1. Artifact Integrity
- `artifact_type` must equal `continuity_distribution_artifact`

### 2. Receipt Integrity
- `receipt_type` must equal `continuity_distribution_receipt`

### 3. Artifact / Receipt Alignment
The following must align:
- `distribution_id == artifact_id`
- `target_core`
- `consumer_profile`
- `requested_view`

### 4. Consumer-Profile Legality
- `consumer_profile` must be registered
- `requesting_surface` must be allowed for that profile

### 5. Target and Scope Legality
- target must be allowed for the profile
- continuity scope must be allowed for the profile

### 6. View Legality
- requested view must be allowed for the profile

### 7. Policy-Version Compatibility
- incoming Stage 28 distribution policy version must be allowed

### 8. Transformation Legality
- the selected transformation type must be allowed for the profile

### 9. Output Boundedness
- output packet must be one of the allowed packet classes for the profile
- no output may widen beyond the distributed artifact

---

## Transformation Types

Example allowed transformation types:
- `pm_planning_brief`
- `strategy_signal_packet`
- `child_core_context_packet`

These are bounded output classes, not open-ended reasoning modes.

---

## Hold Conditions

A request may be held when:
- artifact and receipt are valid
- profile is valid
- but the selected transformation type requires review or is deferred

A hold must emit:
- hold reason
- release condition
- review window if available

---

## Rejection Conditions

Reject when:
- artifact type is invalid
- receipt type is invalid
- required fields are missing or malformed
- artifact / receipt alignment fails
- consumer profile is unregistered
- requesting surface is not allowed for the profile
- target is unlawful
- scope is unlawful
- requested view is unlawful
- policy version is invalid
- transformation type is unsupported or unlawful

---

## Consumption Rules

- transformations must be deterministic
- output packets must be bounded
- output packets must preserve lineage refs where present
- no mutation of continuity may occur
- no direct store access may occur from this stage
- profile shaping may narrow the output but may not widen it