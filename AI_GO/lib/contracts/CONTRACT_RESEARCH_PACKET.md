# Contract Research Packet

## Purpose

This contract preserves the canonical structure and boundary rules for a governed research packet within AI_GO.

A research packet is the lawful downstream artifact emitted by `RESEARCH_CORE` after intake, screening, and trust classification have occurred.

---

## Contract Role

The research packet exists to:

- preserve source provenance
- record screening outcome
- record trust classification
- summarize governed research signal
- provide a bounded handoff artifact for downstream authorities

A research packet is not a PM decision, a child-core execution command, or a canon declaration.

---

## Required Elements

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

## Contract Rules

1. A research packet must preserve visible source provenance.
2. Screening status must be explicit.
3. Trust class must be explicit.
4. Research packets may not silently become strategic authority.
5. Research packets may not overstate certainty beyond governed research scope.
6. Downstream use does not alter originating research authority.

---

## Invalid Conditions

A research packet is invalid if:

- required elements are missing
- source provenance is unclear
- screening status is omitted
- trust class is omitted
- the packet implies PM or execution authority
- the summary exceeds the justified scope of the underlying research signal

---

## Summary

This contract preserves the lawful packet shape of governed research output in AI_GO.