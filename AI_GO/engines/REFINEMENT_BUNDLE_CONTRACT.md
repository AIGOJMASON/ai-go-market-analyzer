# Refinement Bundle Contract

## Purpose

This contract defines the minimum structure and authority rules for any refinement bundle emitted by the `engines/` layer.

A refinement bundle is the lawful downstream artifact produced after governed input passes through a declared engine surface.

---

## Contract Role

The refinement bundle exists to:

- preserve the source of the upstream governed signal
- record which engine performed the refinement
- summarize the bounded interpretive or transformational result
- provide a lawful handoff artifact for downstream PM or other declared consumers
- preserve provenance across transformation

A refinement bundle is not a strategic command, a child-core execution instruction, or a canon declaration.

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

## Element Definitions

### `bundle_id`
Unique governed identifier for the refinement bundle.

### `originating_engine`
Declared engine that produced the refinement result.

### `source_gate_id`
Identifier of the refinement gate event that admitted the input.

### `source_artifact_id`
Identifier of the upstream governed artifact that was refined.

### `bundle_type`
Declared refinement bundle type such as reasoning refinement, narrative refinement, or other bounded engine output class.

### `summary`
Bounded summary of the refinement result.

### `scope`
Declared scope of relevance such as domain, local, core, or system.

### `tags`
Controlled descriptive tags for the bundle.

### `created_at`
UTC timestamp of bundle emission.

### `bundle_status`
Declared bundle state such as emitted, deferred, held, or rejected.

---

## Contract Rules

1. A refinement bundle must preserve visible provenance.
2. A refinement bundle must identify the engine that produced it.
3. A refinement bundle may not silently become PM strategy.
4. A refinement bundle may not become direct child-core execution by wording or format.
5. Refinement output must remain bounded and traceable.
6. Bundle language may not imply authority it does not possess.

---

## Invalid Bundle Conditions

A refinement bundle is invalid if:

- required elements are missing
- originating engine is omitted
- source gate or source artifact is unclear
- summary makes claims unsupported by the upstream governed input
- the output overstates authority beyond bounded refinement scope

---

## Handoff Rule

Valid refinement bundles may be handed downstream to `PM_CORE`, declared child-core pathways, or other lawful consumers only through declared interface surfaces.

Downstream use does not alter the original engine authority of the bundle.

---

## Summary

The refinement bundle is the governed output artifact of the `engines/` layer.

It preserves refinement legitimacy by ensuring every downstream handoff is structured, explicit, and bounded by declared authority.