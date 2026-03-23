# Contract Refinement Bundle

## Purpose

This contract preserves the canonical structure and boundary rules for refinement bundles emitted by the `engines/` layer of AI_GO.

A refinement bundle is the lawful downstream artifact produced by a declared engine after governed input has passed through a refinement gate.

---

## Contract Role

The refinement bundle exists to:

- preserve source provenance
- identify the engine that performed refinement
- summarize the bounded refinement result
- provide a lawful downstream handoff artifact
- preserve transformation traceability across engine processing

A refinement bundle is not a PM strategy command, a child-core execution instruction, or a canon declaration.

---

## Required Elements

Every refinement bundle must contain at minimum:

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

---

## Contract Rules

1. The originating engine must be explicit.
2. Source gate and source artifact must remain traceable.
3. Refinement output must remain bounded as refinement.
4. Refinement bundles may not silently become PM strategy.
5. Refinement bundles may not silently become direct execution instructions.
6. Downstream use does not alter engine origin.

---

## Invalid Conditions

A refinement bundle is invalid if:

- required elements are missing
- engine identity is omitted
- provenance is unclear
- output overstates authority beyond bounded refinement scope
- the bundle is presented as strategy or execution instead of refinement

---

## Summary

This contract preserves the lawful downstream bundle shape for engine refinement in AI_GO.