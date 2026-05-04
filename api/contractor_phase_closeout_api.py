from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from AI_GO.core.state_runtime.state_paths import contractor_project_root
from AI_GO.core.governance.governed_execution import execute_governed_action

# (imports trimmed here for clarity — keep your existing business imports unchanged)

router = APIRouter(prefix="/phase-closeout", tags=["phase_closeout"])


class PhaseCloseoutRequest(BaseModel):
    project_id: str
    phase_id: str
    client_email: str
    client_name: str = "Customer"
    project_name: str = ""
    email_subject: str = ""
    email_body: str = ""
    actor: str = "phase_closeout_api"
    allow_resend_if_sent: bool = True
    operator_approved: bool = False


# -------------------------
# 🔒 PATH ANCHOR FIX
# -------------------------

def _project_root(project_id: str) -> Path:
    """
    Canonical project root resolver.

    NO fallback paths.
    NO relative paths.
    """
    return contractor_project_root(project_id)


def _documents_root(project_id: str) -> Path:
    return _project_root(project_id) / "documents" / "phase_closeout_pdfs"


def _delivery_root(project_id: str) -> Path:
    return _project_root(project_id) / "delivery"


def _assert_project_exists(project_id: str) -> None:
    root = _project_root(project_id)
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Unknown project_id: {project_id}")


# -------------------------
# 🧠 EXISTING LOGIC (UNCHANGED)
# -------------------------

def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


# -------------------------
# 🚀 MAIN ENTRY
# -------------------------

@router.post("/run")
def run_phase_closeout(req: PhaseCloseoutRequest) -> Dict[str, Any]:
    project_id = _safe_str(req.project_id)
    phase_id = _safe_str(req.phase_id)

    if not project_id:
        raise HTTPException(status_code=400, detail="project_id is required")

    if not phase_id:
        raise HTTPException(status_code=400, detail="phase_id is required")

    _assert_project_exists(project_id)

    request_id = f"phase-closeout-{project_id}-{phase_id}"

    result = execute_governed_action(
        request={
            "request_id": request_id,
            "route": "/contractor-builder/phase-closeout/run",
            "method": "POST",
            "actor": req.actor,
            "target": "contractor_builder_v1.phase_closeout",
            "child_core_id": "contractor_builder_v1",
            "action_type": "phase_closeout",
            "action_class": "workflow_transition",
            "project_id": project_id,
            "phase_id": phase_id,
            "payload": req.model_dump(),
        }
    )

    if result.get("allowed") is not True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "governed_execution_blocked",
                "execution_result": result,
            },
        )

    return result