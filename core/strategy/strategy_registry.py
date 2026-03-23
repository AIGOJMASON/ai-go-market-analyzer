STRATEGY_REGISTRY = {
    "layer": "PM_CORE",
    "implementation_layer": "core/strategy",
    "modules": {
        "pm": "core/strategy/pm.py",
        "inheritance": "core/strategy/inheritance.py",
        "child_core_registry": "core/strategy/child_core_registry.py",
    },
    "receives": [
        "refinement_bundles",
    ],
    "emits": [
        "strategy_signals",
        "child_core_inheritance",
    ],
    "boundary_rules": [
        "no research authority",
        "no continuity authority",
        "no monitoring authority",
    ],
}