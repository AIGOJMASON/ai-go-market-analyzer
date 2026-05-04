# Stage 28 — Continuity Distribution Policy

## Allowed Input

Only:
- `continuity_read_request`

All other inputs are rejected.

---

## Required Request Fields

The incoming `continuity_read_request` must contain:
- `request_type`
- `request_id`
- `requesting_surface`
- `consumer_profile`
- `target_core`
- `continuity_scope`
- `read_reason`
- `requested_view`
- `policy_version`
- `timestamp`

---

## Named Consumer Profiles

Stage 28 uses named consumer profiles to enforce lawful read behavior.

A profile defines:
- which requesting surfaces may use it
- which target cores it may read
- which scopes it may read
- which views it may request
- which default view applies if needed
- the maximum record count it may receive
- the shaping mode used for the returned records

Profiles are access and packaging controls only.

They may not:
- mutate continuity
- prioritize actions
- create strategy decisions
- reinterpret continuity into new meaning

---

## Allowed Outcomes

### 1. fulfilled
The request is lawful and a bounded continuity distribution artifact is emitted.

### 2. held
The request is structurally valid but requires review or a supported view is not yet ready for automatic fulfillment.

### 3. rejected
The request is invalid, unlawful, overbroad, or unsupported.

---

## Required Checks

### 1. Request Integrity
- `request_type` must equal `continuity_read_request`

### 2. Profile Integrity
- `consumer_profile` must be registered
- `requesting_surface` must be allowed to use that profile

### 3. Requester Legality
- `requesting_surface` must be registered through a valid profile-target relationship

### 4. Target Legality
- `target_core` must be registered for distribution
- target must be allowed by the consumer profile

### 5. Scope Legality
- `continuity_scope` must be allowed for both target and consumer profile

### 6. View Legality
- `requested_view` must be one of the views allowed by the consumer profile for the target

### 7. Policy Version Compatibility
- request `policy_version` must be allowed by the Stage 28 distribution registry

### 8. Result Boundedness
- only the allowed continuity subset may be returned
- returned record count must not exceed profile maximum
- no raw unrestricted store dump is allowed

---

## Allowed View Types

Stage 28 may support only bounded view modes such as:
- `latest_record`
- `latest_n_records`
- `refs_only`
- `summary_stub`

No view may expose the entire raw store without explicit future policy.

---

## Profile Shaping Modes

Example shaping modes may include:
- `full_bounded`
- `refs_only`
- `summary_stub`

The shaping mode may narrow the returned structure below the requested view.
It may not widen it.

---

## Hold Conditions

A request may be held when:
- structure is valid
- profile is valid
- requester is valid
- but the requested view requires review or deferred support

A hold must emit:
- hold reason
- release condition
- review window if available

A hold may not mutate continuity.

---

## Rejection Conditions

Reject when:
- request type is invalid
- required fields are missing or malformed
- consumer profile is unregistered
- requesting surface is not allowed for the profile
- target is unregistered
- target is not allowed for the profile
- scope is unlawful
- requested view is unsupported
- policy version is invalid

---

## Distribution Rules

- reads must be deterministic
- reads must not mutate continuity state
- distribution artifacts must be bounded
- receipts must record the policy version used
- distribution must preserve record lineage references when present
- profile shaping may narrow but not widen output