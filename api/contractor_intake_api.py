"""
Contractor intake API surface for contractor_builder_v1.

Stage 1 purpose:
- create project root state
- lock baseline
- emit intake receipts
- return created project view

Northstar rule:
Project creation is Tier 1 mutation. It must pass root governance before the
intake runner writes project state.
"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from AI_GO.child_cores.contractor_builder_v1.ui.project_intake_runner import (
    create_project_from_form,
)
from AI_GO.core.governance.mutation_declaration import mutation_surface
from AI_GO.core.governance.request_governor import govern_request_from_dict


router = APIRouter(prefix="/intake", tags=["contractor_intake"])


INTAKE_MUTATION_CLASS = "project_creation"
INTAKE_PERSISTENCE_TYPE = "filesystem"
INTAKE_ADVISORY_ONLY = False


class ContractorProjectFormRequest(BaseModel):
    project_name: str
    project_type: str
    project_description: str = ""
    client_name: str
    client_email: str = ""
    pm_name: str
    pm_email: str = ""
    site_address: str = ""
    city: str = ""
    county: str = ""
    state: str
    authority_name: str = ""
    portfolio_id: str = ""
    notes: str = ""
    actor: str = "contractor_intake_api"
    operator_approved: bool = False


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>AI_GO Contractor Intake</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1220;
      --panel: #121a2b;
      --panel-2: #18233a;
      --border: #29344f;
      --text: #e7edf7;
      --muted: #a9b4c9;
      --ok: #74d99f;
      --bad: #ff7b7b;
      --accent: #7cb7ff;
      --link: #9fd0ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }
    .wrap { max-width: 1400px; margin: 0 auto; padding: 24px; }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }
    .title { font-size: 28px; font-weight: 700; margin-bottom: 8px; }
    .subtitle { color: var(--muted); line-height: 1.5; max-width: 900px; }
    .nav a { color: var(--link); text-decoration: none; margin-left: 16px; font-weight: 700; }
    .grid { display: grid; grid-template-columns: 460px 1fr; gap: 20px; align-items: start; }
    .panel, .section {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
      margin-bottom: 18px;
    }
    .panel h2, .section h3 { margin: 0 0 14px 0; font-size: 18px; }
    .field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    label { display: block; margin: 12px 0 6px 0; font-size: 13px; color: var(--muted); }
    input, textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
      font-size: 14px;
    }
    textarea { min-height: 100px; resize: vertical; font-family: Arial, Helvetica, sans-serif; }
    button {
      margin-top: 16px;
      width: 100%;
      padding: 12px 14px;
      border: 0;
      border-radius: 10px;
      background: var(--accent);
      color: #081120;
      font-weight: 700;
      cursor: pointer;
    }
    button:disabled { opacity: 0.7; cursor: wait; }
    .status { margin-top: 14px; min-height: 20px; color: var(--muted); font-size: 14px; line-height: 1.5; }
    .ok { color: var(--ok); }
    .bad { color: var(--bad); }
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text);
    }
    .empty { color: var(--muted); }
    .approval-row {
      display: flex;
      gap: 10px;
      align-items: center;
      margin-top: 14px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.4;
    }
    .approval-row input { width: auto; }
    @media (max-width: 1100px) {
      .grid { grid-template-columns: 1fr; }
      .field-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <div class="title">AI_GO Contractor Intake</div>
        <div class="subtitle">
          Stage 1 creates project root state and baseline lock. Under Northstar,
          this is governed mutation and requires explicit operator approval.
        </div>
      </div>
      <div class="nav">
        <a href="/contractor-builder/intake/new-project">New Project</a>
        <a href="/contractor-dashboard">Live Dashboard</a>
      </div>
    </div>

    <div class="grid">
      <div class="panel">
        <h2>New Project Form</h2>

        <label for="apiBase">API Base URL</label>
        <input id="apiBase" value="" placeholder="Leave blank for same-origin" />

        <label for="apiKey">API Key</label>
        <input id="apiKey" type="password" value="" placeholder="x-api-key if required" />

        <label for="projectName">Project Name</label>
        <input id="projectName" value="Demo Kitchen Remodel" />

        <div class="field-grid">
          <div>
            <label for="projectType">Project Type</label>
            <input id="projectType" value="Kitchen Remodel" />
          </div>
          <div>
            <label for="portfolioId">Portfolio ID</label>
            <input id="portfolioId" value="portfolio-demo" />
          </div>
        </div>

        <label for="projectDescription">Project Description</label>
        <textarea id="projectDescription">Kitchen renovation with cabinet, electrical, and inspection work.</textarea>

        <div class="field-grid">
          <div>
            <label for="clientName">Client Name</label>
            <input id="clientName" value="Demo Client" />
          </div>
          <div>
            <label for="clientEmail">Client Email</label>
            <input id="clientEmail" value="test@test.com" />
          </div>
        </div>

        <div class="field-grid">
          <div>
            <label for="pmName">PM Name</label>
            <input id="pmName" value="Demo PM" />
          </div>
          <div>
            <label for="pmEmail">PM Email</label>
            <input id="pmEmail" value="pm@test.com" />
          </div>
        </div>

        <label for="siteAddress">Site Address</label>
        <input id="siteAddress" value="123 Demo Lane" />

        <div class="field-grid">
          <div>
            <label for="city">City</label>
            <input id="city" value="Scottsburg" />
          </div>
          <div>
            <label for="county">County</label>
            <input id="county" value="Scott" />
          </div>
        </div>

        <div class="field-grid">
          <div>
            <label for="state">State</label>
            <input id="state" value="IN" />
          </div>
          <div>
            <label for="authorityName">Authority Name</label>
            <input id="authorityName" value="Scottsburg Building Department" />
          </div>
        </div>

        <label for="notes">Notes</label>
        <textarea id="notes">Initial Stage 1 intake only. Workflow setup comes later.</textarea>

        <div class="approval-row">
          <input id="operatorApproved" type="checkbox" />
          <span>I approve this governed project-creation mutation.</span>
        </div>

        <button id="createBtn">Create Project</button>
        <div id="status" class="status"></div>
      </div>

      <div>
        <div class="section">
          <h3>Governance Decision</h3>
          <pre id="governanceDecision" class="empty">No governance decision yet.</pre>
        </div>

        <div class="section">
          <h3>Project Created View</h3>
          <pre id="createdView" class="empty">No project created yet.</pre>
        </div>

        <div class="section">
          <h3>Artifact Paths</h3>
          <pre id="artifactPaths" class="empty">No artifact paths written yet.</pre>
        </div>

        <div class="section">
          <h3>Receipt Paths</h3>
          <pre id="receiptPaths" class="empty">No receipt paths written yet.</pre>
        </div>
      </div>
    </div>
  </div>

  <script>
    const els = {
      apiBase: document.getElementById("apiBase"),
      apiKey: document.getElementById("apiKey"),
      projectName: document.getElementById("projectName"),
      projectType: document.getElementById("projectType"),
      projectDescription: document.getElementById("projectDescription"),
      clientName: document.getElementById("clientName"),
      clientEmail: document.getElementById("clientEmail"),
      pmName: document.getElementById("pmName"),
      pmEmail: document.getElementById("pmEmail"),
      siteAddress: document.getElementById("siteAddress"),
      city: document.getElementById("city"),
      county: document.getElementById("county"),
      state: document.getElementById("state"),
      authorityName: document.getElementById("authorityName"),
      portfolioId: document.getElementById("portfolioId"),
      notes: document.getElementById("notes"),
      operatorApproved: document.getElementById("operatorApproved"),
      createBtn: document.getElementById("createBtn"),
      status: document.getElementById("status"),
      governanceDecision: document.getElementById("governanceDecision"),
      createdView: document.getElementById("createdView"),
      artifactPaths: document.getElementById("artifactPaths"),
      receiptPaths: document.getElementById("receiptPaths")
    };

    function getBaseUrl() {
      const base = (els.apiBase.value || "").trim();
      return base ? base.replace(/\\/$/, "") : "";
    }

    function getHeaders() {
      const headers = { "Content-Type": "application/json" };
      const apiKey = (els.apiKey.value || "").trim();
      if (apiKey) {
        headers["x-api-key"] = apiKey;
      }
      return headers;
    }

    function pretty(value) {
      return JSON.stringify(value, null, 2);
    }

    function setStatus(message, cls = "") {
      els.status.className = "status " + cls;
      els.status.textContent = message;
    }

    function buildRequestBody() {
      return {
        project_name: (els.projectName.value || "").trim(),
        project_type: (els.projectType.value || "").trim(),
        project_description: (els.projectDescription.value || "").trim(),
        client_name: (els.clientName.value || "").trim(),
        client_email: (els.clientEmail.value || "").trim(),
        pm_name: (els.pmName.value || "").trim(),
        pm_email: (els.pmEmail.value || "").trim(),
        site_address: (els.siteAddress.value || "").trim(),
        city: (els.city.value || "").trim(),
        county: (els.county.value || "").trim(),
        state: (els.state.value || "").trim(),
        authority_name: (els.authorityName.value || "").trim(),
        portfolio_id: (els.portfolioId.value || "").trim(),
        notes: (els.notes.value || "").trim(),
        operator_approved: Boolean(els.operatorApproved.checked),
        actor: "contractor_intake_ui"
      };
    }

    async function createProject() {
      const body = buildRequestBody();
      const url = getBaseUrl() + "/contractor-builder/intake/create-form";
      const headers = getHeaders();

      els.createBtn.disabled = true;
      setStatus("Submitting governed project creation...");

      try {
        const response = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify(body)
        });

        const data = await response.json();

        els.governanceDecision.textContent = pretty(data.governance_decision || data.detail?.governance_decision || {});
        els.createdView.textContent = pretty(data.created_view || data);
        els.artifactPaths.textContent = pretty(data.artifact_paths || {});
        els.receiptPaths.textContent = pretty(data.receipt_paths || {});

        if (!response.ok) {
          setStatus("Project creation blocked or failed.", "bad");
          return;
        }

        setStatus("Project created under governed intake boundary.", "ok");
      } catch (error) {
        setStatus("Network or runtime error: " + String(error), "bad");
      } finally {
        els.createBtn.disabled = false;
      }
    }

    els.createBtn.addEventListener("click", createProject);
  </script>
</body>
</html>
"""


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _intake_classification() -> Dict[str, Any]:
    return {
        "persistence_type": INTAKE_PERSISTENCE_TYPE,
        "mutation_class": INTAKE_MUTATION_CLASS,
        "execution_allowed": False,
        "state_mutation_allowed": True,
        "workflow_mutation_allowed": False,
        "project_truth_mutation_allowed": True,
        "authority_mutation_allowed": False,
        "advisory_only": INTAKE_ADVISORY_ONLY,
    }


