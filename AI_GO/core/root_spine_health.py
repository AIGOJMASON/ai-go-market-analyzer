from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import Any

from AI_GO.core.smi.system_smi import load_latest_system_smi_record


ROOT_SPINE_HEALTH_VERSION = "v1.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _import_status(module_name: str, required_attrs: list[str] | None = None) -> dict[str, Any]:
    required_attrs = required_attrs or []

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        return {
            "module": module_name,
            "available": False,
            "status": "missing",
            "error": f"{type(exc).__name__}: {exc}",
            "required_attrs": required_attrs,
            "missing_attrs": required_attrs,
        }

    missing_attrs = [
        attr for attr in required_attrs if not hasattr(module, attr)
    ]

    return {
        "module": module_name,
        "available": not missing_attrs,
        "status": "ok" if not missing_attrs else "partial",
        "error": "",
        "required_attrs": required_attrs,
        "missing_attrs": missing_attrs,
    }


def _route_present(app: Any, path: str, method: str = "GET") -> bool:
    method_upper = method.upper()

    for route in getattr(app, "routes", []):
        route_path = getattr(route, "path", "")
        route_methods = getattr(route, "methods", set()) or set()

        if route_path == path and method_upper in route_methods:
            return True

    return False


def build_root_spine_component_index() -> dict[str, Any]:
    latest_smi = load_latest_system_smi_record()

    components = {
        "research_core": _import_status(
            "AI_GO.core.research.live_research_gateway",
            ["build_live_research_packet"],
        ),
        "provider_spine_runner": _import_status(
            "AI_GO.core.research.provider_spine_runner",
            [
                "run_alpha_quote_through_root_spine",
                "run_marketaux_news_through_root_spine",
            ],
        ),
        "engines": _import_status(
            "AI_GO.engines.curated_child_core_handoff_engine",
            ["curate_research_packet_for_child_cores"],
        ),
        "child_core_consumption_adapter": _import_status(
            "AI_GO.core.child_core_handoff.consumption_adapter",
            ["build_child_core_consumption_packet"],
        ),
        "market_analyzer_adapter": _import_status(
            "AI_GO.child_cores.market_analyzer_v1.adapters.root_handoff_adapter",
            ["build_market_analyzer_input_from_root_handoff"],
        ),
        "contractor_builder_adapter": _import_status(
            "AI_GO.child_cores.contractor_builder_v1.adapters.root_handoff_adapter",
            ["build_contractor_builder_input_from_root_handoff"],
        ),
        "system_smi": _import_status(
            "AI_GO.core.smi.system_smi",
            [
                "build_system_smi_record",
                "persist_system_smi_record",
                "load_latest_system_smi_record",
            ],
        ),
        "external_memory_runtime": _import_status(
            "AI_GO.EXTERNAL_MEMORY.runtime.external_memory_runtime_bridge",
            ["run_external_memory_runtime_path"],
        ),
        "root_intelligence_spine": _import_status(
            "AI_GO.core.root_intelligence_spine",
            ["run_root_intelligence_spine"],
        ),
    }

    required_keys = [
        "research_core",
        "engines",
        "child_core_consumption_adapter",
        "market_analyzer_adapter",
        "contractor_builder_adapter",
        "system_smi",
        "root_intelligence_spine",
    ]

    required_ok = all(
        components[key]["available"] is True
        for key in required_keys
    )

    return {
        "artifact_type": "root_spine_component_index",
        "artifact_version": ROOT_SPINE_HEALTH_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "read_only",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_fetch_provider": False,
            "can_write_external_memory": False,
            "can_override_governance": False,
            "can_override_watcher": False,
        },
        "components": components,
        "latest_smi": {
            "available": bool(latest_smi),
            "record_id": latest_smi.get("record_id", "") if isinstance(latest_smi, dict) else "",
            "recorded_at": latest_smi.get("recorded_at", "") if isinstance(latest_smi, dict) else "",
            "event_type": latest_smi.get("event_type", "") if isinstance(latest_smi, dict) else "",
        },
        "required_components_ok": required_ok,
        "summary": {
            "research_core_active": components["research_core"]["available"],
            "engines_active": components["engines"]["available"],
            "child_core_consumption_active": components["child_core_consumption_adapter"]["available"],
            "market_analyzer_adapter_active": components["market_analyzer_adapter"]["available"],
            "contractor_builder_adapter_active": components["contractor_builder_adapter"]["available"],
            "smi_active": components["system_smi"]["available"],
            "external_memory_available": components["external_memory_runtime"]["available"],
            "root_intelligence_spine_active": components["root_intelligence_spine"]["available"],
            "required_components_ok": required_ok,
        },
    }


