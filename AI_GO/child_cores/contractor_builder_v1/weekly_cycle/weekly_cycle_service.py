from __future__ import annotations

from typing import Any, Dict

from AI_GO.child_cores.contractor_builder_v1.weekly_cycle.weekly_cycle_executor import (
    execute_weekly_cycle_run,
)
from AI_GO.core.execution_gate.runtime_execution_gate import enforce_execution_gate
from AI_GO.core.governance.governed_context_builder import build_governed_context
from AI_GO.core.governance.governance_failure import raise_governance_failure
from AI_GO.core.state_runtime.contractor_state_profiles import (
    validate_weekly_cycle_state,
)
from AI_GO.core.watcher.contractor_watcher_profiles import watch_weekly_cycle


def run_governed_weekly_cycle(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = "weekly_cycle_run"

    state = validate_weekly_cycle_state(
        action=action,
        request=payload,
    )

    watcher = watch_weekly_cycle(
        action=action,
        request=payload,
    )

    context = build_governed_context(
        profile="contractor_weekly_cycle",
        action=action,
        route="/contractor-builder/weekly-cycle/run",
        request=payload,
        state=state,
        watcher=watcher,
    )

    if not state.get("valid"):
        raise_governance_failure(
            error="weekly_cycle_state_validation_failed",
            message="Weekly cycle state validation failed",
            context=context,
        )

    if not watcher.get("valid"):
        raise_governance_failure(
            error="weekly_cycle_watcher_validation_failed",
            message="Weekly cycle watcher validation failed",
            context=context,
        )

    enforce_execution_gate(context["execution_gate"])

    result = execute_weekly_cycle_run(context)

    return {
        "mode": "governed_execution",
        **context,
        **result,
    }