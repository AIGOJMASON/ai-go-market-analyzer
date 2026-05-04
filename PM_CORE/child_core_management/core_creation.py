from __future__ import annotations

import inspect
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from AI_GO.core.governance.governed_persistence import governed_write_json

from .child_core_registry import (
    CHILD_CORES_DIR,
    PM_CORE_DIR,
    REQUIRED_DIRECTORIES,
    REQUIRED_FILES,
    activate_core,
    ensure_registry_files_exist,
    get_entry,
    register_core_entry,
    update_core_entry,
    validate_registered_core,
)


TEMPLATE_VERSION = "northstar_child_core_template_v1"
RECEIPTS_DIR = PM_CORE_DIR / "state" / "receipts"

MUTATION_CLASS = "project_creation"
RECEIPT_MUTATION_CLASS = "receipt"

AUTHORITY_METADATA: Dict[str, Any] = {
    "advisory_only": False,
    "can_execute": False,
    "can_activate_child_core_without_governance": False,
    "can_mutate_workflow_state": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "pm_child_core_creation_only",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slugify(value: str) -> str:
    lowered = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    parts = [part for part in lowered.split("_") if part]
    return "_".join(parts)


def _core_id_from_domain(domain_focus: str) -> str:
    base = _slugify(domain_focus)
    if not base:
        raise ValueError("domain_focus is required")
    if not base.endswith("_core"):
        base = f"{base}_core"
    return base


def _core_path(core_id: str) -> Path:
    return CHILD_CORES_DIR / core_id


def _normalize_payload(
    payload: Dict[str, Any],
    *,
    persistence_type: str,
    mutation_class: str,
    advisory_only: bool,
) -> Dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_version", TEMPLATE_VERSION)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = mutation_class
    normalized["advisory_only"] = advisory_only
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["approval_required"] = True
    return normalized


def _governed_write(
    path: Path,
    payload: Dict[str, Any],
    *,
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
    advisory_only: bool = False,
) -> str:
    normalized = _normalize_payload(
        payload,
        persistence_type=persistence_type,
        mutation_class=mutation_class,
        advisory_only=advisory_only,
    )

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": advisory_only,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {key: value for key, value in kwargs.items() if key in signature.parameters}

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in signature.parameters.values()):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def _write_text(path: Path, content: str) -> str:
    return _governed_write(
        path,
        {
            "artifact_type": "pm_child_core_seed_text",
            "path": str(path),
            "content": content.rstrip() + "\n",
            "created_at": _utc_now(),
        },
        persistence_type="pm_child_core_seed_text",
        mutation_class=MUTATION_CLASS,
        advisory_only=False,
    )


def _write_json(path: Path, payload: Dict[str, Any]) -> str:
    return _governed_write(
        path,
        payload,
        persistence_type=str(payload.get("persistence_type") or "pm_child_core_creation_artifact"),
        mutation_class=MUTATION_CLASS,
        advisory_only=False,
    )


def _seed_core_identity(core_id: str, display_name: str, domain_focus: str) -> str:
    return f"""# {display_name}

## What it is

Bounded child core for the domain focus: {domain_focus}.

## Authority Position

This child core may receive bounded inheritance packets from PM_CORE.

It may not ingest direct research, bypass PM_CORE inheritance, redefine system truth, or self-activate outside registry lifecycle rules.

## Core Identity

- core_id: {core_id}
- display_name: {display_name}
- domain_focus: {domain_focus}
- template_version: {TEMPLATE_VERSION}
"""


def _seed_inheritance_contract(core_id: str) -> str:
    return f"""# INHERITANCE CONTRACT

## What it is

Governed ingress contract for {core_id}.

## Boundary

All inherited authority must arrive through PM_CORE. This file does not grant execution.
"""


def _seed_json_artifact(core_id: str, artifact_type: str) -> Dict[str, Any]:
    return {
        "artifact_type": artifact_type,
        "artifact_version": TEMPLATE_VERSION,
        "core_id": core_id,
        "created_at": _utc_now(),
        "status": "seeded",
        "persistence_type": artifact_type,
        "mutation_class": MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }


