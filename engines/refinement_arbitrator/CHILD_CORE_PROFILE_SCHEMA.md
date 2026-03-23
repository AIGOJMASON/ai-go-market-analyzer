# REFINEMENT_ARBITRATOR Child-Core Profile Schema

## Purpose

This schema defines the profile structure used by REFINEMENT_ARBITRATOR to score child-core fit.

A child-core profile tells the arbitrator what kinds of signal are useful, what weighting emphasis should apply, and what contamination patterns should be resisted.

## Profile Role

A child-core profile is not a child-core runtime file.

It is an arbitration conditioning file used only for upstream propagation judgment.

Its purpose is to help answer:

- Which packets fit this core
- Which weights matter most for this core
- Which patterns should be rejected or penalized
- Which types of refinement are useful before PM sees the packet

## Minimum Profile Fields

```json
{
  "child_core_id": "string",
  "child_core_name": "string",
  "status": "active|draft|retired",
  "domain_type": "string",
  "reasoning_coefficient": 0.0,
  "human_tempering_coefficient": 0.0,
  "core_fit_coefficient": 0.0,
  "accepted_signal_patterns": ["string"],
  "rejected_signal_patterns": ["string"],
  "contamination_risks": ["string"],
  "preferred_refinement_order": ["curved_mirror", "rosetta"],
  "last_updated": "ISO-8601 string"
}
Constraint:

reasoning_coefficient + human_tempering_coefficient + core_fit_coefficient = 1.00

Optional Fields
{
  "domain_keywords": ["string"],
  "task_biases": ["string"],
  "required_specificity_level": "low|medium|high",
  "preferred_packet_types": ["string"],
  "hold_conditions": ["string"],
  "discard_conditions": ["string"],
  "conditioning_notes": "string or null",
  "max_contamination_penalty": 0.0,
  "profile_authority": "string",
  "receipt_ref": "string or null"
}
Semantics
child_core_id / child_core_name

Canonical identity of the target child core.

status

Only active cores should receive normal fit scoring for downstream propagation.
Draft or retired cores may still be scored for analysis, but should not receive pass-through propagation unless separately governed.

domain_type

Short label for the type of work the core performs.

Examples:

geospatial

proposals

narrative

education

analytics

coefficients

These govern the relative importance of:

reasoning weight

human tempering weight

core-specific fit

accepted_signal_patterns

Patterns that strengthen the likelihood that this packet belongs to the core.

Examples:

contractor estimate workflows

Louisville zoning and parcel data

municipal boundary analysis

bid formatting logic

rejected_signal_patterns

Patterns that should strongly reduce or negate fit.

Examples:

generic motivational content

broad unrelated education theory

vague business advice without operational relevance

contamination_risks

Patterns that risk domain bleed or false fit.

Examples:

narrative-rich but operationally weak content for a proposal core

structured local data with no execution relevance for a writing core

preferred_refinement_order

Default engine sequence for that core.

System default should remain:

curved_mirror

rosetta

But future profiles may tighten invocation preference.

Example Profile: contractor_proposals_core
{
  "child_core_id": "contractor_proposals_core",
  "child_core_name": "contractor_proposals_core",
  "status": "active",
  "domain_type": "proposals",
  "reasoning_coefficient": 0.50,
  "human_tempering_coefficient": 0.15,
  "core_fit_coefficient": 0.35,
  "accepted_signal_patterns": [
    "estimate logic",
    "proposal workflow",
    "change order relevance",
    "contractor quoting process"
  ],
  "rejected_signal_patterns": [
    "generic inspirational content",
    "vague market commentary"
  ],
  "contamination_risks": [
    "narrative-only shaping without operational structure"
  ],
  "preferred_refinement_order": [
    "curved_mirror",
    "rosetta"
  ],
  "last_updated": "2026-03-17T00:00:00Z"
}
Example Profile: louisville_gis_core
{
  "child_core_id": "louisville_gis_core",
  "child_core_name": "louisville_gis_core",
  "status": "active",
  "domain_type": "geospatial",
  "reasoning_coefficient": 0.55,
  "human_tempering_coefficient": 0.10,
  "core_fit_coefficient": 0.35,
  "accepted_signal_patterns": [
    "parcel data",
    "address intelligence",
    "map layer relevance",
    "Louisville location-specific data"
  ],
  "rejected_signal_patterns": [
    "generic business coaching",
    "non-local unsituated data"
  ],
  "contamination_risks": [
    "non-geospatial business content that only appears locally adjacent"
  ],
  "preferred_refinement_order": [
    "curved_mirror",
    "rosetta"
  ],
  "last_updated": "2026-03-17T00:00:00Z"
}
Schema Rule

Profiles must remain short, structural, and inspectable.

They are not essays. They are weighting-control surfaces.

Summary

A child-core profile defines how REFINEMENT_ARBITRATOR interprets downstream usefulness for a specific child core without collapsing into routing authority or memory logic.