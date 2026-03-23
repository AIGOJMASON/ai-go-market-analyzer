from __future__ import annotations

from typing import Dict, Any


class InheritancePlanner:
    """
    Determines which child cores should inherit the planning signal.
    """

    def determine_inheritance(
        self,
        strategy_signal: Dict[str, Any],
        available_cores: Dict[str, Any],
    ) -> Dict[str, Any]:

        selected_cores = []

        signal_type = strategy_signal.get("signal_type")

        for core_name in available_cores.keys():
            if signal_type and signal_type in core_name:
                selected_cores.append(core_name)

        return {
            "inheritance_status": "planned",
            "selected_child_cores": selected_cores,
        }