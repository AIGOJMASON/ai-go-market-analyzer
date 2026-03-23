# RESEARCH_CORE Layer

## Purpose

`RESEARCH_CORE/` is the root-level research authority of AI_GO.

It exists to receive external signals, normalize them, screen them, assign trust classification, and emit governed research packets for downstream interpretation.

`RESEARCH_CORE/` does not perform strategic planning, execution, long-term continuity management, or canon archival.

It is a bounded intake-and-validation layer.

---

## Authority Role

`RESEARCH_CORE/` is responsible for:

- receiving raw external inputs
- normalizing intake structures
- applying screening rules
- assigning trust classification
- building governed research packets
- handing validated outputs to downstream authorities

`RESEARCH_CORE/` is not responsible for:

- PM interpretation
- child-core execution
- system continuity state
- monitoring drift detection
- canon authorship
- runtime boot orchestration

---

## Position in the System

`RESEARCH_CORE/` sits at the root of AI_GO beside other major authorities such as:

- `boot/`
- `core/`
- `PM_CORE/`
- `engines/`
- `child_cores/`
- `lib/`
- `state/`
- `packets/`
- `telemetry/`

This placement is intentional.

Research is a first-class authority surface, not an implementation detail hidden inside runtime.

---

## Information Flow

The lawful downstream flow is:

Research Intake  
↓  
Screening  
↓  
Trust Classification  
↓  
Research Packet Emission  
↓  
Refinement / PM downstream consumers

This layer may prepare information for interpretation, but it may not perform interpretation as strategy.

---

## Internal Structure

The root of `RESEARCH_CORE/` contains the governing documents for research authority:

- `_RESEARCH_CORE_LAYER.md`
- `RESEARCH_CORE_IDENTITY.md`
- `RESEARCH_PACKET_CONTRACT.md`
- `TRUST_CLASSIFICATION_POLICY.md`
- `SCREENING_POLICY.md`
- `RESEARCH_REGISTRY.json`

Additional subdirectories under `RESEARCH_CORE/` implement the operational pipeline such as intake, screening, trust, packets, interfaces, and state.

---

## Boundary Rules

`RESEARCH_CORE/` must preserve the following boundaries:

1. Raw inputs may not pass downstream without screening.
2. Screening may not silently assign trust.
3. Trust classification must be explicit, not implied.
4. No research output becomes planning authority by itself.
5. Emitted packets must follow the research packet contract.
6. Research state must remain separate from PM state, runtime state, and canon archive.

---

## Relationship to Other Authorities

### `core/`
`core/` governs runtime, continuity, and monitoring, but does not replace research authority.

### `PM_CORE/`
`PM_CORE/` receives governed research outputs and converts them into strategic interpretation.

### `engines/`
Engines may refine or transform research inputs later, but they do not define research intake policy.

### `child_cores/`
Child cores may receive downstream strategic outputs informed by research, but do not bypass research governance.

### `lib/`
`lib/` may preserve canonized research laws and contracts, but `RESEARCH_CORE/` performs live research operations.

---

## Summary

`RESEARCH_CORE/` is the lawful research intake and validation authority of AI_GO.

It exists to ensure that external signal becomes governed research structure before any downstream interpretation or execution occurs.