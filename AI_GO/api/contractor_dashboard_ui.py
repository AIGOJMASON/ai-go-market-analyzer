"""
Contractor live dashboard UI for contractor_builder_v1.

This UI is intentionally thin:
- serves one operator page
- posts to the canonical live contractor endpoint
- renders returned dashboard payload, watcher result, cycle status, and visibility paths
- can trigger phase closeout / signoff email from the currently loaded project payload
- reads and displays the System Brain surface through the read-only API
- reads and displays deterministic posture explanation through the read-only API

It does not contain business logic.
It does not mutate contractor truth directly.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["contractor_dashboard_ui"])


HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>AI_GO Contractor Dashboard</title>
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
      --warn: #ffd166;
      --bad: #ff7b7b;
      --accent: #7cb7ff;
      --accent-2: #95d5ff;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }

    .wrap {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px;
    }

    .title {
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .subtitle {
      color: var(--muted);
      margin-bottom: 24px;
      line-height: 1.5;
    }

    .grid {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 20px;
      align-items: start;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
      margin-bottom: 18px;
    }

    .panel h2 {
      margin: 0 0 14px 0;
      font-size: 18px;
    }

    label {
      display: block;
      margin: 12px 0 6px 0;
      font-size: 13px;
      color: var(--muted);
    }

    input, textarea {
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
      font-size: 14px;
    }

    textarea {
      min-height: 260px;
      resize: vertical;
      font-family: Consolas, monospace;
    }

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

    button.secondary {
      background: var(--accent-2);
    }

    button:disabled {
      opacity: 0.7;
      cursor: wait;
    }

    .status {
      margin-top: 14px;
      min-height: 20px;
      color: var(--muted);
      font-size: 14px;
      line-height: 1.5;
    }

    .cards {
      display: grid;
      grid-template-columns: repeat(2, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 16px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }

    .card .label {
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .card .value {
      font-size: 20px;
      font-weight: 700;
    }

    .ok { color: var(--ok); }
    .warn { color: var(--warn); }
    .bad { color: var(--bad); }

    .section {
      margin-top: 16px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }

    .section h3 {
      margin: 0 0 12px 0;
      font-size: 16px;
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text);
    }

    .muted {
      color: var(--muted);
    }

    .helper {
      margin-top: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.5;
    }

    @media (max-width: 1100px) {
      .grid {
        grid-template-columns: 1fr;
      }

      .cards {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="title">AI_GO Contractor Dashboard</div>
    <div class="subtitle">
      Governed contractor read surface. This page calls the single live contractor endpoint, shows the validated dashboard payload, reads the System Brain surface, explains system posture, and can trigger phase closeout / signoff email for the currently loaded phase.
    </div>

    <div class="grid">
      <div>
        <div class="panel">
          <h2>Live Run Request</h2>

          <label for="apiBase">API Base URL</label>
          <input id="apiBase" value="" placeholder="Leave blank for same-origin" />

          <label for="apiKey">API Key</label>
          <input id="apiKey" type="password" value="" placeholder="x-api-key if required" />

          <label for="requestBody">Request JSON</label>
          <textarea id="requestBody"></textarea>

          <button id="runBtn">Run Live Dashboard</button>
          <div id="status" class="status"></div>
        </div>

        <div class="panel">
          <h2>Phase Signoff</h2>

          <label for="signoffProjectId">Project ID</label>
          <input id="signoffProjectId" value="" placeholder="Populated after dashboard run" />

          <label for="signoffPhaseId">Phase ID</label>
          <input id="signoffPhaseId" value="" placeholder="Populated after dashboard run" />

          <label for="signoffClientEmail">Client Email</label>
          <input id="signoffClientEmail" value="" placeholder="customer@example.com" />

          <button id="signoffBtn" class="secondary">Send for Signoff</button>

          <div class="helper">
            This triggers the governed phase closeout route and writes signoff status back into workflow state.
          </div>

          <div id="signoffStatus" class="status"></div>
        </div>
      </div>

      <div>
        <div class="cards">
          <div class="card">
            <div class="label">Cycle Status</div>
            <div id="cycleStatus" class="value muted">Not run</div>
          </div>
          <div class="card">
            <div class="label">Watcher Validation</div>
            <div id="watcherStatus" class="value muted">Unknown</div>
          </div>
          <div class="card">
            <div class="label">Project</div>
            <div id="projectName" class="value muted">No payload</div>
          </div>
          <div class="card">
            <div class="label">Compliance Blocking</div>
            <div id="complianceBlocking" class="value muted">Unknown</div>
          </div>
        </div>

        <div class="section">
          <h3>System Brain</h3>
          <pre id="systemBrainSummary" class="muted">No System Brain loaded.</pre>
        </div>

        <div class="section">
          <h3>Why This Posture?</h3>
          <pre id="postureExplanation" class="muted">No posture explanation loaded.</pre>
        </div>

        <div class="section">
          <h3>Posture Reasons</h3>
          <pre id="postureReasons" class="muted">No posture reasons loaded.</pre>
        </div>

        <div class="section">
          <h3>System Brain Cards</h3>
          <pre id="systemBrainCards" class="muted">No cards loaded.</pre>
        </div>

        <div class="section">
          <h3>What to Watch</h3>
          <pre id="systemBrainWatch" class="muted">No watch items loaded.</pre>
        </div>

        <div class="section">
          <h3>Operator Read</h3>
          <pre id="operatorRead" class="muted">No explanation loaded.</pre>
        </div>

        <div class="section">
          <h3>Watcher Result</h3>
          <pre id="watcherResult" class="muted">No watcher result loaded.</pre>
        </div>

        <div class="section">
          <h3>Visibility Paths</h3>
          <pre id="visibilityPaths" class="muted">No visibility paths written yet.</pre>
        </div>

        <div class="section">
          <h3>Phase Signoff Result</h3>
          <pre id="signoffResult" class="muted">No signoff request sent yet.</pre>
        </div>

        <div class="section">
          <h3>Dashboard Payload</h3>
          <pre id="dashboardPayload" class="muted">No dashboard payload loaded.</pre>
        </div>
      </div>
    </div>
  </div>

  <script>
    const defaultRequest = {
      request_id: "contractor-live-demo-001",
      reporting_period_label: "Weekly Demo",
      target_project_id: "project-demo-001",
      target_portfolio_id: "portfolio-demo",
      persist_visibility: true,
      persist_by_request: true,
      portfolio_project_map: {
        "portfolio-demo": ["project-demo-001"]
      },
      project_payloads: [
        {
          project_id: "project-demo-001",
          project_profile: {
            project_id: "project-demo-001",
            project_name: "Demo Kitchen Remodel",
            project_type: "Kitchen Remodel",
            status: "active",
            portfolio_id: "portfolio-demo",
            client: {
              name: "Demo Client",
              email: "test@test.com"
            },
            pm: { name: "Demo PM" },
            jurisdiction: {
              jurisdiction_id: "scottsburg-in",
              state: "IN"
            }
          },
          baseline_lock: {
            baseline_refs: {
              schedule_baseline_id: "schedule-demo-001",
              budget_baseline_id: "budget-demo-001",
              compliance_snapshot_id: "compliance-demo-001"
            }
          },
          workflow_snapshot: {
            workflow_status: "active",
            phase_count: 3,
            current_phase_id: "phase-demo-framing"
          },
          change_records: [],
          compliance_snapshot: {
            blocking: false,
            blocking_count: 0,
            permits: [],
            inspections: []
          },
          router_snapshot: {
            conflict_count: 0
          },
          oracle_snapshot: {
            summary_label: "stable"
          },
          decision_records: [],
          risk_records: [],
          assumption_records: []
        }
      ]
    };

    const els = {
      apiBase: document.getElementById("apiBase"),
      apiKey: document.getElementById("apiKey"),
      requestBody: document.getElementById("requestBody"),
      runBtn: document.getElementById("runBtn"),
      status: document.getElementById("status"),

      cycleStatus: document.getElementById("cycleStatus"),
      watcherStatus: document.getElementById("watcherStatus"),
      projectName: document.getElementById("projectName"),
      complianceBlocking: document.getElementById("complianceBlocking"),

      systemBrainSummary: document.getElementById("systemBrainSummary"),
      postureExplanation: document.getElementById("postureExplanation"),
      postureReasons: document.getElementById("postureReasons"),
      systemBrainCards: document.getElementById("systemBrainCards"),
      systemBrainWatch: document.getElementById("systemBrainWatch"),

      operatorRead: document.getElementById("operatorRead"),
      watcherResult: document.getElementById("watcherResult"),
      visibilityPaths: document.getElementById("visibilityPaths"),
      dashboardPayload: document.getElementById("dashboardPayload"),

      signoffProjectId: document.getElementById("signoffProjectId"),
      signoffPhaseId: document.getElementById("signoffPhaseId"),
      signoffClientEmail: document.getElementById("signoffClientEmail"),
      signoffBtn: document.getElementById("signoffBtn"),
      signoffStatus: document.getElementById("signoffStatus"),
      signoffResult: document.getElementById("signoffResult")
    };

    els.requestBody.value = JSON.stringify(defaultRequest, null, 2);

    function pretty(value) {
      return JSON.stringify(value, null, 2);
    }

    function setStatus(message, cls = "muted") {
      els.status.className = "status " + cls;
      els.status.textContent = message;
    }

    function setSignoffStatus(message, cls = "muted") {
      els.signoffStatus.className = "status " + cls;
      els.signoffStatus.textContent = message;
    }

    function setValue(el, text, cls = "muted") {
      el.className = "value " + cls;
      el.textContent = text;
    }

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

    function populateSignoffFields(dashboard, requestBody) {
      const summary = dashboard.summary_panel || {};
      const projectPanel = dashboard.project_panel || {};
      const workflow = projectPanel.workflow || {};

      els.signoffProjectId.value = summary.project_id || projectPanel.project_id || "";
      els.signoffPhaseId.value = workflow.current_phase_id || summary.current_phase_id || "";

      const targetProjectId = els.signoffProjectId.value;
      const payloads = Array.isArray(requestBody?.project_payloads) ? requestBody.project_payloads : [];
      const matched = payloads.find(p => p.project_id === targetProjectId) || {};
      const email = matched?.project_profile?.client?.email || "";
      if (email && !els.signoffClientEmail.value) {
        els.signoffClientEmail.value = email;
      }
    }

    async function loadPostureExplanation() {
      const url = getBaseUrl() + "/contractor-builder/system-brain/posture-explanation?limit=500";
      const headers = getHeaders();

      try {
        const response = await fetch(url, {
          method: "GET",
          headers
        });

        const data = await response.json();

        if (!response.ok) {
          els.postureExplanation.textContent = pretty(data);
          els.postureReasons.textContent = "Posture explanation request failed.";
          return;
        }

        els.postureExplanation.textContent =
          data.plain_explanation || "No posture explanation returned.";

        els.postureReasons.textContent = pretty(data.reasons || []);
      } catch (error) {
        els.postureExplanation.textContent = "Posture explanation error: " + String(error);
        els.postureReasons.textContent = "Unavailable.";
      }
    }

    async function loadSystemBrain() {
      const url = getBaseUrl() + "/contractor-builder/system-brain/summary?limit=500";
      const headers = getHeaders();

      try {
        const response = await fetch(url, {
          method: "GET",
          headers
        });

        const data = await response.json();

        if (!response.ok) {
          els.systemBrainSummary.textContent = pretty(data);
          els.systemBrainCards.textContent = "System Brain request failed.";
          els.systemBrainWatch.textContent = "System Brain request failed.";
          await loadPostureExplanation();
          return;
        }

        els.systemBrainSummary.textContent =
          data.plain_summary || "No System Brain summary returned.";

        els.systemBrainCards.textContent = pretty(data.operator_cards || []);
        els.systemBrainWatch.textContent = pretty(data.what_to_watch || []);
        await loadPostureExplanation();
      } catch (error) {
        els.systemBrainSummary.textContent = "System Brain error: " + String(error);
        els.systemBrainCards.textContent = "Unavailable.";
        els.systemBrainWatch.textContent = "Unavailable.";
        await loadPostureExplanation();
      }
    }

    async function runLiveDashboard() {
      let body;
      try {
        body = JSON.parse(els.requestBody.value);
      } catch (error) {
        setStatus("Request JSON is invalid.", "bad");
        return;
      }

      const url = getBaseUrl() + "/contractor-builder/live/dashboard";
      const headers = getHeaders();

      els.runBtn.disabled = true;
      setStatus("Running live contractor dashboard...");
      try {
        const response = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok) {
          setStatus("Request failed.", "bad");
          els.watcherResult.textContent = pretty(data);
          await loadSystemBrain();
          return;
        }

        const watcher = data.watcher_result || {};
        const dashboard = data.dashboard_payload || {};
        const summary = dashboard.summary_panel || {};
        const projectPanel = dashboard.project_panel || {};
        const explanation = dashboard.explanation_panel || {};

        setStatus("Live contractor dashboard run completed.", "ok");
        setValue(els.cycleStatus, data.cycle_record?.cycle_status || "unknown", "ok");
        setValue(
          els.watcherStatus,
          watcher.valid ? "Valid" : "Invalid",
          watcher.valid ? "ok" : "bad"
        );
        setValue(
          els.projectName,
          projectPanel.project_name || summary.project_name || "Unnamed project",
          "ok"
        );

        if (summary.compliance_blocking === true) {
          setValue(els.complianceBlocking, "Blocked", "bad");
        } else if (summary.compliance_blocking === false) {
          setValue(els.complianceBlocking, "Not Blocked", "ok");
        } else {
          setValue(els.complianceBlocking, "Unknown", "warn");
        }

        els.operatorRead.textContent =
          explanation.operator_read || "No operator explanation returned.";
        els.watcherResult.textContent = pretty(watcher);
        els.visibilityPaths.textContent = pretty(data.visibility_paths || {});
        els.dashboardPayload.textContent = pretty(dashboard);

        populateSignoffFields(dashboard, body);
        setSignoffStatus(
          "Phase signoff fields populated from current dashboard state. Current status: " +
          (projectPanel.phase_signoff_status || "not_requested"),
          "ok"
        );

        await loadSystemBrain();
      } catch (error) {
        setStatus("Network or runtime error: " + String(error), "bad");
        await loadSystemBrain();
      } finally {
        els.runBtn.disabled = false;
      }
    }

    async function runPhaseSignoff() {
      const projectId = (els.signoffProjectId.value || "").trim();
      const phaseId = (els.signoffPhaseId.value || "").trim();
      const clientEmail = (els.signoffClientEmail.value || "").trim();

      if (!projectId || !phaseId || !clientEmail) {
        setSignoffStatus("Project ID, Phase ID, and Client Email are required.", "bad");
        return;
      }

      const url = getBaseUrl() + "/contractor-builder/phase-closeout/run";
      const headers = getHeaders();

      els.signoffBtn.disabled = true;
      setSignoffStatus("Sending phase closeout for signoff...");
      try {
        const response = await fetch(url, {
          method: "POST",
          headers,
          body: JSON.stringify({
            project_id: projectId,
            phase_id: phaseId,
            client_email: clientEmail,
            client_name: "Customer"
          })
        });

        const data = await response.json();

        if (!response.ok) {
          setSignoffStatus("Phase signoff request failed.", "bad");
          els.signoffResult.textContent = pretty(data);
          await loadSystemBrain();
          return;
        }

        setSignoffStatus("Phase closeout sent for signoff. Re-running dashboard...", "ok");
        els.signoffResult.textContent = pretty(data);

        await runLiveDashboard();
      } catch (error) {
        setSignoffStatus("Network or runtime error: " + String(error), "bad");
        await loadSystemBrain();
      } finally {
        els.signoffBtn.disabled = false;
      }
    }

    els.runBtn.addEventListener("click", runLiveDashboard);
    els.signoffBtn.addEventListener("click", runPhaseSignoff);

    loadSystemBrain();
    loadPostureExplanation();
  </script>
</body>
</html>
"""


@router.get("/contractor-dashboard", response_class=HTMLResponse)
def contractor_dashboard_ui() -> HTMLResponse:
    return HTMLResponse(content=HTML_PAGE)