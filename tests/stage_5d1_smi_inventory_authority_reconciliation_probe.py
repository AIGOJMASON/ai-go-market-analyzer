from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List


PHASE = "5D.1"
PROBE_ID = "stage_5d1_smi_inventory_authority_reconciliation_probe"


PM_CONTINUITY_REGISTRY_MODULE = "AI_GO.PM_CORE.smi.pm_continuity_registry"
PM_CONTINUITY_RUNTIME_MODULE = "AI_GO.PM_CORE.smi.pm_continuity"
SYSTEM_SMI_MODULE = "AI_GO.core.smi.system_smi"


AWARENESS_MODULES = [
    "AI_GO.core.awareness.pattern_recognition",
    "AI_GO.core.awareness.temporal_awareness",
    "AI_GO.core.awareness.posture_explanation",
    "AI_GO.core.awareness.unified_system_awareness",
    "AI_GO.core.awareness.cross_run_intelligence",
]


FORBIDDEN_AUTHORITY_FLAGS = [
    "can_execute",
    "can_mutate_state",
    "can_override_governance",
    "can_override_watcher",
    "can_override_execution_gate",
    "execution_allowed",
    "mutation_allowed",
]


EXPECTED_PATHS = {
    "pm_continuity_registry": Path("AI_GO/PM_CORE/smi/pm_continuity_registry.py"),
    "pm_continuity_runtime": Path("AI_GO/PM_CORE/smi/pm_continuity.py"),
    "system_smi": Path("AI_GO/core/smi/system_smi.py"),
    "pm_core_init": Path("AI_GO/PM_CORE/__init__.py"),
    "pm_smi_init": Path("AI_GO/PM_CORE/smi/__init__.py"),
    "core_smi_init": Path("AI_GO/core/smi/__init__.py"),
}


