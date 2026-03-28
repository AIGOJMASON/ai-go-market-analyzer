from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


def _page_html() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>AI_GO Operator</title>
  <style>
    :root {
      --bg: #0f1115;
      --panel: #171a21;
      --panel-soft: #1d222b;
      --border: #2b3340;
      --text: #e8edf5;
      --muted: #97a3b6;
      --good: #6dd3a8;
      --warn: #f0c674;
      --bad: #ef6b73;
      --accent: #7aa2ff;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      padding: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
      line-height: 1.45;
    }

    .shell {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px 18px 40px;
    }

    .header {
      margin-bottom: 20px;
    }

    .title {
      margin: 0 0 6px;
      font-size: 28px;
      font-weight: 700;
    }

    .subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 14px;
    }

    .layout {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 18px;
      align-items: start;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }

    .panel-head {
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
      background: var(--panel-soft);
      font-weight: 700;
      letter-spacing: 0.02em;
    }

    .panel-body {
      padding: 16px;
    }

    .field {
      margin-bottom: 14px;
    }

    .field:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    input,
    select,
    textarea,
    button {
      width: 100%;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: #11151b;
      color: var(--text);
      padding: 11px 12px;
      font-size: 14px;
    }

    textarea {
      min-height: 92px;
      resize: vertical;
    }

    .button-row {
      display: flex;
      gap: 10px;
      margin-top: 18px;
    }

    .button-row button {
      cursor: pointer;
      font-weight: 700;
    }

    .button-primary {
      background: var(--accent);
      color: #0b1020;
      border-color: var(--accent);
    }

    .button-secondary {
      background: #121822;
      color: var(--text);
    }

    .stack {
      display: grid;
      gap: 14px;
    }

    .decision-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      min-height: 160px;
    }

    .card.span-2 {
      grid-column: span 2;
    }

    .card-head {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      background: var(--panel-soft);
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.04em;
    }

    .card-body {
      padding: 14px;
    }

    .muted {
      color: var(--muted);
    }

    .big {
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 6px;
    }

    .kv {
      display: grid;
      gap: 8px;
    }

    .kv-row {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      padding: 8px 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }

    .kv-row:last-child {
      border-bottom: none;
    }

    .kv-key {
      color: var(--muted);
      font-size: 13px;
      min-width: 120px;
    }

    .kv-value {
      text-align: right;
      font-weight: 700;
      word-break: break-word;
    }

    .badge-row {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid var(--border);
      background: #121822;
      color: var(--text);
    }

    .badge.good {
      color: var(--good);
      border-color: rgba(109, 211, 168, 0.35);
      background: rgba(109, 211, 168, 0.08);
    }

    .badge.warn {
      color: var(--warn);
      border-color: rgba(240, 198, 116, 0.35);
      background: rgba(240, 198, 116, 0.08);
    }

    .badge.bad {
      color: var(--bad);
      border-color: rgba(239, 107, 115, 0.35);
      background: rgba(239, 107, 115, 0.08);
    }

    .notice {
      margin-bottom: 14px;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: #121822;
      color: var(--muted);
    }

    .notice.error {
      border-color: rgba(239, 107, 115, 0.4);
      background: rgba(239, 107, 115, 0.08);
      color: #ffd7da;
    }

    details {
      border-top: 1px solid var(--border);
      margin-top: 8px;
      padding-top: 10px;
    }

    summary {
      cursor: pointer;
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    pre {
      margin: 12px 0 0;
      padding: 12px;
      border-radius: 10px;
      background: #0b0f14;
      border: 1px solid var(--border);
      color: #d7e0ef;
      overflow: auto;
      font-size: 12px;
    }

    @media (max-width: 980px) {
      .layout {
        grid-template-columns: 1fr;
      }

      .decision-grid {
        grid-template-columns: 1fr;
      }

      .card.span-2 {
        grid-column: span 1;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="header">
      <h1 class="title">AI_GO Operator Dashboard</h1>
      <p class="subtitle">
        One governed decision surface for live analyzer intake. This page compresses governed output into
        signal, why it matters, recommendation, risk, and status.
      </p>
    </div>

    <div class="layout">
      <section class="panel">
        <div class="panel-head">Live Analysis Input</div>
        <div class="panel-body">
          <div id="message" class="notice">
            Ready. Submit a live bounded case to <code>/market-analyzer/run/live</code>.
          </div>

          <form id="run-form">
            <div class="field">
              <label for="api-key">API Key</label>
              <input id="api-key" name="apiKey" type="password" placeholder="Enter API key" />
            </div>

            <div class="field">
              <label for="request-id">Request ID</label>
              <input id="request-id" name="requestId" type="text" value="ui-live-001" />
            </div>

            <div class="field">
              <label for="symbol">Symbol</label>
              <input id="symbol" name="symbol" type="text" value="XLE" />
            </div>

            <div class="field">
              <label for="headline">Headline</label>
              <textarea id="headline" name="headline">Energy rebound after necessity shock</textarea>
            </div>

            <div class="field">
              <label for="price-change-pct">Price Change %</label>
              <input id="price-change-pct" name="priceChangePct" type="number" step="0.1" value="2.4" />
            </div>

            <div class="field">
              <label for="sector">Sector</label>
              <select id="sector" name="sector">
                <option value="energy" selected>energy</option>
                <option value="materials">materials</option>
                <option value="industrials">industrials</option>
                <option value="utilities">utilities</option>
                <option value="healthcare">healthcare</option>
                <option value="technology">technology</option>
                <option value="consumer">consumer</option>
              </select>
            </div>

            <div class="field">
              <label for="confirmation">Confirmation</label>
              <select id="confirmation" name="confirmation">
                <option value="confirmed" selected>confirmed</option>
                <option value="partial">partial</option>
                <option value="missing">missing</option>
              </select>
            </div>

            <div class="button-row">
              <button class="button-primary" type="submit">Run Analysis</button>
              <button class="button-secondary" type="button" id="reset-button">Reset Form</button>
            </div>
          </form>
        </div>
      </section>

      <section class="stack">
        <div class="decision-grid">
          <article class="card">
            <div class="card-head">SIGNAL</div>
            <div class="card-body" id="card-signal">
              <div class="muted">Waiting for analysis.</div>
            </div>
          </article>

          <article class="card">
            <div class="card-head">WHY IT MATTERS</div>
            <div class="card-body" id="card-why">
              <div class="muted">No refinement insight yet.</div>
            </div>
          </article>

          <article class="card">
            <div class="card-head">RECOMMENDATION</div>
            <div class="card-body" id="card-recommendation">
              <div class="muted">No recommendation yet.</div>
            </div>
          </article>

          <article class="card">
            <div class="card-head">RISK</div>
            <div class="card-body" id="card-risk">
              <div class="muted">No governance state yet.</div>
            </div>
          </article>

          <article class="card span-2">
            <div class="card-head">STATUS</div>
            <div class="card-body" id="card-status">
              <div class="muted">No workflow status yet.</div>
            </div>
          </article>

          <article class="card span-2">
            <div class="card-head">RAW RESPONSE</div>
            <div class="card-body">
              <details>
                <summary>Show canonical response</summary>
                <pre id="raw-response">{}</pre>
              </details>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>

  <script>
    function text(value, fallback = "—") {
      if (value === null || value === undefined || value === "") {
        return fallback;
      }
      return String(value);
    }

    function safeArray(value) {
      return Array.isArray(value) ? value : [];
    }

    function confidenceBadge(value) {
      const normalized = String(value || "").toLowerCase();
      if (normalized === "high") return "good";
      if (normalized === "medium") return "warn";
      if (normalized === "low") return "bad";
      return "";
    }

    function classForBool(value, truthyClass = "good", falsyClass = "warn") {
      return value ? truthyClass : falsyClass;
    }

    function deriveWorkflowStatus(data) {
      const workflow = data.pm_workflow || data.workflow_panel || null;
      const queue = workflow?.queue || workflow?.queue_record || null;
      const dispatch = workflow?.dispatch || workflow?.dispatch_record || null;
      const review = workflow?.review || workflow?.review_record || null;
      const planning = workflow?.planning || workflow?.planning_record || null;

      return {
        reviewClass: review?.review_class || data.review_class || null,
        planClass: planning?.plan_class || data.plan_class || null,
        queueLane: queue?.queue_lane || data.queue_lane || null,
        queueStatus: queue?.queue_status || data.queue_status || null,
        dispatchClass: dispatch?.dispatch_class || data.dispatch_class || null,
        dispatchTarget: dispatch?.dispatch_target || data.dispatch_target || null
      };
    }

    function transformSystemView(data) {
      const casePanel = data.case_panel || {};
      const marketPanel = data.market_panel || {};
      const recommendationPanel = data.recommendation_panel || {};
      const governancePanel = data.governance_panel || {};
      const refinementPanel = data.refinement_panel || {};
      const recommendations = safeArray(recommendationPanel.recommendations);
      const recommendation = recommendations.length > 0 ? recommendations[0] : null;
      const workflow = deriveWorkflowStatus(data);

      return {
        signal: {
          title: casePanel.title || marketPanel.headline || "No case title",
          headline: marketPanel.headline || casePanel.title || "No headline",
          symbol: recommendation?.symbol || data.symbol || null,
          theme: marketPanel.event_theme || null,
          regime: marketPanel.market_regime || null,
          macroBias: marketPanel.macro_bias || null
        },
        why: {
          insight: refinementPanel.insight || null,
          narrative: refinementPanel.narrative || null,
          signal: refinementPanel.signal || null
        },
        recommendation: recommendation
          ? {
              symbol: recommendation.symbol || null,
              entry: recommendation.entry || null,
              exit: recommendation.exit || null,
              confidence: recommendation.confidence || null
            }
          : null,
        risk: {
          confidence: recommendation?.confidence || null,
          approvalRequired: governancePanel.approval_required ?? data.approval_required ?? null,
          executionAllowed: governancePanel.execution_allowed ?? data.execution_allowed ?? null,
          watcherPassed: governancePanel.watcher_passed ?? null,
          riskFlag: refinementPanel.risk_flag || null,
          requiresReview: data.requires_review ?? null
        },
        status: {
          mode: data.mode || null,
          routeMode: data.route_mode || null,
          closeoutStatus: data.closeout_status || null,
          reviewClass: workflow.reviewClass,
          planClass: workflow.planClass,
          queueLane: workflow.queueLane,
          queueStatus: workflow.queueStatus,
          dispatchClass: workflow.dispatchClass,
          dispatchTarget: workflow.dispatchTarget
        }
      };
    }

    function renderBadges(container, items) {
      const filtered = items.filter(item => item && item.value);
      if (!filtered.length) {
        container.innerHTML = '<div class="muted">No additional signal context.</div>';
        return;
      }

      const html = filtered.map(item => {
        const cls = item.className ? `badge ${item.className}` : 'badge';
        return `<span class="${cls}">${item.label}: ${item.value}</span>`;
      }).join("");

      container.innerHTML = `<div class="badge-row">${html}</div>`;
    }

    function renderSignal(view) {
      const el = document.getElementById("card-signal");
      el.innerHTML = `
        <div class="big">${text(view.signal.title)}</div>
        <div class="muted" style="margin-bottom: 12px;">${text(view.signal.headline)}</div>
        <div id="signal-badges"></div>
      `;

      renderBadges(document.getElementById("signal-badges"), [
        { label: "Symbol", value: text(view.signal.symbol, "") },
        { label: "Theme", value: text(view.signal.theme, "") },
        { label: "Regime", value: text(view.signal.regime, "") },
        { label: "Macro Bias", value: text(view.signal.macroBias, "") }
      ]);
    }

    function renderWhy(view) {
      const el = document.getElementById("card-why");
      const insight = view.why.insight ? `<div style="margin-bottom:10px;"><strong>Insight:</strong> ${text(view.why.insight)}</div>` : "";
      const narrative = view.why.narrative ? `<div>${text(view.why.narrative)}</div>` : '<div class="muted">No refinement narrative returned.</div>';
      const signal = view.why.signal ? `<div class="muted" style="margin-top:10px;">Refinement signal: ${text(view.why.signal)}</div>` : "";
      el.innerHTML = `${insight}${narrative}${signal}`;
    }

    function renderRecommendation(view) {
      const el = document.getElementById("card-recommendation");

      if (!view.recommendation) {
        el.innerHTML = '<div class="muted">No recommendation returned.</div>';
        return;
      }

      el.innerHTML = `
        <div class="kv">
          <div class="kv-row">
            <div class="kv-key">Symbol</div>
            <div class="kv-value">${text(view.recommendation.symbol)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Entry</div>
            <div class="kv-value">${text(view.recommendation.entry)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Exit</div>
            <div class="kv-value">${text(view.recommendation.exit)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Confidence</div>
            <div class="kv-value">
              <span class="badge ${confidenceBadge(view.recommendation.confidence)}">${text(view.recommendation.confidence)}</span>
            </div>
          </div>
        </div>
      `;
    }

    function renderRisk(view) {
      const el = document.getElementById("card-risk");
      const approvalClass = classForBool(view.risk.approvalRequired === true, "warn", "good");
      const executionClass = classForBool(view.risk.executionAllowed === true, "bad", "good");
      const watcherClass = classForBool(view.risk.watcherPassed === true, "good", "warn");
      const reviewClass = classForBool(view.risk.requiresReview === true, "warn", "good");

      el.innerHTML = `
        <div class="badge-row" style="margin-bottom:12px;">
          <span class="badge ${confidenceBadge(view.risk.confidence)}">Confidence: ${text(view.risk.confidence)}</span>
          <span class="badge ${approvalClass}">Approval Required: ${text(view.risk.approvalRequired)}</span>
          <span class="badge ${executionClass}">Execution Allowed: ${text(view.risk.executionAllowed)}</span>
          <span class="badge ${watcherClass}">Watcher Passed: ${text(view.risk.watcherPassed)}</span>
          <span class="badge ${reviewClass}">Requires Review: ${text(view.risk.requiresReview)}</span>
        </div>
        <div>${view.risk.riskFlag ? `<strong>Risk Flag:</strong> ${text(view.risk.riskFlag)}` : '<span class="muted">No explicit refinement risk flag.</span>'}</div>
      `;
    }

    function renderStatus(view) {
      const el = document.getElementById("card-status");
      el.innerHTML = `
        <div class="kv">
          <div class="kv-row">
            <div class="kv-key">Mode</div>
            <div class="kv-value">${text(view.status.mode)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Route Mode</div>
            <div class="kv-value">${text(view.status.routeMode)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Review Class</div>
            <div class="kv-value">${text(view.status.reviewClass)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Plan Class</div>
            <div class="kv-value">${text(view.status.planClass)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Queue Lane</div>
            <div class="kv-value">${text(view.status.queueLane)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Queue Status</div>
            <div class="kv-value">${text(view.status.queueStatus)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Dispatch Class</div>
            <div class="kv-value">${text(view.status.dispatchClass)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Dispatch Target</div>
            <div class="kv-value">${text(view.status.dispatchTarget)}</div>
          </div>
          <div class="kv-row">
            <div class="kv-key">Closeout</div>
            <div class="kv-value">${text(view.status.closeoutStatus)}</div>
          </div>
        </div>
      `;
    }

    function setMessage(message, isError = false) {
      const el = document.getElementById("message");
      el.textContent = message;
      el.className = isError ? "notice error" : "notice";
    }

    function resetOutput() {
      document.getElementById("card-signal").innerHTML = '<div class="muted">Waiting for analysis.</div>';
      document.getElementById("card-why").innerHTML = '<div class="muted">No refinement insight yet.</div>';
      document.getElementById("card-recommendation").innerHTML = '<div class="muted">No recommendation yet.</div>';
      document.getElementById("card-risk").innerHTML = '<div class="muted">No governance state yet.</div>';
      document.getElementById("card-status").innerHTML = '<div class="muted">No workflow status yet.</div>';
      document.getElementById("raw-response").textContent = "{}";
    }

    async function runAnalysis(payload, apiKey) {
      const response = await fetch("/market-analyzer/run/live", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": apiKey
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        const message = data?.detail || data?.message || "Request failed.";
        throw new Error(message);
      }

      return data;
    }

    document.getElementById("run-form").addEventListener("submit", async (event) => {
      event.preventDefault();

      const apiKey = document.getElementById("api-key").value.trim();
      if (!apiKey) {
        setMessage("API key required for analyzer execution.", true);
        return;
      }

      const payload = {
        request_id: document.getElementById("request-id").value.trim(),
        symbol: document.getElementById("symbol").value.trim(),
        headline: document.getElementById("headline").value.trim(),
        price_change_pct: Number(document.getElementById("price-change-pct").value),
        sector: document.getElementById("sector").value,
        confirmation: document.getElementById("confirmation").value
      };

      setMessage("Running governed live analysis...");
      resetOutput();

      try {
        const data = await runAnalysis(payload, apiKey);
        const view = transformSystemView(data);

        renderSignal(view);
        renderWhy(view);
        renderRecommendation(view);
        renderRisk(view);
        renderStatus(view);

        document.getElementById("raw-response").textContent = JSON.stringify(data, null, 2);
        setMessage("Analysis complete.");
      } catch (error) {
        setMessage(error.message || "Request failed.", true);
      }
    });

    document.getElementById("reset-button").addEventListener("click", () => {
      document.getElementById("run-form").reset();
      document.getElementById("request-id").value = "ui-live-001";
      document.getElementById("symbol").value = "XLE";
      document.getElementById("headline").value = "Energy rebound after necessity shock";
      document.getElementById("price-change-pct").value = "2.4";
      document.getElementById("sector").value = "energy";
      document.getElementById("confirmation").value = "confirmed";
      setMessage("Form reset.");
      resetOutput();
    });
  </script>
</body>
</html>
"""


@router.get("/operator", response_class=HTMLResponse)
def operator_dashboard_ui() -> HTMLResponse:
    return HTMLResponse(content=_page_html())