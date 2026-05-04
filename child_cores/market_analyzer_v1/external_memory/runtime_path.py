# AI_GO/child_cores/market_analyzer_v1/external_memory/runtime_path.py

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict

try:
    from AI_GO.child_cores.market_analyzer_v1.external_memory.outbound_ingress import (
        build_outbound_memory_ingress_record,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.qualification_engine import (
        run_qualification_engine,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.persistence_gate import (
        run_persistence_gate,
    )
    from AI_GO.child_cores.market_analyzer_v1.external_memory.db_writer import (
        run_db_writer,
    )
except ModuleNotFoundError:
    from child_cores.market_analyzer_v1.external_memory.outbound_ingress import (  # type: ignore
        build_outbound_memory_ingress_record,
    )
    from child_cores.market_analyzer_v1.external_memory.qualification_engine import (  # type: ignore
        run_qualification_engine,
    )
    from child_cores.market_analyzer_v1.external_memory.persistence_gate import (  # type: ignore
        run_persistence_gate,
    )
    from child_cores.market_analyzer_v1.external_memory.db_writer import (  # type: ignore
        run_db_writer,
    )


class ExternalMemoryAdmissionRuntimeError(ValueError):
    pass


def run_market_analyzer_external_memory_admission(
    child_core_result: Dict[str, Any],
    *,
    target_child_core_id: str = "market_analyzer_v1",
) -> Dict[str, Any]:
    if not isinstance(child_core_result, dict):
        raise ExternalMemoryAdmissionRuntimeError("child_core_result must be a dict")

    sealed_result = deepcopy(child_core_result)

    ingress_record = build_outbound_memory_ingress_record(
        sealed_result,
        target_child_core_id=target_child_core_id,
        source_type="child_core_output",
    )

    qualification_result = run_qualification_engine(ingress_record)
    persistence_gate_result = run_persistence_gate(ingress_record, qualification_result)

    db_write_result: Dict[str, Any] | None = None
    if persistence_gate_result.get("allow_persist") is True:
        db_write_result = run_db_writer(
            ingress_record,
            qualification_result,
            persistence_gate_result,
        )

    return {
        "status": "written" if db_write_result else "blocked",
        "external_memory_ingress_record": ingress_record,
        "external_memory_qualification_result": qualification_result,
        "external_memory_persistence_gate_result": persistence_gate_result,
        "external_memory_db_write_result": db_write_result,
        "persisted": bool(db_write_result),
    }


def run_market_analyzer_external_memory_path(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    """
    Compatibility wrapper.

    Lawful use now requires a sealed child_core_result dict.
    Runtime-ingress usage is prohibited.
    """
    if args and isinstance(args[0], dict):
        return run_market_analyzer_external_memory_admission(args[0])

    child_core_result = kwargs.get("child_core_result")
    if isinstance(child_core_result, dict):
        return run_market_analyzer_external_memory_admission(child_core_result)

    raise ExternalMemoryAdmissionRuntimeError(
        "run_market_analyzer_external_memory_path now requires a sealed child_core_result dict. "
        "Live runtime ingress usage is prohibited."
    )