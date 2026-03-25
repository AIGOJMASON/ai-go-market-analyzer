from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["contractor-builder-v1-operator-ui"])


@router.get("/operator", response_class=HTMLResponse)
def operator_dashboard_page() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>AI_GO Contractor Builder V1</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; line-height: 1.4; }
    h1, h2, h3 { margin-bottom: 8px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
    label { display: block; font-weight: bold; margin-bottom: 4px; }
    input, select, textarea, button { width: 100%; padding: 8px; box-sizing: border-box; }
    textarea { min-height: 90px; }
    .panel { border: 1px solid #ccc; padding: 12px; margin-top: 16px; border-radius: 6px; }
    .mono { font-family: Consolas, monospace; white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <h1>AI_GO Contractor Builder V1</h1>
  <p>Canonical operator dashboard at <strong>/operator</strong>.</p>

  <div class="panel">
    <h2>Operator Input</h2>

    <div class="row">
      <div>
        <label for="request_id">Request ID</label>
        <input id="request_id" value="contractor-live-001" />
      </div>
      <div>
        <label for="project_type">Project Type</label>
        <select id="project_type">
          <option value="remodel" selected>remodel</option>
          <option value="repair">repair</option>
          <option value="new_build">new_build</option>
          <option value="maintenance">maintenance</option>
        </select>
      </div>
    </div>

    <div class="row">
      <div>
        <label for="trade_focus">Trade Focus</label>
        <select id="trade_focus">
          <option value="general">general</option>
          <option value="roofing">roofing</option>
          <option value="electrical">electrical</option>
          <option value="plumbing">plumbing</option>
          <option value="hvac">hvac</option>
          <option value="interior" selected>interior</option>
          <option value="exterior">exterior</option>
        </select>
      </div>
      <div>
        <label for="location_mode">Location Mode</label>
        <select id="location_mode">
          <option value="onsite">onsite</option>
          <option value="remote" selected>remote</option>
          <option value="hybrid">hybrid</option>
        </select>
      </div>
    </div>

    <div class="row">
      <div>
        <label for="budget_band">Budget Band</label>
        <select id="budget_band">
          <option value="low">low</option>
          <option value="medium" selected>medium</option>
          <option value="high">high</option>
        </select>
      </div>
      <div>
        <label for="timeline_band">Timeline Band</label>
        <select id="timeline_band">
          <option value="urgent">urgent</option>
          <option value="near_term" selected>near_term</option>
          <option value="flexible">flexible</option>
        </select>
      </div>
    </div>

    <div class="row">
      <div>
        <label for="confirmation">Confirmation</label>
        <select id="confirmation">
          <option value="confirmed">confirmed</option>
          <option value="partial" selected>partial</option>
          <option value="missing">missing</option>
        </select>
      </div>
      <div></div>
    </div>

    <div>
      <label for="scope_summary">Scope Summary</label>
      <textarea id="scope_summary">Interior kitchen refresh with cabinet, lighting, and minor layout planning.</textarea>
    </div>

    <div style="margin-top:12px;">
      <button onclick="submitCase()">Run Live Case</button>
    </div>
  </div>

  <div id="output" class="panel" style="display:none;">
    <h2>System View</h2>

    <div class="panel"><h3>Case</h3><div id="case_panel" class="mono"></div></div>
    <div class="panel"><h3>Runtime</h3><div id="runtime_panel" class="mono"></div></div>
    <div class="panel"><h3>Recommendation</h3><div id="recommendation_panel" class="mono"></div></div>
    <div class="panel"><h3>Cognition</h3><div id="cognition_panel" class="mono"></div></div>
    <div class="panel"><h3>PM Workflow</h3><div id="pm_workflow_panel" class="mono"></div></div>
    <div class="panel"><h3>Governance</h3><div id="governance_panel" class="mono"></div></div>
  </div>

  <script>
    function pretty(obj) {
      return JSON.stringify(obj, null, 2);
    }

    async function submitCase() {
      const payload = {
        request_id: document.getElementById("request_id").value,
        project_type: document.getElementById("project_type").value,
        trade_focus: document.getElementById("trade_focus").value,
        scope_summary: document.getElementById("scope_summary").value,
        budget_band: document.getElementById("budget_band").value,
        timeline_band: document.getElementById("timeline_band").value,
        location_mode: document.getElementById("location_mode").value,
        confirmation: document.getElementById("confirmation").value
      };

      const response = await fetch("/contractor-builder/run/live", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();
      const view = data.system_view || {};

      document.getElementById("output").style.display = "block";
      document.getElementById("case_panel").textContent = pretty(view.case || {});
      document.getElementById("runtime_panel").textContent = pretty(view.runtime || {});
      document.getElementById("recommendation_panel").textContent = pretty(view.recommendation || {});
      document.getElementById("cognition_panel").textContent = pretty(view.cognition || {});
      document.getElementById("pm_workflow_panel").textContent = pretty(view.pm_workflow || {});
      document.getElementById("governance_panel").textContent = pretty(view.governance || {});
    }
  </script>
</body>
</html>
"""