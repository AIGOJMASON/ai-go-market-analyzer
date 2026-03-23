# CURVED_MIRROR Layer

## Layer Status
Locked

## Layer Position
AI_GO/engines/curved_mirror/

## Parent Authority
ENGINES

## Layer Purpose
This layer contains the implementation surface for CURVED_MIRROR, AI_GO’s governed reasoning engine.

The CURVED_MIRROR layer is the engine-side implementation boundary where structured reasoning behavior is defined, constrained, and exposed to the rest of the system. It is not the place where system truth is validated, strategic authority is decided, or domain work is executed.

This layer exists to make reasoning available as a governed service inside AI_GO.

## What This Layer Implements
The CURVED_MIRROR layer implements the runtime-facing pieces required for reasoning refinement, including:

- engine invocation
- reasoning prompt structure
- reasoning policy constraints
- input/output shaping for analytical interpretation
- bounded reasoning behavior for operator-facing outputs

Typical files in this layer include:
- engine.py
- prompts.py
- policies.py

## Canonical Function
CURVED_MIRROR performs reasoning refinement.

It transforms governed inputs into structured analytical output.

Typical inputs:
- RESEARCH_PACKET
- REFINEMENT_GATE tasks
- PM-directed interpretation requests
- bounded system state needed for explanation

Typical outputs:
- reasoning_refinement
- analytical summaries
- causal interpretation
- failure-mode analysis
- implementation reasoning
- structured operator-facing explanation

## Layer Responsibilities

### 1. Analytical Engine Surface
This layer provides the callable reasoning interface used by the rest of the system.

It should make CURVED_MIRROR accessible as an engine, not as a freeform text generator.

### 2. Prompt and Policy Discipline
This layer defines the reasoning prompts and policies that keep CURVED_MIRROR structurally clear, bounded, and non-rhetorical.

Its reasoning defaults should favor:
- structure
- assumptions made explicit
- bounded inference
- causal explanation
- practical next steps
- diagnostics over theatrics

### 3. Reasoning Output Control
This layer should ensure CURVED_MIRROR output remains analytical and does not drift into:
- strategic command
- truth validation
- narrative stylization
- domain execution language

### 4. Refinement Gate Support
This layer supports the reasoning branch of the REFINEMENT_GATE.

It is the engine-side implementation of the reasoning component of REFINEMENT_BUNDLE.

## Explicit Non-Responsibilities
This layer does not perform:
- research intake
- source screening
- trust classification
- strategic prioritization
- inheritance authority
- child-core execution
- canon storage
- continuity management

Those responsibilities belong to other system layers.

## File Intent

### engine.py
Contains the callable runtime interface for CURVED_MIRROR.

This file should expose a governed reasoning entry point and return structured reasoning outputs.

### prompts.py
Contains prompt scaffolds or reasoning frames used to shape CURVED_MIRROR behavior.

Prompting here should reinforce:
- analytical clarity
- structure
- boundedness
- non-rhetorical reasoning

### policies.py
Contains engine-specific constraints and operating policy.

This should define:
- reasoning style
- output limits
- authority boundaries
- response shape expectations

## Relationship to Upstream Layers
CURVED_MIRROR depends on lawful upstream inputs.

It should trust:
- RESEARCH for validation
- PM for strategy
- LIB for canon
- SMI only for bounded continuity references when needed

It should not silently absorb those authorities into its own layer.

## Relationship to Downstream Layers
CURVED_MIRROR primarily feeds:
- REFINEMENT_BUNDLE reasoning component
- PM interpretation support
- operator-facing analytical outputs
- child-core support where analytical reasoning is required by inheritance

## Failure Modes
This layer must be protected against:
- rhetorical inflation
- unsupported certainty
- strategy leakage
- analysis turning into command authority
- prompt-driven overreach
- vague abstraction with low operational value

## Layer Rule
CURVED_MIRROR is an engine implementation layer for governed reasoning.

It exists to expose structured analytical interpretation, not to become a truth source, strategic authority, or execution layer.