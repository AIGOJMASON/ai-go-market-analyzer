from __future__ import annotations

try:
    from AI_GO.core.awareness.cross_run_intelligence import (
        append_unified_awareness_history_record,
        build_cross_run_intelligence_packet,
        summarize_cross_run_intelligence,
    )
except Exception:
    append_unified_awareness_history_record = None
    build_cross_run_intelligence_packet = None
    summarize_cross_run_intelligence = None

try:
    from AI_GO.core.awareness.operator_system_brain_surface import (
        build_operator_system_brain_surface,
    )
except Exception:
    build_operator_system_brain_surface = None

try:
    from AI_GO.core.awareness.pattern_recognition import build_pattern_recognition_packet
except Exception:
    build_pattern_recognition_packet = None

try:
    from AI_GO.core.awareness.posture_explanation import build_posture_explanation_packet
except Exception:
    build_posture_explanation_packet = None

from AI_GO.core.awareness.smi_pattern_posture_reader import (
    build_smi_pattern_posture_packet,
    summarize_smi_pattern_posture,
)

try:
    from AI_GO.core.awareness.temporal_awareness import build_temporal_awareness_packet
except Exception:
    build_temporal_awareness_packet = None

try:
    from AI_GO.core.awareness.unified_system_awareness import (
        build_unified_system_awareness_packet,
        summarize_unified_system_awareness,
    )
except Exception:
    build_unified_system_awareness_packet = None
    summarize_unified_system_awareness = None


__all__ = [
    "append_unified_awareness_history_record",
    "build_cross_run_intelligence_packet",
    "summarize_cross_run_intelligence",
    "build_operator_system_brain_surface",
    "build_pattern_recognition_packet",
    "build_posture_explanation_packet",
    "build_smi_pattern_posture_packet",
    "summarize_smi_pattern_posture",
    "build_temporal_awareness_packet",
    "build_unified_system_awareness_packet",
    "summarize_unified_system_awareness",
]