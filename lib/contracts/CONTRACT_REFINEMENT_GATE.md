# Contract Refinement Gate

## Purpose

This contract preserves the canonical structure and boundary rules for governed input entering the `engines/` layer of AI_GO.

A refinement gate exists to ensure that engine processing begins only from explicit, traceable, and bounded upstream artifacts.

---

## Contract Role

The refinement gate exists to:

- preserve input provenance
- define lawful engine entry
- identify the target refinement engine
- preserve scope and handling context
- prevent raw signal from entering engine processing without governed structure

A refinement gate is not a PM decision, a research packet, or a child-core execution instruction.

---

## Required Elements

Every refinement gate must contain at minimum:

- `gate_id`
- `originating_authority`
- `input_artifact_id`
- `input_type`
- `target_engine`
- `summary`
- `scope`
- `tags`
- `created_at`
- `gate_status`

---

## Contract Rules

1. The target engine must be explicit.
2. Input provenance must remain visible.
3. Raw ungoverned signal is not valid refinement input.
4. A refinement gate may not imply PM or child-core authority.
5. Engine entry must remain bounded and traceable.
6. Downstream engine receipt does not alter the original authority of the gated artifact.

---

## Invalid Conditions

A refinement gate is invalid if:

- required elements are missing
- target engine is unclear
- source artifact is not identifiable
- provenance is stripped
- raw undeclared signal is treated as governed engine input
- the gate overstates authority beyond bounded refinement entry

---

## Summary

This contract preserves the lawful entry shape for governed refinement inside AI_GO.