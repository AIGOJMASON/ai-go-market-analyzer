from __future__ import annotations

import json
from pathlib import Path


ROOT = Path("AI_GO")
CORE_ROOT = ROOT / "child_cores" / "market_analyzer_v1"

REQUIRED_FILES = [
    "CORE_IDENTITY.md",
    "INHERITANCE_CONTRACT.md",
    "RESEARCH_INTERFACE.md",
    "SMI_INTERFACE.md",
    "WATCHER_INTERFACE.md",
    "OUTPUT_POLICY.md",
    "DOMAIN_POLICY.md",
    "DOMAIN_REGISTRY.json",
    "domains/_DOMAIN_LAYER.md",
    "execution/ingress_processor.py",
    "execution/refinement_conditioning.py",
    "execution/market_regime_classifier.py",
    "execution/event_propagation_classifier.py",
    "execution/necessity_filter.py",
    "execution/rebound_validator.py",
    "execution/recommendation_builder.py",
    "execution/run.py",
    "outputs/output_builder.py",
    "outputs/market_regime_view.py",
    "outputs/active_event_view.py",
    "outputs/watchlist_view.py",
    "outputs/trade_recommendation_view.py",
    "outputs/receipt_trace_view.py",
    "outputs/approval_request_view.py",
    "watcher/core_watcher.py",
    "smi/core_smi.py",
    "research/research_interface.py",
    "constraints/constraints.json",
]

REQUIRED_DIRECTORIES = [
    "inheritance_state",
    "execution",
    "outputs",
    "watcher",
    "smi",
    "research",
    "state/current",
    "constraints",
    "domains",
]

REQUIRED_REGISTRY_FIELDS = [
    "core_id",
    "display_name",
    "domain_focus",
    "status",
    "template_version",
    "created_at",
    "updated_at",
    "core_path",
    "domain_registry_path",
    "required_files_verified",
    "structural_validation",
    "semantic_validation",
    "activation_receipt_path",
    "retirement_receipt_path",
    "notes",
]


def _result(case: str, status: str, detail: str | None = None) -> dict:
    row = {"case": case, "status": status}
    if detail:
        row["detail"] = detail
    return row


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _find_registry_entry(registry_path: Path, core_id: str) -> dict | None:
    data = _load_json(registry_path)
    for entry in data.get("cores", []):
        if entry.get("core_id") == core_id:
            return entry
    return None


def main() -> dict:
    results = []

    for rel_path in REQUIRED_FILES:
        path = CORE_ROOT / rel_path
        results.append(
            _result(
                f"file_exists::{rel_path}",
                "passed" if path.exists() else "failed",
                None if path.exists() else f"missing file: {path}",
            )
        )

    for rel_path in REQUIRED_DIRECTORIES:
        path = CORE_ROOT / rel_path
        ok = path.exists() and path.is_dir()
        results.append(
            _result(
                f"directory_exists::{rel_path}",
                "passed" if ok else "failed",
                None if ok else f"missing directory: {path}",
            )
        )

    domain_registry_path = CORE_ROOT / "DOMAIN_REGISTRY.json"
    try:
        domain_registry = _load_json(domain_registry_path)
        results.append(_result("domain_registry_json_parses", "passed"))
    except Exception as exc:
        domain_registry = {}
        results.append(_result("domain_registry_json_parses", "failed", str(exc)))

    constraints_path = CORE_ROOT / "constraints" / "constraints.json"
    try:
        _load_json(constraints_path)
        results.append(_result("constraints_json_parses", "passed"))
    except Exception as exc:
        results.append(_result("constraints_json_parses", "failed", str(exc)))

    mirror_registry_path = ROOT / "child_cores" / "child_core_registry.json"
    pm_registry_path = ROOT / "PM_CORE" / "state" / "child_core_registry.json"

    mirror_entry = None
    pm_entry = None

    try:
        mirror_entry = _find_registry_entry(mirror_registry_path, "market_analyzer_v1")
        results.append(
            _result(
                "mirror_registry_entry_present",
                "passed" if mirror_entry else "failed",
                None if mirror_entry else "market_analyzer_v1 missing from mirror registry",
            )
        )
    except Exception as exc:
        results.append(_result("mirror_registry_entry_present", "failed", str(exc)))

    try:
        pm_entry = _find_registry_entry(pm_registry_path, "market_analyzer_v1")
        results.append(
            _result(
                "pm_registry_entry_present",
                "passed" if pm_entry else "failed",
                None if pm_entry else "market_analyzer_v1 missing from PM registry",
            )
        )
    except Exception as exc:
        results.append(_result("pm_registry_entry_present", "failed", str(exc)))

    for registry_name, entry in [("mirror", mirror_entry), ("pm", pm_entry)]:
        if isinstance(entry, dict):
            missing = [field for field in REQUIRED_REGISTRY_FIELDS if field not in entry]
            results.append(
                _result(
                    f"{registry_name}_registry_required_fields",
                    "passed" if not missing else "failed",
                    None if not missing else f"missing fields: {missing}",
                )
            )
        else:
            results.append(
                _result(
                    f"{registry_name}_registry_required_fields",
                    "failed",
                    "registry entry unavailable",
                )
            )

    if isinstance(domain_registry, dict):
        required_domain_keys = [
            "core_id",
            "display_name",
            "domain_focus",
            "template_version",
            "allowed_actions",
            "forbidden_actions",
            "required_artifacts",
            "approval_gate",
        ]
        missing = [key for key in required_domain_keys if key not in domain_registry]
        results.append(
            _result(
                "domain_registry_required_keys",
                "passed" if not missing else "failed",
                None if not missing else f"missing keys: {missing}",
            )
        )

    failed = sum(1 for item in results if item["status"] == "failed")
    passed = sum(1 for item in results if item["status"] == "passed")

    return {"passed": passed, "failed": failed, "results": results}


if __name__ == "__main__":
    print(main())