from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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


TEMPLATE_VERSION = "stage12.v1"
RECEIPTS_DIR = PM_CORE_DIR / "state" / "receipts"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slugify(value: str) -> str:
    lowered = value.strip().lower().replace("-", "_").replace(" ", "_")
    parts = [part for part in lowered.split("_") if part]
    return "_".join(parts)


def _core_id_from_domain(domain_focus: str) -> str:
    base = _slugify(domain_focus)
    if not base.endswith("_core"):
        base = f"{base}_core"
    return base


def _core_path(core_id: str) -> Path:
    return CHILD_CORES_DIR / core_id


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")


def _seed_core_identity(core_id: str, display_name: str, domain_focus: str) -> str:
    return f"""# {display_name}

## What it is

Bounded child core for the domain focus: {domain_focus}.

## Why it is there

Provides lawful domain-specific execution under PM_CORE inheritance authority.

## Authority Position

This child core may receive bounded inheritance packets from PM_CORE and may
execute only within its declared domain.

It may not:
- ingest direct research from RESEARCH_CORE
- bypass PM_CORE inheritance
- redefine system truth
- self-activate outside registry lifecycle rules

## Core Identity

- `core_id`: `{core_id}`
- `display_name`: `{display_name}`
- `domain_focus`: `{domain_focus}`
- `template_version`: `{TEMPLATE_VERSION}`
"""


def _seed_inheritance_contract(core_id: str) -> str:
    return f"""# INHERITANCE CONTRACT

## What it is

Governed ingress contract for `{core_id}`.

## Why it is there

Defines the bounded conditions under which a PM inheritance packet may enter
child-core execution state.

## Lawful Entry Rule

This child core may only activate from:
- a PM-produced inheritance packet
- a lawful PM child-core ingress receipt
- an active registry state

## Illegal Entry Conditions

The child core must reject:
- raw research packets
- incomplete PM artifacts
- unverified runtime artifacts
- direct engine output as authority
"""


def _seed_research_interface(core_id: str) -> str:
    return f"""# RESEARCH INTERFACE

## What it is

Governed domain-research intake boundary for `{core_id}`.

## Why it is there

Defines what later domain-specific research may lawfully mean inside this child core.

## Rule

This interface validates domain fit only.
It does not authorize direct RESEARCH_CORE ingress.
"""


def _seed_smi_interface(core_id: str) -> str:
    return f"""# SMI INTERFACE

## What it is

Child-core continuity contract for `{core_id}`.

## Why it is there

Defines how verified local events may be written into child-core continuity state.

## Rule

Continuity may be recorded only after child-core watcher verification succeeds.
"""


def _seed_watcher_interface(core_id: str) -> str:
    return f"""# WATCHER INTERFACE

## What it is

Child-core watcher contract for `{core_id}`.

## Why it is there

Defines how this child core verifies its own execution artifacts before continuity is recorded.

## Rule

Unchecked execution artifacts may not become continuity truth.
"""


def _seed_output_policy(core_id: str, domain_focus: str) -> str:
    return f"""# OUTPUT POLICY

## What it is

Output validation policy for `{core_id}`.

## Why it is there

Defines the minimum bounded output structure for the domain focus `{domain_focus}`.

## Output Rule

Every emitted output must:
- preserve source execution linkage
- remain domain-bounded
- be inspectable
- be verifiable by child-core watcher
"""


def _seed_domain_policy(core_id: str, domain_focus: str) -> str:
    return f"""# DOMAIN POLICY

## What it is

Domain-boundary policy for `{core_id}`.

## Why it is there

Defines what counts as lawful work within the domain focus `{domain_focus}`.

## Rule

This child core may operate only within the declared domain focus and may not
expand into unrelated authority or execution areas.
"""


def _seed_domain_layer(core_id: str) -> str:
    return f"""# DOMAIN LAYER

## What it is

Domain-layer description for `{core_id}`.

## Why it is there

Keeps domain-specific scope explicit and separated from system-wide authority.
"""