def build_root_spine_route_index(app: Any) -> dict[str, Any]:
    routes = {
        "market_analyzer_curated_live": {
            "path": "/market-analyzer/run/curated-live",
            "method": "POST",
            "present": _route_present(app, "/market-analyzer/run/curated-live", "POST"),
        },
        "contractor_curated_external_pressure": {
            "path": "/contractor-builder/external-pressure/curated",
            "method": "POST",
            "present": _route_present(app, "/contractor-builder/external-pressure/curated", "POST"),
        },
        "contractor_root_spine_health": {
            "path": "/contractor-builder/root-spine/health",
            "method": "GET",
            "present": _route_present(app, "/contractor-builder/root-spine/health", "GET"),
        },
        "contractor_root_spine_index": {
            "path": "/contractor-builder/root-spine/index",
            "method": "GET",
            "present": _route_present(app, "/contractor-builder/root-spine/index", "GET"),
        },
    }

    return {
        "artifact_type": "root_spine_route_index",
        "artifact_version": ROOT_SPINE_HEALTH_VERSION,
        "generated_at": _utc_now_iso(),
        "mode": "read_only",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_override_routes": False,
        },
        "routes": routes,
        "summary": {
            "market_analyzer_curated_live_present": routes["market_analyzer_curated_live"]["present"],
            "contractor_curated_external_pressure_present": routes["contractor_curated_external_pressure"]["present"],
            "health_present": routes["contractor_root_spine_health"]["present"],
            "index_present": routes["contractor_root_spine_index"]["present"],
            "all_required_routes_present": all(item["present"] for item in routes.values()),
        },
    }


def build_root_spine_health_packet(app: Any | None = None) -> dict[str, Any]:
    component_index = build_root_spine_component_index()
    route_index = build_root_spine_route_index(app) if app is not None else {}

    route_summary = route_index.get("summary", {}) if isinstance(route_index, dict) else {}

    healthy = bool(component_index["summary"]["required_components_ok"])
    if route_summary:
        healthy = healthy and bool(route_summary.get("all_required_routes_present"))

    return {
        "artifact_type": "root_spine_health_packet",
        "artifact_version": ROOT_SPINE_HEALTH_VERSION,
        "generated_at": _utc_now_iso(),
        "phase": "Phase 5A.5",
        "status": "ok" if healthy else "degraded",
        "mode": "read_only",
        "authority": {
            "read_only": True,
            "advisory_only": True,
            "can_execute": False,
            "can_mutate_state": False,
            "can_fetch_provider": False,
            "can_write_external_memory": False,
            "can_override_governance": False,
            "can_override_watcher": False,
        },
        "component_index": component_index,
        "route_index": route_index,
        "summary": {
            "healthy": healthy,
            "required_components_ok": component_index["summary"]["required_components_ok"],
            "all_required_routes_present": route_summary.get("all_required_routes_present"),
            "research_core_active": component_index["summary"]["research_core_active"],
            "engines_active": component_index["summary"]["engines_active"],
            "smi_active": component_index["summary"]["smi_active"],
            "external_memory_available": component_index["summary"]["external_memory_available"],
            "market_analyzer_curated_live_present": route_summary.get(
                "market_analyzer_curated_live_present"
            ),
            "contractor_curated_external_pressure_present": route_summary.get(
                "contractor_curated_external_pressure_present"
            ),
        },
    }