# RESEARCH_CORE Packet Schema

## Purpose

This schema defines the runtime packet shape emitted by `RESEARCH_CORE/packets/packet_builder.py`.

It operationalizes the root `RESEARCH_PACKET_CONTRACT.md` into a concrete field structure for packet artifacts.

---

## Required Fields

Every research packet must contain:

- `packet_id`
- `packet_type`
- `source_refs`
- `title`
- `summary`
- `screening_status`
- `trust_class`
- `confidence`
- `scope`
- `tags`
- `created_at`
- `issuing_authority`

---

## Runtime Field Shape

### `packet_id`
String. Governed unique identifier for the packet.

### `packet_type`
String. Declared packet type.

### `source_refs`
List. Source identifiers or structured source references.

### `title`
String. Short descriptive packet title.

### `summary`
String. Bounded research summary.

### `screening_status`
String. One of the lawful screening outcomes.

### `trust_class`
String. Explicit trust handling class.

### `confidence`
Number. Bounded confidence indicator for downstream handling.

### `scope`
String. Declared scope of relevance.

### `tags`
List of strings. Controlled descriptive tags.

### `created_at`
String. UTC timestamp in ISO format.

### `issuing_authority`
String. Must identify `RESEARCH_CORE`.

---

## Optional Runtime Fields

A packet may also contain:

- `notes`
- `screening_reasons`
- `trust_rationale`
- `handoff_target`

These optional fields may enrich packet visibility but may not replace required fields.

---

## Schema Rule

The packet schema is an implementation schema.

If runtime packet shape and root packet contract diverge, the root contract remains authoritative and the implementation must be corrected.