def _seed_core_structure(core_id: str, display_name: str, domain_focus: str) -> Dict[str, Any]:
    core_path = _core_path(core_id)
    created_paths: list[str] = []

    for directory in REQUIRED_DIRECTORIES:
        target = core_path / directory
        target.mkdir(parents=True, exist_ok=True)
        created_paths.append(str(target))

    text_files = {
        "CORE_IDENTITY.md": _seed_core_identity(core_id, display_name, domain_focus),
        "INHERITANCE_CONTRACT.md": _seed_inheritance_contract(core_id),
    }

    for filename, content in text_files.items():
        created_paths.append(_write_text(core_path / filename, content))

    for filename in REQUIRED_FILES:
        target = core_path / filename
        if target.name not in text_files and not target.exists():
            created_paths.append(_write_text(target, f"# {filename}\n\nSeeded by PM_CORE child-core creation.\n"))

    for directory in REQUIRED_DIRECTORIES:
        created_paths.append(
            _write_json(
                core_path / directory / "__init__.json",
                _seed_json_artifact(core_id, f"pm_child_core_seed_{directory}"),
            )
        )

    return {
        "core_path": str(core_path),
        "created_paths": created_paths,
    }


def _creation_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__creation_receipt.json"


def _activation_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__activation_receipt.json"


def create_child_core(
    *,
    domain_focus: str,
    display_name: Optional[str] = None,
    core_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_registry_files_exist()

    clean_core_id = _slugify(core_id) if core_id else _core_id_from_domain(domain_focus)
    clean_display_name = str(display_name or clean_core_id.replace("_", " ").title()).strip()
    clean_domain_focus = str(domain_focus or "").strip()

    if get_entry(clean_core_id) is not None:
        raise ValueError(f"Child core '{clean_core_id}' is already registered.")

    seeded = _seed_core_structure(clean_core_id, clean_display_name, clean_domain_focus)
    validation = validate_registered_core(clean_core_id)

    created_at = _utc_now()
    receipt = {
        "artifact_type": "pm_child_core_creation_receipt",
        "artifact_version": TEMPLATE_VERSION,
        "status": "child_core_created",
        "core_id": clean_core_id,
        "display_name": clean_display_name,
        "domain_focus": clean_domain_focus,
        "created_at": created_at,
        "notes": notes,
        "seeded": seeded,
        "validation": validation,
        "persistence_type": "pm_child_core_creation_receipt",
        "mutation_class": RECEIPT_MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    receipt_path = _creation_receipt_path(clean_core_id)
    written_receipt_path = _governed_write(
        receipt_path,
        receipt,
        persistence_type="pm_child_core_creation_receipt",
        mutation_class=RECEIPT_MUTATION_CLASS,
        advisory_only=False,
    )

    entry = register_core_entry(
        {
            "core_id": clean_core_id,
            "display_name": clean_display_name,
            "domain_focus": clean_domain_focus,
            "core_path": seeded["core_path"],
            "status": "validated",
            "template_version": TEMPLATE_VERSION,
            "created_at": created_at,
            "updated_at": created_at,
            "creation_receipt_path": written_receipt_path,
            "activation_receipt_path": None,
            "retirement_receipt_path": None,
            "notes": notes,
            "required_files_verified": validation.get("required_files_verified") is True,
            "structural_validation": validation.get("structural_validation"),
            "semantic_validation": validation.get("semantic_validation"),
        }
    )

    return {
        "status": "created",
        "core_id": clean_core_id,
        "creation_receipt_path": written_receipt_path,
        "registry_entry": entry,
        "validation": validation,
    }


def activate_child_core(core_id: str) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    receipt = {
        "artifact_type": "pm_child_core_activation_receipt",
        "artifact_version": TEMPLATE_VERSION,
        "status": "child_core_activation_recorded",
        "core_id": core_id,
        "activated_at": _utc_now(),
        "prior_status": entry.get("status"),
        "governance_note": "Activation is registry state only and does not grant autonomous execution.",
        "persistence_type": "pm_child_core_activation_receipt",
        "mutation_class": RECEIPT_MUTATION_CLASS,
        "advisory_only": False,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    receipt_path = _activation_receipt_path(core_id)
    written_receipt_path = _governed_write(
        receipt_path,
        receipt,
        persistence_type="pm_child_core_activation_receipt",
        mutation_class=RECEIPT_MUTATION_CLASS,
        advisory_only=False,
    )

    updated = activate_core(core_id, written_receipt_path)
    update_core_entry(core_id, {"updated_at": _utc_now()})

    return {
        "status": "activated",
        "core_id": core_id,
        "activation_receipt_path": written_receipt_path,
        "registry_entry": updated,
    }


def create_and_activate_child_core(
    *,
    domain_focus: str,
    display_name: Optional[str] = None,
    core_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    created = create_child_core(
        domain_focus=domain_focus,
        display_name=display_name,
        core_id=core_id,
        notes=notes,
    )
    activated = activate_child_core(created["core_id"])
    return {
        "status": "created_and_activated",
        "core_id": created["core_id"],
        "creation_receipt_path": created["creation_receipt_path"],
        "activation_receipt_path": activated["activation_receipt_path"],
    }