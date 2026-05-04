# PM_CORE Inheritance Packet Schema

## Purpose

This schema defines the runtime handoff shape emitted by `PM_CORE/inheritance/`.
It operationalizes the root `CHILD_CORE_INHERITANCE_CONTRACT.md` into a concrete implementation shape.

---

## Required Fields

Every inheritance packet must contain:

- `inheritance_id`
- `originating_authority`
- `target_child_core`
- `planning_summary`
- `strategic_signal`
- `scope`
- `tags`
- `created_at`
- `inheritance_status`

---

## Runtime Field Shape

### `inheritance_id`
String. Governed unique identifier for the inheritance handoff.

### `originating_authority`
String. Must identify `PM_CORE`.

### `target_child_core`
String. Declared child core intended to receive the planning signal.

### `planning_summary`
String. Bounded summary of the PM planning intent.

### `strategic_signal`
String. Explicit PM strategic interpretation result.

### `scope`
String. Declared scope of relevance.

### `tags`
List of strings. Controlled descriptive tags.

### `created_at`
String. UTC timestamp in ISO format.

### `inheritance_status`
String. Declared handoff state such as prepared, issued, deferred, or rejected.

---

## Optional Runtime Fields

A packet may also contain:

- `propagation_allowed`
- `source_pm_refinement_id`
- `source_packet_id`
- `strategic_rationale`
- `propagation_rationale`
- `notes`

These optional fields add visibility but may not replace required fields.

---

## Schema Rule

The inheritance packet schema is an implementation schema.

If runtime handoff shape and the root inheritance contract diverge, the root contract remains authoritative and the implementation must be corrected.