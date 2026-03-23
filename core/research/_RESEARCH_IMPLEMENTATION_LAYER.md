# Research Implementation Layer

## Purpose

This document defines the runtime implementation layer for RESEARCH_CORE inside AI_GO.

RESEARCH_CORE is the system’s intake and truth-filtering layer.

It is responsible for:

- receiving external signal
- normalizing intake inputs
- screening source material
- classifying trust
- assembling validated research packets

RESEARCH_CORE does not make planning decisions.
RESEARCH_CORE does not perform strategic inheritance.
RESEARCH_CORE does not execute child-core domain work.

Its job is intake, screening, trust classification, and packet emission.

---

## Runtime Surface

RESEARCH_CORE runtime implementation lives in:

core/research/

Primary files:

- intake.py
- screening.py
- trust.py
- packet_builder.py
- research_registry.py

Artifact output surface lives in:

packets/research/

---

## Receives

RESEARCH_CORE receives:

- external signal
- source material
- source metadata
- optional intake context
- optional source references

---

## Emits

RESEARCH_CORE emits:

- validated research packets
- screening outcomes
- trust classification results
- intake-normalized source records

---

## Boundary Rules

RESEARCH_CORE must not:

- make PM planning decisions
- emit child-core inheritance decisions
- bypass refinement
- act as continuity authority
- act as monitoring authority

RESEARCH_CORE may only emit structured research outputs that are ready for
downstream refinement and later strategic interpretation.

---

## Internal Components

### intake.py
Normalizes raw intake into a governed intake record.

### screening.py
Applies screening rules to source material and signal candidates.

### trust.py
Assigns trust classification and confidence surfaces to screened inputs.

### packet_builder.py
Builds validated research packets for downstream refinement.

### research_registry.py
Declares the research-layer module surface and artifact surface.

---

## Connection Law

RESEARCH_CORE sits downstream of runtime input and upstream of refinement.

It receives raw external signal and source material, converts them into
screened and trust-classified records, and emits validated research packets
for the refinement layer.

It does not self-authorize strategic motion.

---

## Summary

RESEARCH_CORE is the intake and truth-filtering layer of AI_GO.

It receives external signal, screens and classifies it, and emits validated
research packets without crossing into planning or execution authority.