from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[2]
PM_CORE_DIR = ROOT / "PM_CORE"
CHILD_CORES_DIR = ROOT / "child_cores"

AUTHORITATIVE_REGISTRY_PATH = PM_CORE_DIR / "state" / "child_core_registry.json"
MIRROR_REGISTRY_PATH = CHILD_CORES_DIR / "child_core_registry.json"

VALID_LIFECYCLE_STATES = {"draft", "active", "retired"}

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

REQUIRED_FILES = [
    "CORE_IDENTITY.md",
    "INHERITANCE_CONTRACT.md",
    "RESEARCH_INTERFACE.md",
    "SMI_INTERFACE.md",
    "WATCHER_INTERFACE.md",
    "OUTPUT_POLICY.md",
    "DOMAIN_POLICY.md",
    "DOMAIN_REGISTRY.json",
    "execution/ingress_processor.py",
    "outputs/output_builder.py",
    "watcher/core_watcher.py",
    "smi/core_smi.py",
    "research/research_interface.py",
    "domains/_DOMAIN_LAYER.md",
]

REQUIRED_DOMAIN_REGISTRY_KEYS = [
    "core_id",
    "display_name",
    "domain_focus",
    "allowed_actions",
    "forbidden_actions",
    "research_themes",
    "status",
]


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "details": self.details,
        }


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if not path.exists():
        return deepcopy(default) if default is not None else {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _default_registry() -> Dict[str, Any]:
    return {
        "registry_id": "AI_GO_CHILD_CORE_REGISTRY",
        "authority": "PM_CORE",
        "version": "1.0",
        "entries": {},
    }


def _default_mirror_registry() -> Dict[str, Any]:
    return {
        "registry_id": "AI_GO_CHILD_CORE_MIRROR",
        "authority": "child_cores_layer",
        "mirrors_authoritative_registry": str(AUTHORITATIVE_REGISTRY_PATH.as_posix()),
        "version": "1.0",
        "entries": {},
    }


def load_registry() -> Dict[str, Any]:
    registry = _read_json(AUTHORITATIVE_REGISTRY_PATH, default=_default_registry())
    registry.setdefault("entries", {})
    return registry


def save_registry(registry: Dict[str, Any]) -> None:
    _write_json(AUTHORITATIVE_REGISTRY_PATH, registry)


def load_mirror_registry() -> Dict[str, Any]:
    mirror = _read_json(MIRROR_REGISTRY_PATH, default=_default_mirror_registry())
    mirror.setdefault("entries", {})
    return mirror


def save_mirror_registry(mirror: Dict[str, Any]) -> None:
    _write_json(MIRROR_REGISTRY_PATH, mirror)


def sync_mirror_registry() -> Dict[str, Any]:
    authoritative = load_registry()
    mirror = _default_mirror_registry()
    for core_id, entry in authoritative.get("entries", {}).items():
        mirror["entries"][core_id] = {
            "core_id": core_id,
            "status": entry.get("status"),
            "domain_focus": entry.get("domain_focus"),
            "core_path": entry.get("core_path"),
            "template_version": entry.get("template_version"),
            "authoritative_registry_path": str(AUTHORITATIVE_REGISTRY_PATH.as_posix()),
        }
    save_mirror_registry(mirror)
    return mirror


def get_entry(core_id: str) -> Optional[Dict[str, Any]]:
    registry = load_registry()
    return registry.get("entries", {}).get(core_id)


def is_registered(core_id: str) -> bool:
    return get_entry(core_id) is not None


def get_active_cores() -> Dict[str, Dict[str, Any]]:
    registry = load_registry()
    return {
        core_id: entry
        for core_id, entry in registry.get("entries", {}).items()
        if entry.get("status") == "active"
    }


def resolve_active_core(core_id: str) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")
    if entry.get("status") != "active":
        raise ValueError(f"Child core '{core_id}' is not active.")
    validation = validate_registered_core(core_id)
    if not validation.ok:
        raise ValueError(
            f"Child core '{core_id}' failed validation and cannot be resolved as active: "
            + "; ".join(validation.errors)
        )
    return entry


def _core_root(core_id: str) -> Path:
    return CHILD_CORES_DIR / core_id


def _domain_registry_path(core_root: Path) -> Path:
    return core_root / "DOMAIN_REGISTRY.json"


def validate_lifecycle_state(state: str) -> bool:
    return state in VALID_LIFECYCLE_STATES


def validate_structural(core_id: str) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {
        "missing_directories": [],
        "missing_files": [],
        "json_parse_errors": [],
    }

    core_root = _core_root(core_id)
    if not core_root.exists():
        errors.append(f"Core directory does not exist: {core_root.as_posix()}")
        return ValidationResult(False, errors, warnings, details)

    for directory in REQUIRED_DIRECTORIES:
        path = core_root / directory
        if not path.exists() or not path.is_dir():
            details["missing_directories"].append(directory)

    for filename in REQUIRED_FILES:
        path = core_root / filename
        if not path.exists() or not path.is_file():
            details["missing_files"].append(filename)

    domain_registry = _domain_registry_path(core_root)
    if domain_registry.exists():
        try:
            _read_json(domain_registry)
        except Exception as exc:
            details["json_parse_errors"].append(
                f"DOMAIN_REGISTRY.json parse failure: {exc}"
            )

    if details["missing_directories"]:
        errors.append("Missing required directories.")
    if details["missing_files"]:
        errors.append("Missing required files.")
    if details["json_parse_errors"]:
        errors.append("JSON parsing failed for one or more required files.")

    return ValidationResult(len(errors) == 0, errors, warnings, details)


def _semantic_duplicate_domain_focus(core_id: str, domain_focus: str) -> Optional[str]:
    for existing_core_id, entry in get_active_cores().items():
        if existing_core_id == core_id:
            continue
        if entry.get("domain_focus") == domain_focus:
            return existing_core_id
    return None


def validate_semantic(core_id: str) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    details: Dict[str, Any] = {
        "domain_registry_checks": {},
    }

    entry = get_entry(core_id)
    if entry is None:
        errors.append(f"Core '{core_id}' is not present in authoritative registry.")
        return ValidationResult(False, errors, warnings, details)

    core_root = _core_root(core_id)
    domain_registry_path = _domain_registry_path(core_root)
    if not domain_registry_path.exists():
        errors.append("DOMAIN_REGISTRY.json missing; semantic validation cannot proceed.")
        return ValidationResult(False, errors, warnings, details)

    try:
        domain_registry = _read_json(domain_registry_path)
    except Exception as exc:
        errors.append(f"Unable to read DOMAIN_REGISTRY.json: {exc}")
        return ValidationResult(False, errors, warnings, details)

    missing_keys = [key for key in REQUIRED_DOMAIN_REGISTRY_KEYS if key not in domain_registry]
    if missing_keys:
        errors.append(f"DOMAIN_REGISTRY.json missing required keys: {missing_keys}")
    details["domain_registry_checks"]["missing_keys"] = missing_keys

    registry_core_id = domain_registry.get("core_id")
    if registry_core_id != core_id:
        errors.append(
            f"DOMAIN_REGISTRY core_id mismatch. Expected '{core_id}', got '{registry_core_id}'."
        )

    entry_domain_focus = entry.get("domain_focus")
    domain_focus = domain_registry.get("domain_focus")
    if not domain_focus:
        errors.append("DOMAIN_REGISTRY domain_focus is empty.")
    elif entry_domain_focus != domain_focus:
        errors.append(
            f"Registry domain_focus mismatch. Registry='{entry_domain_focus}', "
            f"DOMAIN_REGISTRY='{domain_focus}'."
        )

    allowed_actions = domain_registry.get("allowed_actions", [])
    forbidden_actions = domain_registry.get("forbidden_actions", [])
    research_themes = domain_registry.get("research_themes", [])

    if not isinstance(allowed_actions, list) or not allowed_actions:
        errors.append("DOMAIN_REGISTRY allowed_actions must be a non-empty list.")
    if not isinstance(forbidden_actions, list) or not forbidden_actions:
        errors.append("DOMAIN_REGISTRY forbidden_actions must be a non-empty list.")
    if not isinstance(research_themes, list):
        errors.append("DOMAIN_REGISTRY research_themes must be a list.")

    duplicate = _semantic_duplicate_domain_focus(core_id, domain_focus)
    if duplicate is not None and entry.get("status") == "draft":
        errors.append(
            f"Domain focus collision with active child core '{duplicate}'. "
            "Duplicate active domain focus is not allowed."
        )

    status = entry.get("status")
    if not validate_lifecycle_state(status):
        errors.append(f"Invalid lifecycle state in registry: '{status}'")

    details["domain_registry_checks"]["core_id"] = registry_core_id
    details["domain_registry_checks"]["domain_focus"] = domain_focus
    details["domain_registry_checks"]["allowed_actions_count"] = len(allowed_actions) if isinstance(allowed_actions, list) else 0
    details["domain_registry_checks"]["forbidden_actions_count"] = len(forbidden_actions) if isinstance(forbidden_actions, list) else 0
    details["domain_registry_checks"]["research_themes_count"] = len(research_themes) if isinstance(research_themes, list) else 0

    return ValidationResult(len(errors) == 0, errors, warnings, details)


def validate_registered_core(core_id: str) -> ValidationResult:
    structural = validate_structural(core_id)
    semantic = validate_semantic(core_id)

    errors = structural.errors + semantic.errors
    warnings = structural.warnings + semantic.warnings
    details = {
        "structural": structural.to_dict(),
        "semantic": semantic.to_dict(),
    }
    return ValidationResult(len(errors) == 0, errors, warnings, details)


def register_core_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    core_id = entry["core_id"]
    registry = load_registry()
    if core_id in registry["entries"]:
        raise ValueError(f"Child core '{core_id}' is already registered.")

    status = entry.get("status", "draft")
    if not validate_lifecycle_state(status):
        raise ValueError(f"Invalid lifecycle state: '{status}'")

    registry["entries"][core_id] = entry
    save_registry(registry)
    sync_mirror_registry()
    return entry


def update_core_entry(core_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    registry = load_registry()
    if core_id not in registry["entries"]:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    registry["entries"][core_id].update(updates)
    save_registry(registry)
    sync_mirror_registry()
    return registry["entries"][core_id]


def activate_core(core_id: str, activation_receipt_path: str) -> Dict[str, Any]:
    validation = validate_registered_core(core_id)
    if not validation.ok:
        raise ValueError(
            f"Child core '{core_id}' failed validation and cannot be activated: "
            + "; ".join(validation.errors)
        )

    updated = update_core_entry(
        core_id,
        {
            "status": "active",
            "required_files_verified": True,
            "structural_validation": validation.details["structural"],
            "semantic_validation": validation.details["semantic"],
            "activation_receipt_path": activation_receipt_path,
        },
    )
    return updated


def retire_core(core_id: str, retirement_receipt_path: str, notes: Optional[str] = None) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    updated = update_core_entry(
        core_id,
        {
            "status": "retired",
            "retirement_receipt_path": retirement_receipt_path,
            "notes": notes or entry.get("notes"),
        },
    )
    return updated


def list_registered_cores() -> Dict[str, Dict[str, Any]]:
    return load_registry().get("entries", {})


def ensure_registry_files_exist() -> None:
    if not AUTHORITATIVE_REGISTRY_PATH.exists():
        save_registry(_default_registry())
    if not MIRROR_REGISTRY_PATH.exists():
        save_mirror_registry(_default_mirror_registry())
    sync_mirror_registry()