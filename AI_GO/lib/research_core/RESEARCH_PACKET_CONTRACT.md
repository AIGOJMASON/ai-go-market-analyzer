# Research Packet Contract

## Purpose

This contract defines the minimum structure and authority rules for any research packet emitted by `RESEARCH_CORE`.

A research packet is the lawful downstream artifact produced after intake, screening, and trust classification.

---

## Contract Role

The research packet exists to:

- preserve the source of a research signal
- record screening outcome
- record trust classification
- summarize the validated research content
- provide a bounded handoff artifact for downstream authorities

A research packet is not a strategic decision, execution command, or canon declaration.

---

## Required Fields

Every research packet must contain at minimum:

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

## Field Definitions

### `packet_id`
Unique governed identifier for the packet.

### `packet_type`
Declared packet type such as research brief, planning brief precursor, or signal digest.

### `source_refs`
List of source identifiers or source references used in the packet.

### `title`
Short descriptive title for the packet.

### `summary`
Bounded summary of the screened and classified research signal.

### `screening_status`
Declared result of screening, such as passed, rejected, deferred, or needs_review.

### `trust_class`
Declared trust classification assigned under research trust policy.

### `confidence`
Bounded confidence value or declared confidence band.

### `scope`
Declared scope of relevance such as local, domain, core, or system.

### `tags`
Relevant controlled tags describing the signal.

### `created_at`
UTC timestamp of packet creation.

### `issuing_authority`
Must identify `RESEARCH_CORE` as the packet issuer.

---

## Optional Fields

Optional fields may include:

- `notes`
- `related_packets`
- `supporting_artifacts`
- `screening_reasons`
- `trust_rationale`
- `decision_recommendation`
- `handoff_target`

Optional fields may enrich the packet but may not replace required fields.

---

## Contract Rules

1. A packet may not be emitted without declared screening status.
2. A packet may not be emitted without declared trust classification.
3. A packet may not imply authority it does not possess.
4. A packet may not conceal missing sources behind narrative summary.
5. A packet may not act as a PM decision by format or wording.
6. A packet must remain traceable to source references.

---

## Invalid Packet Conditions

A research packet is invalid if:

- required fields are missing
- trust classification is omitted
- screening status is omitted
- issuing authority is unclear
- summary makes claims unsupported by source references
- packet language overstates authority beyond research scope

---

## Handoff Rule

Valid research packets may be handed downstream to refinement, PM, or other declared interfaces only through lawful packet surfaces.

Downstream use does not alter the original research authority of the packet.

---

## Summary

The research packet is the governed output artifact of `RESEARCH_CORE`.

It preserves research legitimacy by ensuring every downstream handoff is structured, explicit, and bounded by declared authority.