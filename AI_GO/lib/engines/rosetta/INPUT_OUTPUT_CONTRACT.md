# Rosetta Input / Output Contract

## Purpose

This contract defines the minimum structure and boundary rules for governed input entering the `rosetta` engine and the narrative refinement bundle emitted from it.

The contract exists so Rosetta processing remains explicit, traceable, and bounded.

---

## Input Contract

Rosetta may only accept inputs that have already passed through a lawful refinement gate.

### Required Input Elements

Every Rosetta input must contain at minimum:

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

### Input Rules

1. The target engine must identify `rosetta`.
2. Input provenance must remain visible.
3. Raw ungoverned signal is not valid engine input.
4. The input may not imply PM or execution authority.

---

## Output Contract

Rosetta emits a narrative refinement bundle.

### Required Output Elements

Every Rosetta output must contain at minimum:

- `bundle_id`
- `originating_engine`
- `source_gate_id`
- `source_artifact_id`
- `bundle_type`
- `summary`
- `scope`
- `tags`
- `created_at`
- `bundle_status`

### Output Rules

1. The originating engine must identify `rosetta`.
2. Output must preserve traceability to the source gate and source artifact.
3. Output must remain bounded as narrative refinement.
4. Output may not silently become PM strategic authority or child-core execution instruction.

---

## Invalid Conditions

Rosetta processing is invalid if:

- required input or output elements are missing
- the source gate is not identifiable
- the target engine is not Rosetta
- provenance is stripped
- the output overstates authority beyond bounded narrative refinement

---

## Summary

This contract preserves lawful entry and lawful output for the `rosetta` engine.

It ensures narrative refinement remains explicit, provenance-preserving, and bounded.