def _seed_domain_registry(core_id: str, display_name: str, domain_focus: str) -> Dict[str, Any]:
    return {
        "core_id": core_id,
        "display_name": display_name,
        "domain_focus": domain_focus,
        "allowed_actions": [
            "bounded_domain_execution",
            "domain_output_generation",
            "child_core_artifact_verification",
            "local_continuity_recording_after_verification",
        ],
        "forbidden_actions": [
            "direct_research_ingress",
            "cross_domain_authority_override",
            "self_activation",
            "engine_as_authority",
            "unverified_output_persistence",
        ],
        "research_themes": [
            domain_focus,
            f"{domain_focus} bounded execution",
            f"{domain_focus} output generation",
        ],
        "status": "draft",
        "template_version": TEMPLATE_VERSION,
    }


def _seed_ingress_processor(core_id: str) -> str:
    return f'''from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def process_ingress(ingress_receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage-12 scaffold surface for {core_id} child-core execution.

    This file is seeded by PM_CORE lawful creation and must later be refined
    without violating the child-core contract.
    """
    return {{
        "status": "scaffolded_not_yet_customized",
        "core_id": "{core_id}",
        "received_ingress_receipt": bool(ingress_receipt),
    }}
'''


def _seed_output_builder(core_id: str) -> str:
    return f'''from __future__ import annotations

from typing import Any, Dict


def build_output(execution_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage-12 scaffold output builder for {core_id}.
    """
    return {{
        "status": "scaffolded_output",
        "core_id": "{core_id}",
        "execution_record_present": bool(execution_record),
    }}
'''


def _seed_core_watcher(core_id: str) -> str:
    return f'''from __future__ import annotations

from typing import Any, Dict


def verify_child_core_artifacts(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage-12 scaffold child-core watcher for {core_id}.
    """
    return {{
        "status": "scaffolded_verification_surface",
        "core_id": "{core_id}",
        "verified": bool(artifacts),
    }}
'''


def _seed_core_smi(core_id: str) -> str:
    return f'''from __future__ import annotations

from typing import Any, Dict


def record_child_core_continuity(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage-12 scaffold child-core continuity surface for {core_id}.
    """
    return {{
        "status": "scaffolded_continuity_surface",
        "core_id": "{core_id}",
        "event_received": bool(event),
    }}
'''


def _seed_research_module(core_id: str) -> str:
    return f'''from __future__ import annotations

from typing import Any, Dict


def validate_domain_research(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stage-12 scaffold domain research validation surface for {core_id}.
    """
    return {{
        "status": "scaffolded_research_surface",
        "core_id": "{core_id}",
        "payload_received": bool(payload),
    }}
'''


def _blank_json_state() -> Dict[str, Any]:
    return {}


def _activation_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__activation_receipt.json"


def _creation_receipt_path(core_id: str) -> Path:
    return RECEIPTS_DIR / f"{core_id}__creation_receipt.json"