def _build_intake_watcher_result(request: ContractorProjectFormRequest) -> Dict[str, Any]:
    errors = []

    if not _safe_str(request.project_name):
        errors.append("project_name_required")

    if not _safe_str(request.project_type):
        errors.append("project_type_required")

    if not _safe_str(request.client_name):
        errors.append("client_name_required")

    if not _safe_str(request.pm_name):
        errors.append("pm_name_required")

    if not _safe_str(request.state):
        errors.append("state_required")

    return {
        "status": "passed" if not errors else "blocked",
        "valid": len(errors) == 0,
        "errors": errors,
        "source": "contractor_intake_api_pre_governor_check",
        "temporary_until_root_watcher": True,
    }


def _enforce_project_creation_governance(
    *,
    request: ContractorProjectFormRequest,
) -> Dict[str, Any]:
    watcher_result = _build_intake_watcher_result(request)
    classification = _intake_classification()

    governance_decision = govern_request_from_dict(
        {
            "request_id": f"project-intake-{_safe_str(request.project_name).replace(' ', '_')}",
            "route": "/contractor-builder/intake/create-form",
            "method": "POST",
            "actor": _safe_str(request.actor) or "contractor_intake_api",
            "target": "contractor_builder_v1.project_creation",
            "child_core_id": "contractor_builder_v1",
            "action_type": "create_project",
            "action_class": "write_state",
            "project_id": "",
            "phase_id": "",
            "payload": {
                "project_name": request.project_name,
                "project_type": request.project_type,
                "client_name": request.client_name,
                "pm_name": request.pm_name,
                "state": request.state,
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": bool(request.operator_approved),
                "mutation_class": INTAKE_MUTATION_CLASS,
                "persistence_type": INTAKE_PERSISTENCE_TYPE,
                "advisory_only": INTAKE_ADVISORY_ONLY,
            },
            "context": {
                "watcher_result": watcher_result,
                "receipt_planned": True,
                "state_mutation_declared": True,
                "operator_approved": bool(request.operator_approved),
                "approval_required": True,
                "classification": classification,
            },
        }
    )

    if governance_decision.get("allowed") is not True:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "request_governor_blocked",
                "message": "Project creation blocked by root Request Governor.",
                "governance_decision": governance_decision,
            },
        )

    return governance_decision


@router.get("/new-project", response_class=HTMLResponse)
def contractor_new_project_ui() -> HTMLResponse:
    return HTMLResponse(content=HTML_PAGE)


@router.post("/create-form")
@mutation_surface(
    mutation_class=INTAKE_MUTATION_CLASS,
    persistence_type=INTAKE_PERSISTENCE_TYPE,
    advisory_only=INTAKE_ADVISORY_ONLY,
)
def create_project_from_form_api(request: ContractorProjectFormRequest) -> Dict[str, Any]:
    try:
        governance_decision = _enforce_project_creation_governance(request=request)

        result = create_project_from_form(request.model_dump())

        if isinstance(result, dict):
            result["governance_decision"] = governance_decision
            result["classification"] = _intake_classification()

        return result

    except HTTPException:
        raise
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))