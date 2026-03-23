RESEARCH_REGISTRY = {
    "layer": "RESEARCH_CORE",
    "implementation_layer": "core/research",
    "modules": {
        "intake": "core/research/intake.py",
        "screening": "core/research/screening.py",
        "trust": "core/research/trust.py",
        "packet_builder": "core/research/packet_builder.py",
    },
    "artifact_surfaces": {
        "research_packets": "packets/research/",
    },
    "receives": [
        "external signal",
        "source material",
        "source metadata",
    ],
    "emits": [
        "validated research packets",
        "screening outcomes",
        "trust classification results",
    ],
    "boundary_rules": [
        "no planning decisions",
        "no refinement bypass",
        "no continuity authority",
        "no monitoring authority",
    ],
}