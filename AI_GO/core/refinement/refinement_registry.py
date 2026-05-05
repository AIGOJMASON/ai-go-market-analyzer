REFINEMENT_REGISTRY = {
    "layer": "REFINEMENT",
    "implementation_layer": "core/refinement",
    "modules": {
        "refinement_gate": "core/refinement/refinement_gate.py",
        "pm_refinement": "core/refinement/pm_refinement.py",
        "reasoning_refinement": "core/refinement/reasoning_refinement.py",
        "narrative_refinement": "core/refinement/narrative_refinement.py",
    },
    "artifact_surfaces": {
        "refinement_packets": "packets/refinement/",
    },
    "receives": [
        "research_packets",
    ],
    "emits": [
        "refinement_bundles",
        "refinement_interpretation_surfaces",
    ],
    "boundary_rules": [
        "no planning authority",
        "no continuity authority",
        "no monitoring authority",
    ],
}