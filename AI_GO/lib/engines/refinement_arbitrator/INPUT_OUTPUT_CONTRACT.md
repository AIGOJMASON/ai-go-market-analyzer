# REFINEMENT_ARBITRATOR Input / Output Contract

## Purpose

This contract defines the lawful input, processing boundary, and output artifact shape for REFINEMENT_ARBITRATOR.

It exists to ensure that arbitration decisions are inspectable, repeatable, receipt-bearing, and bounded.

## Input Authority

REFINEMENT_ARBITRATOR accepts only governed research packets that have already passed through RESEARCH_CORE screening and trust classification.

Allowed upstream authority:

- RESEARCH_CORE

Disallowed upstream authority:

- raw user prompt as direct arbitrator input
- unscreened external source material
- PM-created speculative packets
- child-core self-generated escalation packets unless separately governed later

## Required Input Artifact

The required input artifact is a screened research packet.

Minimum required fields:

```json
{
  "packet_id": "string",
  "source_core": "research_core",
  "packet_type": "string",
  "title": "string",
  "summary": "string",
  "source_refs": ["string"],
  "trust_class": "string",
  "confidence": 0.0,
  "scope": "string",
  "tags": ["string"],
  "screening_status": "screened",
  "issuing_authority": "RESEARCH_CORE",
  "timestamp": "ISO-8601 string"
}
Optional Input Fields

Optional fields may include:

{
  "target_core_hint": "string or null",
  "domain_hint": "string or null",
  "prior_packet_refs": ["string"],
  "notes": "string or null",
  "screening_receipt_ref": "string or null",
  "trust_receipt_ref": "string or null"
}

Optional fields may influence weighting, but may not override decision rules.

Arbitrator Processing Surface

The arbitrator may derive the following internal working values:

reasoning_weight

human_tempering_weight

child_core_fit_scores

composite_weight

entropy_status

recommendation

These values must be surfaced in the output artifact or receipt. Hidden decision-critical values are not allowed.

Engine Invocation Contract

REFINEMENT_ARBITRATOR may invoke:

Curved Mirror

Rosetta

Invocation is conditional, not automatic.

Curved Mirror invocation purpose

Curved Mirror is used to estimate structural worth, including:

domain fit

specificity

repeatability

downstream utility

reasoning coherence

Rosetta invocation purpose

Rosetta is used to estimate human-facing tempering value, including:

clarity

communicative usability

interpretive accessibility

narrative shaping relevance

presentation fitness

Output Artifact

The output artifact is an arbitration decision packet.

Minimum required fields:

{
  "arbitration_id": "string",
  "source_packet_id": "string",
  "issuing_layer": "REFINEMENT_ARBITRATOR",
  "reasoning_weight": 0.0,
  "human_tempering_weight": 0.0,
  "child_core_fit_scores": {
    "child_core_name": 0.0
  },
  "composite_weight": 0.0,
  "recommended_action": "discard|hold|condition_for_child_core|send_to_curved_mirror|send_to_rosetta|pass_to_pm",
  "justification_summary": "string",
  "timestamp": "ISO-8601 string"
}
Optional Output Fields

Optional fields may include:

{
  "target_child_core": "string or null",
  "engine_invocations": [
    {
      "engine": "curved_mirror|rosetta",
      "status": "invoked|skipped",
      "receipt_ref": "string or null"
    }
  ],
  "entropy_status": "low|medium|high",
  "gravity_status": "low|medium|high",
  "grace_status": "low|medium|high",
  "decision_threshold_band": "string",
  "hold_reason": "string or null",
  "discard_reason": "string or null",
  "condition_profile_ref": "string or null",
  "receipt_ref": "string or null"
}
Output Authority

REFINEMENT_ARBITRATOR output is advisory for downstream propagation, but authoritative for its own layer decision.

That means:

PM_CORE may rely on the recommendation

PM_CORE still owns routing authority

the arbitrator owns the validity of the recommendation artifact it emitted

Illegal Outputs

The arbitrator must never emit output that:

directly activates a child core

mutates child-core lifecycle state

declares PM routing complete

rewrites research trust classification

writes continuity memory as though it were PM memory

bypasses receipt generation

omits the scored basis for recommendation

Receipt Requirement

Every arbitration output must produce or reference an arbitration receipt.

Minimum receipt contents:

arbitration_id

source_packet_id

decision

score summary

invoked engines

target child-core recommendation if any

timestamp

issuing layer

Contract Summary

Input: screened RESEARCH_CORE packet
Output: scored arbitration decision packet
Authority: propagation recommendation only
Non-authority: routing, execution, continuity truth, research truth mutation