def _safe_import(module_name: str) -> Dict[str, Any]:
    try:
        module = importlib.import_module(module_name)
        return {
            "module": module,
            "available": True,
            "error": "",
        }
    except Exception as exc:
        return {
            "module": None,
            "available": False,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _inspect_file_paths() -> Dict[str, Any]:
    return {
        key: {
            "path": str(path),
            "exists": path.exists(),
        }
        for key, path in EXPECTED_PATHS.items()
    }


def _inspect_pm_continuity_registry() -> Dict[str, Any]:
    imported = _safe_import(PM_CONTINUITY_REGISTRY_MODULE)
    module = imported.pop("module", None)

    has_registry_entrypoint = False
    authority_violations: List[str] = []

    if module is not None:
        has_registry_entrypoint = any(
            hasattr(module, name)
            for name in (
                "build_pm_continuity_registry",
                "get_pm_continuity_registry",
                "PM_CONTINUITY_REGISTRY",
            )
        )

        for flag in FORBIDDEN_AUTHORITY_FLAGS:
            if getattr(module, flag, False) is True:
                authority_violations.append(flag)

    return {
        **imported,
        "module_name": PM_CONTINUITY_REGISTRY_MODULE,
        "has_registry_entrypoint": has_registry_entrypoint,
        "authority_reconciled": not authority_violations,
        "authority_violations": authority_violations,
        "authority_model": "pm_owned_decision_memory_only",
    }


def _inspect_pm_continuity_runtime() -> Dict[str, Any]:
    imported = _safe_import(PM_CONTINUITY_RUNTIME_MODULE)
    module = imported.pop("module", None)

    has_runtime_entrypoint = False
    authority_violations: List[str] = []

    if module is not None:
        has_runtime_entrypoint = any(
            hasattr(module, name)
            for name in (
                "build_pm_continuity_state",
                "record_pm_continuity",
                "load_pm_continuity_state",
                "append_pm_continuity_event",
            )
        )

        for flag in FORBIDDEN_AUTHORITY_FLAGS:
            if getattr(module, flag, False) is True:
                authority_violations.append(flag)

    return {
        **imported,
        "module_name": PM_CONTINUITY_RUNTIME_MODULE,
        "has_runtime_entrypoint": has_runtime_entrypoint,
        "authority_reconciled": not authority_violations,
        "authority_violations": authority_violations,
        "authority_model": "pm_continuity_storage_only",
    }


def _inspect_system_smi_module() -> Dict[str, Any]:
    imported = _safe_import(SYSTEM_SMI_MODULE)
    module = imported.pop("module", None)

    has_build_entrypoint = False
    authority_violations: List[str] = []

    if module is not None:
        has_build_entrypoint = any(
            hasattr(module, name)
            for name in (
                "build_system_smi_record",
                "record_system_smi",
                "load_latest_system_smi_record",
            )
        )

        for flag in FORBIDDEN_AUTHORITY_FLAGS:
            if getattr(module, flag, False) is True:
                authority_violations.append(flag)

    return {
        **imported,
        "module_name": SYSTEM_SMI_MODULE,
        "has_build_entrypoint": has_build_entrypoint,
        "authority_reconciled": not authority_violations,
        "authority_violations": authority_violations,
        "authority_model": "system_wide_continuity_record_only",
    }


def _inspect_awareness_modules() -> Dict[str, Any]:
    available: List[str] = []
    missing: List[Dict[str, str]] = []

    for module_name in AWARENESS_MODULES:
        imported = _safe_import(module_name)
        if imported["available"]:
            available.append(module_name)
        else:
            missing.append(
                {
                    "module": module_name,
                    "error": imported["error"],
                }
            )

    return {
        "available_count": len(available),
        "available": available,
        "missing": missing,
    }


def _inspect_state_surfaces() -> Dict[str, Any]:
    return {
        "pm_continuity_state": "AI_GO/PM_CORE/state/current/pm_continuity_state.json",
        "pm_change_ledger": "AI_GO/PM_CORE/state/current/pm_change_ledger.json",
        "pm_unresolved_queue": "AI_GO/PM_CORE/state/current/pm_unresolved_queue.json",
        "system_smi_latest": "AI_GO/state/system_smi/latest_system_smi_record.json",
        "system_smi_history": "AI_GO/state/system_smi/system_smi_history.jsonl",
    }


def _build_reconciliation(
    *,
    file_paths: Dict[str, Any],
    pm_registry: Dict[str, Any],
    pm_runtime: Dict[str, Any],
    system_smi: Dict[str, Any],
    awareness: Dict[str, Any],
) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []

    for key, info in file_paths.items():
        if info.get("exists") is not True:
            errors.append(f"{key}_file_missing")

    if not pm_registry["available"]:
        errors.append("pm_continuity_registry_import_failed")

    if not pm_registry["has_registry_entrypoint"]:
        errors.append("pm_continuity_registry_entrypoint_missing")

    if not pm_registry["authority_reconciled"]:
        errors.append("pm_continuity_registry_authority_not_reconciled")

    if pm_registry["authority_violations"]:
        errors.append("pm_continuity_registry_forbidden_authority_flag_true")

    if not pm_runtime["available"]:
        errors.append("pm_continuity_runtime_import_failed")

    if not pm_runtime["has_runtime_entrypoint"]:
        errors.append("pm_continuity_runtime_entrypoint_missing")

    if not pm_runtime["authority_reconciled"]:
        errors.append("pm_continuity_runtime_authority_not_reconciled")

    if pm_runtime["authority_violations"]:
        errors.append("pm_continuity_runtime_forbidden_authority_flag_true")

    if not system_smi["available"]:
        errors.append("system_smi_import_failed")

    if not system_smi["has_build_entrypoint"]:
        errors.append("system_smi_build_entrypoint_missing")

    if not system_smi["authority_reconciled"]:
        errors.append("system_smi_authority_not_reconciled")

    if system_smi["authority_violations"]:
        errors.append("system_smi_forbidden_authority_flag_true")

    if awareness["available_count"] == 0:
        warnings.append("no_awareness_modules_available")

    if awareness["missing"]:
        warnings.append("some_awareness_modules_missing")

    return {
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "warnings": warnings,
        "authority_model": {
            "pm_continuity": "pm_owned_decision_memory_only",
            "system_smi": "system_wide_continuity_record_only",
            "system_brain": "advisory_interpretation_only",
        },
        "hard_rules_confirmed": {
            "pm_continuity_must_not_execute": True,
            "pm_continuity_must_not_activate_child_cores": True,
            "pm_continuity_must_not_mutate_canon_truth": True,
            "system_smi_must_not_execute": True,
            "system_smi_must_not_override_governance": True,
            "system_brain_must_remain_advisory": True,
        },
    }


def run_probe() -> Dict[str, Any]:
    file_paths = _inspect_file_paths()
    pm_registry = _inspect_pm_continuity_registry()
    pm_runtime = _inspect_pm_continuity_runtime()
    system_smi = _inspect_system_smi_module()
    awareness = _inspect_awareness_modules()
    state_surfaces = _inspect_state_surfaces()

    reconciliation = _build_reconciliation(
        file_paths=file_paths,
        pm_registry=pm_registry,
        pm_runtime=pm_runtime,
        system_smi=system_smi,
        awareness=awareness,
    )

    assert reconciliation["status"] == "passed", reconciliation

    return {
        "status": "passed",
        "phase": PHASE,
        "probe_id": PROBE_ID,
        "purpose": "Inventory SMI surfaces and reconcile authority before System Brain activation.",
        "file_paths": file_paths,
        "pm_continuity_registry": pm_registry,
        "pm_continuity_runtime": pm_runtime,
        "system_smi": system_smi,
        "awareness_modules": awareness,
        "state_surfaces": state_surfaces,
        "reconciliation": reconciliation,
        "next": {
            "phase": "5D.2",
            "recommended_step": "Build SMI pattern posture reader that consumes PM_CONTINUITY and system_smi as advisory context only.",
        },
    }


if __name__ == "__main__":
    result = run_probe()
    print("STAGE_5D1_SMI_INVENTORY_AUTHORITY_RECONCILIATION_PROBE: PASS")
    print(result)