def create_child_core(
    *,
    domain_focus: str,
    display_name: Optional[str] = None,
    core_id: Optional[str] = None,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    ensure_registry_files_exist()

    resolved_core_id = core_id or _core_id_from_domain(domain_focus)
    resolved_display_name = display_name or resolved_core_id.replace("_", " ").title()
    now = _utc_now()
    core_root = _core_path(resolved_core_id)

    if core_root.exists():
        raise ValueError(f"Child-core path already exists: {core_root.as_posix()}")

    # Directories
    for directory in REQUIRED_DIRECTORIES:
        (core_root / directory).mkdir(parents=True, exist_ok=True)

    # Governance files
    _write_text(core_root / "CORE_IDENTITY.md", _seed_core_identity(resolved_core_id, resolved_display_name, domain_focus))
    _write_text(core_root / "INHERITANCE_CONTRACT.md", _seed_inheritance_contract(resolved_core_id))
    _write_text(core_root / "RESEARCH_INTERFACE.md", _seed_research_interface(resolved_core_id))
    _write_text(core_root / "SMI_INTERFACE.md", _seed_smi_interface(resolved_core_id))
    _write_text(core_root / "WATCHER_INTERFACE.md", _seed_watcher_interface(resolved_core_id))
    _write_text(core_root / "OUTPUT_POLICY.md", _seed_output_policy(resolved_core_id, domain_focus))
    _write_text(core_root / "DOMAIN_POLICY.md", _seed_domain_policy(resolved_core_id, domain_focus))
    _write_json(core_root / "DOMAIN_REGISTRY.json", _seed_domain_registry(resolved_core_id, resolved_display_name, domain_focus))

    # Runtime files
    _write_text(core_root / "execution" / "ingress_processor.py", _seed_ingress_processor(resolved_core_id))
    _write_text(core_root / "outputs" / "output_builder.py", _seed_output_builder(resolved_core_id))
    _write_text(core_root / "watcher" / "core_watcher.py", _seed_core_watcher(resolved_core_id))
    _write_text(core_root / "smi" / "core_smi.py", _seed_core_smi(resolved_core_id))
    _write_text(core_root / "research" / "research_interface.py", _seed_research_module(resolved_core_id))
    _write_text(core_root / "domains" / "_DOMAIN_LAYER.md", _seed_domain_layer(resolved_core_id))

    # State seed
    _write_json(core_root / "state" / "current" / "core_smi_state.json", _blank_json_state())

    entry = {
        "core_id": resolved_core_id,
        "display_name": resolved_display_name,
        "domain_focus": domain_focus,
        "status": "draft",
        "template_version": TEMPLATE_VERSION,
        "created_at": now,
        "updated_at": now,
        "core_path": core_root.as_posix(),
        "domain_registry_path": (core_root / "DOMAIN_REGISTRY.json").as_posix(),
        "required_files_verified": False,
        "structural_validation": None,
        "semantic_validation": None,
        "activation_receipt_path": None,
        "retirement_receipt_path": None,
        "notes": notes,
    }
    register_core_entry(entry)

    creation_receipt = {
        "status": "child_core_created",
        "core_id": resolved_core_id,
        "display_name": resolved_display_name,
        "domain_focus": domain_focus,
        "template_version": TEMPLATE_VERSION,
        "created_at": now,
        "core_path": core_root.as_posix(),
        "required_directories": REQUIRED_DIRECTORIES,
        "required_files": REQUIRED_FILES,
    }
    _write_json(_creation_receipt_path(resolved_core_id), creation_receipt)

    update_core_entry(
        resolved_core_id,
        {
            "updated_at": _utc_now(),
            "notes": notes,
        },
    )

    return {
        "status": "created",
        "core_id": resolved_core_id,
        "core_path": core_root.as_posix(),
        "creation_receipt_path": _creation_receipt_path(resolved_core_id).as_posix(),
    }


def validate_child_core(core_id: str) -> Dict[str, Any]:
    validation = validate_registered_core(core_id)
    update_core_entry(
        core_id,
        {
            "updated_at": _utc_now(),
            "structural_validation": validation.details.get("structural"),
            "semantic_validation": validation.details.get("semantic"),
            "required_files_verified": validation.ok,
        },
    )
    return validation.to_dict()


def activate_child_core(core_id: str) -> Dict[str, Any]:
    entry = get_entry(core_id)
    if entry is None:
        raise ValueError(f"Child core '{core_id}' is not registered.")

    validation = validate_child_core(core_id)
    if not validation["ok"]:
        raise ValueError(
            f"Child core '{core_id}' failed validation and cannot be activated."
        )

    receipt = {
        "status": "child_core_activated",
        "core_id": core_id,
        "activated_at": _utc_now(),
        "template_version": entry.get("template_version"),
        "core_path": entry.get("core_path"),
        "validation": validation,
    }
    receipt_path = _activation_receipt_path(core_id)
    _write_json(receipt_path, receipt)

    updated = activate_core(core_id, receipt_path.as_posix())
    update_core_entry(core_id, {"updated_at": _utc_now()})

    return {
        "status": "activated",
        "core_id": core_id,
        "activation_receipt_path": receipt_path.as_posix(),
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