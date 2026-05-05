# Refinement Gate Contract

## Purpose

This contract defines the minimum structure and boundary rules for any governed input entering the `engines/` layer.

A refinement gate exists to preserve lawful entry into engine surfaces so interpretation cannot begin from raw, detached, or provenance-free signal.

---

## Contract Role

The refinement gate exists to:

- preserve the origin of upstream governed signal
- define the allowed entry shape for engine processing
- record the declared target engine or refinement path
- preserve scope and handling context
- prevent engines from receiving raw signal as if it were already governed input

A refinement gate artifact is not a PM decision, a research intake record, or a child-core execution command.

---

## Required Elements

Every refinement-gated input must contain at minimum:

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

## Element Definitions

### `gate_id`
Unique governed identifier for the refinement gate event.

### `originating_authority`
Declared upstream authority that issued or forwarded the governed input.

### `input_artifact_id`
Identifier of the governed upstream artifact entering refinement.

### `input_type`
Declared input type such as research packet, planning input, or other governed artifact class.

### `target_engine`
Declared engine intended to process the input.

### `summary`
Bounded summary of the governed input entering the engine layer.

### `scope`
Declared scope of relevance such as local, domain, core, or system.

### `tags`
Controlled descriptive tags associated with the input.

### `created_at`
UTC timestamp of gate creation.

### `gate_status`
Declared gate state such as prepared, accepted, deferred, or rejected.

---

## Contract Rules

1. Engine entry must be explicit.
2. The target engine must be declared.
3. Input provenance must remain visible.
4. A refinement gate may not imply PM strategy or execution authority.
5. Raw unscreened input may not be treated as valid gated refinement input.
6. Gate language may not overstate authority beyond bounded refinement entry.

---

## Invalid Gate Conditions

A refinement gate is invalid if:

- required elements are missing
- target engine is unclear
- input origin is omitted
- input artifact is not identifiable
- the summary overstates authority beyond refinement scope
- the gate attempts to smuggle raw signal into engine processing without governed provenance

---

## Boundary Rule

Valid refinement-gated inputs may move from declared upstream authorities into declared engine surfaces only through lawful interface pathways.

Receipt by an engine does not alter the originating authority of the gated input artifact.

---

## Summary

The refinement gate contract is the governed entry artifact of the `engines/` layer.

It preserves authority separation by ensuring engine input remains explicit, traceable, and bounded before interpretation begins.