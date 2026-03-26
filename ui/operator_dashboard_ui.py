from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter()


HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>AI_GO Operator Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {
      color-scheme: dark;
      --bg: #0b1020;
      --panel: #111831;
      --panel-2: #17203f;
      --border: #2a3563;
      --text: #eef2ff;
      --muted: #aeb8d6;
      --soft: #8b97bd;
      --good: #7ee787;
      --warn: #f2cc60;
      --bad: #ff7b72;
      --accent: #7aa2ff;
      --accent-2: #9b8cff;
      --shadow: rgba(0, 0, 0, 0.28);
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      background: linear-gradient(180deg, #0b1020 0%, #0f1530 100%);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }

    .shell {
      max-width: 1280px;
      margin: 0 auto;
      padding: 24px;
    }

    .hero {
      display: grid;
      gap: 12px;
      margin-bottom: 20px;
    }

    .eyebrow {
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .hero h1 {
      margin: 0;
      font-size: clamp(28px, 4vw, 42px);
      line-height: 1.05;
    }

    .hero p {
      margin: 0;
      color: var(--muted);
      max-width: 920px;
    }

    .layout {
      display: grid;
      grid-template-columns: 360px 1fr;
      gap: 20px;
      align-items: start;
    }

    @media (max-width: 980px) {
      .layout {
        grid-template-columns: 1fr;
      }
    }

    .panel {
      background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: 0 12px 30px var(--shadow);
    }

    .panel-inner {
      padding: 18px;
    }

    .panel h2,
    .panel h3 {
      margin: 0 0 10px 0;
      line-height: 1.15;
    }

    .panel h2 {
      font-size: 20px;
    }

    .panel h3 {
      font-size: 15px;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    .stack {
      display: grid;
      gap: 16px;
    }

    .field {
      display: grid;
      gap: 8px;
    }

    .field label {
      color: var(--muted);
      font-size: 13px;
      font-weight: 600;
    }

    .field input,
    .field select,
    .field textarea {
      width: 100%;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.03);
      color: var(--text);
      border-radius: 12px;
      padding: 12px 14px;
      font: inherit;
      outline: none;
    }

    .field textarea {
      min-height: 110px;
      resize: vertical;
    }

    .field input:focus,
    .field select:focus,
    .field textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(122, 162, 255, 0.18);
    }

    .helper {
      color: var(--soft);
      font-size: 12px;
    }

    .row-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    @media (max-width: 560px) {
      .row-2 {
        grid-template-columns: 1fr;
      }
    }

    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }

    button {
      border: 0;
      border-radius: 12px;
      padding: 12px 16px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.12s ease, opacity 0.12s ease;
    }

    button:hover {
      transform: translateY(-1px);
    }

    button:disabled {
      cursor: not-allowed;
      opacity: 0.6;
      transform: none;
    }

    .primary {
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
      color: white;
    }

    .secondary {
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
      border: 1px solid var(--border);
    }

    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }

    @media (max-width: 1100px) {
      .summary-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 600px) {
      .summary-grid {
        grid-template-columns: 1fr;
      }
    }

    .summary-card {
      background: rgba(255, 255, 255, 0.025);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      min-height: 118px;
    }

    .summary-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }

    .summary-value {
      font-size: 22px;
      font-weight: 800;
      line-height: 1.12;
      margin-bottom: 8px;
    }

    .summary-note {
      color: var(--muted);
      font-size: 13px;
    }

    .badge-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 4px;
    }

    .badge {
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.04em;
      border: 1px solid transparent;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      white-space: nowrap;
    }

    .badge-neutral {
      background: rgba(255, 255, 255, 0.05);
      border-color: var(--border);
      color: var(--text);
    }

    .badge-good {
      background: rgba(126, 231, 135, 0.14);
      border-color: rgba(126, 231, 135, 0.34);
      color: var(--good);
    }

    .badge-warn {
      background: rgba(242, 204, 96, 0.14);
      border-color: rgba(242, 204, 96, 0.34);
      color: var(--warn);
    }

    .badge-bad {
      background: rgba(255, 123, 114, 0.14);
      border-color: rgba(255, 123, 114, 0.34);
      color: var(--bad);
    }

    .section-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }

    @media (max-width: 900px) {
      .section-grid {
        grid-template-columns: 1fr;
      }
    }

    .section-card {
      background: rgba(255, 255, 255, 0.025);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 16px;
    }

    .kv {
      display: grid;
      grid-template-columns: minmax(120px, 160px) 1fr;
      gap: 8px 14px;
      align-items: start;
      margin-top: 10px;
    }

    .kv-key {
      color: var(--muted);
      font-size: 13px;
      font-weight: 700;
    }

    .kv-value {
      color: var(--text);
      min-width: 0;
      word-break: break-word;
    }

    .signal-list,
    .simple-list {
      display: grid;
      gap: 8px;
      margin-top: 12px;
    }

    .signal-item,
    .simple-item {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px 14px;
    }

    .signal-item strong,
    .simple-item strong {
      display: block;
      margin-bottom: 4px;
    }

    .highlight {
      border-left: 4px solid var(--accent);
      padding-left: 12px;
      margin-top: 10px;
      color: var(--text);
    }

    .risk-box,
    .empty-box,
    .error-box,
    .success-box {
      border-radius: 14px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      margin-top: 12px;
    }

    .risk-box {
      background: rgba(255, 123, 114, 0.08);
      border-color: rgba(255, 123, 114, 0.28);
    }

    .empty-box {
      background: rgba(255, 255, 255, 0.03);
    }

    .error-box {
      background: rgba(255, 123, 114, 0.08);
      border-color: rgba(255, 123, 114, 0.32);
      color: #ffd3cf;
    }

    .success-box {
      background: rgba(126, 231, 135, 0.08);
      border-color: rgba(126, 231, 135, 0.30);
      color: #d7ffe0;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .small {
      font-size: 12px;
      color: var(--muted);
    }

    .mono {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 12px;
    }

    .hidden {
      display: none !important;
    }

    details.debug {
      margin-top: 16px;
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      background: rgba(255, 255, 255, 0.025);
    }

    details.debug summary {
      cursor: pointer;
      padding: 14px 16px;
      font-weight: 700;
      color: var(--muted);
    }

    pre {
      margin: 0;
      padding: 16px;
      white-space: pre-wrap;
      word-break: break-word;
      overflow-x: auto;
      background: rgba(0, 0, 0, 0.18);
      color: #dbe5ff;
      border-top: 1px solid var(--border);
    }
  </style>
</head>
<body>
  <div class="shell">
    <section class="hero">
      <div class="eyebrow">AI_GO Operator Surface</div>
      <h1>Market Analyzer V1</h1>
      <p>
        Human-usable advisory surface for governed market analysis.
        This page preserves the canonical system_view contract while compressing cognition,
        PM workflow, and governance into clearer operator-facing signals.
      </p>
    </section>

    <div class="layout">
      <aside class="panel">
        <div class="panel-inner">
          <h2>Run Live Analysis</h2>
          <div class="stack">
            <div class="field">
              <label for="api_key">API Key</label>
              <input id="api_key" name="api_key" type="password" placeholder="Enter x-api-key value" />
              <div class="helper">Required for protected API routes. Stored only in this browser tab.</div>
            </div>

            <div class="field">
              <label for="request_id">Request ID</label>
              <input id="request_id" name="request_id" type="text" placeholder="live-case-001" />
              <div class="helper">Unique operator-visible request identifier.</div>
            </div>

            <div class="field">
              <label for="symbol">Symbol</label>
              <input id="symbol" name="symbol" type="text" placeholder="XLE" />
            </div>

            <div class="field">
              <label for="headline">Headline</label>
              <textarea id="headline" name="headline" placeholder="Energy rebound after necessity shock"></textarea>
            </div>

            <div class="row-2">
              <div class="field">
                <label for="price_change_pct">Price Change %</label>
                <input id="price_change_pct" name="price_change_pct" type="number" step="0.1" placeholder="2.4" />
              </div>
              <div class="field">
                <label for="sector">Sector</label>
                <select id="sector" name="sector">
                  <option value="energy">energy</option>
                  <option value="materials">materials</option>
                  <option value="utilities">utilities</option>
                  <option value="industrials">industrials</option>
                  <option value="technology">technology</option>
                  <option value="consumer_discretionary">consumer_discretionary</option>
                  <option value="financials">financials</option>
                  <option value="healthcare">healthcare</option>
                  <option value="communication_services">communication_services</option>
                  <option value="consumer_staples">consumer_staples</option>
                  <option value="real_estate">real_estate</option>
                </select>
              </div>
            </div>

            <div class="field">
              <label for="confirmation">Confirmation</label>
              <select id="confirmation" name="confirmation">
                <option value="confirmed">confirmed</option>
                <option value="partial">partial</option>
                <option value="missing">missing</option>
              </select>
            </div>

            <div class="actions">
              <button id="run_live_btn" class="primary" type="button">Run Live Route</button>
              <button id="load_sample_btn" class="secondary" type="button">Load Sample</button>
              <button id="clear_btn" class="secondary" type="button">Clear</button>
            </div>

            <div class="small">
              Calls the governed <span class="mono">/market-analyzer/run/live</span> endpoint and renders the
              unified <span class="mono">system_view</span> response without changing authority.
            </div>

            <div id="auth_hint" class="empty-box hidden"></div>
          </div>
        </div>
      </aside>

      <main class="panel">
        <div class="panel-inner">
          <div class="toolbar">
            <div>
              <h2>Operator System View</h2>
              <div class="small">Canonical outward response, compressed for human readability</div>
            </div>
            <div class="badge-row" id="top_badges"></div>
          </div>

          <div id="result_error" class="error-box hidden"></div>
          <div id="result_success" class="success-box hidden"></div>

          <div id="result_surface" class="hidden">
            <section class="summary-grid">
              <article class="summary-card">
                <div class="summary-label">Operator Insight</div>
                <div class="summary-value" id="summary_insight">No run yet</div>
                <div class="summary-note" id="summary_insight_note">Awaiting live route response.</div>
              </article>

              <article class="summary-card">
                <div class="summary-label">Recommendation</div>
                <div class="summary-value" id="summary_recommendation">None</div>
                <div class="summary-note" id="summary_recommendation_note">No recommendation generated.</div>
              </article>

              <article class="summary-card">
                <div class="summary-label">Workflow Status</div>
                <div class="summary-value" id="summary_status">Idle</div>
                <div class="summary-note" id="summary_next_step">No PM workflow yet.</div>
              </article>

              <article class="summary-card">
                <div class="summary-label">Governance State</div>
                <div class="summary-value" id="summary_governance">Unknown</div>
                <div class="summary-note" id="summary_governance_note">No governed response loaded.</div>
              </article>
            </section>

            <section class="section-grid">
              <article class="section-card">
                <h3>Case</h3>
                <div class="kv" id="case_section"></div>
              </article>

              <article class="section-card">
                <h3>Runtime</h3>
                <div class="kv" id="runtime_section"></div>
              </article>

              <article class="section-card">
                <h3>Recommendation</h3>
                <div id="recommendation_section"></div>
              </article>

              <article class="section-card">
                <h3>Cognition</h3>
                <div id="cognition_section"></div>
              </article>

              <article class="section-card">
                <h3>PM Workflow</h3>
                <div id="pm_workflow_section"></div>
              </article>

              <article class="section-card">
                <h3>Governance</h3>
                <div id="governance_section"></div>
              </article>
            </section>

            <details class="debug">
              <summary>Raw system_view</summary>
              <pre id="raw_json"></pre>
            </details>
          </div>
        </div>
      </main>
    </div>
  </div>

  <script>
    const endpoint = "/market-analyzer/run/live";
    const storageKey = "ai_go_operator_api_key";

    function el(id) {
      return document.getElementById(id);
    }

    function safeValue(value, fallback = "Not available") {
      if (value === null || value === undefined || value === "") {
        return fallback;
      }
      return String(value);
    }

    function titleCase(input) {
      return safeValue(input, "")
        .replace(/[_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim()
        .replace(/\b\w/g, (char) => char.toUpperCase()) || "Unknown";
    }

    function normalizeConfidence(value) {
      const raw = safeValue(value, "").toLowerCase();
      if (!raw) return "Unknown";
      if (["high", "strong", "reinforced_support"].includes(raw)) return "High";
      if (["medium", "moderate", "partial"].includes(raw)) return "Medium";
      if (["low", "weak", "down"].includes(raw)) return "Low";
      return titleCase(raw);
    }

    function confidenceClass(value) {
      const normalized = normalizeConfidence(value).toLowerCase();
      if (normalized === "high") return "badge-good";
      if (normalized === "medium") return "badge-warn";
      if (normalized === "low") return "badge-bad";
      return "badge-neutral";
    }

    function governanceText(governance) {
      const executionAllowed = !!(governance && governance.execution_allowed);
      const approvalRequired = !!(governance && governance.approval_required);
      const watcherPassed = governance && governance.watcher_passed;

      if (!executionAllowed && approvalRequired && watcherPassed === true) {
        return "Advisory Locked";
      }
      if (!executionAllowed && approvalRequired) {
        return "Approval Required";
      }
      if (!executionAllowed) {
        return "Execution Blocked";
      }
      return "Execution Allowed";
    }

    function buildKvRows(items) {
      return items.map(([key, value]) => {
        return `
          <div class="kv-key">${key}</div>
          <div class="kv-value">${safeValue(value)}</div>
        `;
      }).join("");
    }

    function renderBadges(root, badges) {
      root.innerHTML = badges.map((badge) => {
        return `<span class="badge ${badge.className}">${badge.text}</span>`;
      }).join("");
    }

    function deriveRecommendation(response) {
      const recommendationPanel = response.recommendation_panel || {};
      const recommendations = Array.isArray(recommendationPanel.recommendations)
        ? recommendationPanel.recommendations
        : [];

      const first = recommendations[0];
      if (!first) {
        return {
          title: "No recommendation",
          note: "The system did not produce a candidate recommendation.",
          confidence: "Unknown",
          detailHtml: `<div class="empty-box">No recommendation payload was returned.</div>`
        };
      }

      const symbol = safeValue(first.symbol, "Unknown Symbol");
      const entry = safeValue(first.entry, "No entry logic");
      const exit = safeValue(first.exit, "No exit logic");
      const confidence = normalizeConfidence(first.confidence);

      return {
        title: symbol,
        note: `${entry} to ${exit}`,
        confidence,
        detailHtml: `
          <div class="simple-list">
            <div class="simple-item">
              <strong>${symbol}</strong>
              <div>Entry: ${entry}</div>
              <div>Exit: ${exit}</div>
              <div class="badge-row" style="margin-top:10px;">
                <span class="badge ${confidenceClass(confidence)}">Confidence: ${confidence}</span>
              </div>
            </div>
          </div>
        `
      };
    }

    function deriveCognition(response) {
      const cognition = response.cognition_panel || response.refinement_panel || {};
      const signal = cognition.signal || cognition.primary_signal || null;
      const insight = cognition.insight || cognition.summary || cognition.narrative || null;
      const riskFlag = cognition.risk_flag || cognition.risk || null;
      const narrative = cognition.narrative || cognition.explanation || null;
      const adjustment = cognition.confidence_adjustment || cognition.adjustment || null;

      let operatorInsight = "No refinement insight";
      let operatorNote = "No cognition layer output was surfaced.";

      if (insight) {
        operatorInsight = insight;
        operatorNote = signal ? `Signal: ${titleCase(signal)}` : "Derived from bounded refinement output.";
      } else if (riskFlag) {
        operatorInsight = titleCase(riskFlag);
        operatorNote = "Risk surfaced without narrative expansion.";
      } else if (signal) {
        operatorInsight = titleCase(signal);
        operatorNote = "Signal surfaced without additional narrative.";
      }

      let html = "";
      if (insight) {
        html += `<div class="highlight">${safeValue(insight)}</div>`;
      }

      const listItems = [];
      if (signal) {
        listItems.push(`
          <div class="signal-item">
            <strong>Signal</strong>
            <div>${titleCase(signal)}</div>
          </div>
        `);
      }
      if (adjustment) {
        listItems.push(`
          <div class="signal-item">
            <strong>Confidence Adjustment</strong>
            <div>${titleCase(adjustment)}</div>
          </div>
        `);
      }
      if (narrative && narrative !== insight) {
        listItems.push(`
          <div class="signal-item">
            <strong>Narrative</strong>
            <div>${safeValue(narrative)}</div>
          </div>
        `);
      }
      if (listItems.length) {
        html += `<div class="signal-list">${listItems.join("")}</div>`;
      }
      if (riskFlag) {
        html += `<div class="risk-box"><strong>Risk</strong><div>${safeValue(riskFlag)}</div></div>`;
      }
      if (!html) {
        html = `<div class="empty-box">No cognition annotations were available.</div>`;
      }

      return {
        insight: operatorInsight,
        note: operatorNote,
        riskFlag: riskFlag,
        adjustment: adjustment,
        html
      };
    }

    function derivePmWorkflow(response) {
      const workflow = response.pm_workflow_panel || {};
      const dispatch = workflow.dispatch || workflow.dispatch_record || {};
      const queue = workflow.queue || workflow.queue_record || {};
      const planning = workflow.planning || workflow.planning_record || {};
      const review = workflow.review || workflow.review_record || {};
      const strategy = workflow.strategy || workflow.strategy_record || {};

      const status =
        dispatch.dispatch_class ||
        planning.next_step_class ||
        planning.plan_class ||
        review.review_class ||
        strategy.strategy_class ||
        "monitor";

      const nextStep =
        dispatch.dispatch_target ||
        queue.queue_target ||
        planning.next_step_class ||
        review.review_class ||
        strategy.strategy_class ||
        "await_more_information";

      const summary = `
        <div class="simple-list">
          <div class="simple-item">
            <strong>Status</strong>
            <div>${titleCase(status)}</div>
          </div>
          <div class="simple-item">
            <strong>Next Step</strong>
            <div>${titleCase(nextStep)}</div>
          </div>
        </div>
      `;

      const detailRows = [];
      if (strategy.strategy_class) detailRows.push(["Strategy", titleCase(strategy.strategy_class)]);
      if (review.review_class) detailRows.push(["Review", titleCase(review.review_class)]);
      if (planning.plan_class) detailRows.push(["Planning", titleCase(planning.plan_class)]);
      if (planning.next_step_class) detailRows.push(["Workflow Next", titleCase(planning.next_step_class)]);
      if (queue.queue_lane) detailRows.push(["Queue Lane", titleCase(queue.queue_lane)]);
      if (queue.queue_status) detailRows.push(["Queue Status", titleCase(queue.queue_status)]);
      if (dispatch.dispatch_class) detailRows.push(["Dispatch Class", titleCase(dispatch.dispatch_class)]);
      if (dispatch.dispatch_target) detailRows.push(["Dispatch Target", titleCase(dispatch.dispatch_target)]);

      const detailHtml = detailRows.length
        ? `<div class="kv" style="margin-top:14px;">${buildKvRows(detailRows)}</div>`
        : `<div class="empty-box">No PM workflow artifacts were returned.</div>`;

      return {
        status: titleCase(status),
        nextStep: `Next step: ${titleCase(nextStep)}`,
        html: summary + detailHtml
      };
    }

    function deriveGovernance(response) {
      const governance = response.governance_panel || {};
      const governanceState = governanceText(governance);
      const badges = [
        {
          text: governanceState,
          className: governance.execution_allowed ? "badge-good" : "badge-neutral"
        }
      ];

      badges.push({
        text: governance.approval_required ? "Approval Required" : "No Approval Gate",
        className: governance.approval_required ? "badge-warn" : "badge-neutral"
      });

      if (governance.watcher_passed === true) {
        badges.push({ text: "Watcher Passed", className: "badge-good" });
      } else if (governance.watcher_passed === false) {
        badges.push({ text: "Watcher Failed", className: "badge-bad" });
      }

      if (governance.requires_review === true) {
        badges.push({ text: "Review Required", className: "badge-warn" });
      }

      const detailRows = [
        ["Mode", safeValue(response.mode || governance.mode || "advisory")],
        ["Execution Allowed", governance.execution_allowed === true ? "true" : "false"],
        ["Approval Required", governance.approval_required === true ? "true" : "false"],
        ["Watcher Passed", governance.watcher_passed === true ? "true" : governance.watcher_passed === false ? "false" : "not_returned"],
        ["Requires Review", governance.requires_review === true ? "true" : "false"]
      ];

      if (governance.receipt_id) {
        detailRows.push(["Receipt ID", governance.receipt_id]);
      }
      if (governance.watcher_validation_id) {
        detailRows.push(["Watcher Validation ID", governance.watcher_validation_id]);
      }
      if (governance.closeout_id) {
        detailRows.push(["Closeout ID", governance.closeout_id]);
      }

      return {
        state: governanceState,
        note: governance.execution_allowed ? "Execution path enabled." : "Advisory posture preserved.",
        badges,
        html: `<div class="kv">${buildKvRows(detailRows)}</div>`
      };
    }

    function deriveRuntime(response) {
      const runtime = response.runtime_panel || response.market_panel || {};
      const casePanel = response.case_panel || {};

      return {
        caseHtml: buildKvRows([
          ["Case ID", casePanel.case_id || response.case_id || response.request_id],
          ["Title", casePanel.title || runtime.headline || response.headline],
          ["Observed At", casePanel.observed_at || response.observed_at || "not_returned"]
        ]),
        runtimeHtml: buildKvRows([
          ["Market Regime", titleCase(runtime.market_regime || response.market_regime || "unknown")],
          ["Event Theme", titleCase(runtime.event_theme || response.event_theme || "unknown")],
          ["Macro Bias", titleCase(runtime.macro_bias || response.macro_bias || "unknown")],
          ["Headline", runtime.headline || response.headline || "not_returned"]
        ])
      };
    }

    function compressSystemView(response) {
      const recommendation = deriveRecommendation(response);
      const cognition = deriveCognition(response);
      const workflow = derivePmWorkflow(response);
      const governance = deriveGovernance(response);
      const runtime = deriveRuntime(response);

      const topBadges = [
        { text: `Confidence: ${recommendation.confidence}`, className: confidenceClass(recommendation.confidence) },
        { text: governance.state, className: "badge-neutral" }
      ];

      if (cognition.riskFlag) {
        topBadges.push({ text: `Risk: ${titleCase(cognition.riskFlag)}`, className: "badge-bad" });
      }

      return {
        summary: {
          insight: cognition.insight,
          insightNote: cognition.note,
          recommendation: recommendation.title,
          recommendationNote: recommendation.note,
          status: workflow.status,
          nextStep: workflow.nextStep,
          governance: governance.state,
          governanceNote: governance.note
        },
        sections: {
          caseHtml: runtime.caseHtml,
          runtimeHtml: runtime.runtimeHtml,
          recommendationHtml: recommendation.detailHtml,
          cognitionHtml: cognition.html,
          workflowHtml: workflow.html,
          governanceHtml: governance.html
        },
        topBadges
      };
    }

    function renderResponse(response) {
      const compressed = compressSystemView(response);

      el("result_error").classList.add("hidden");
      el("result_success").classList.remove("hidden");
      el("result_success").innerHTML = "<strong>Request Succeeded</strong><div style='margin-top:6px;'>Governed live route returned a valid response.</div>";
      el("result_surface").classList.remove("hidden");

      el("summary_insight").textContent = compressed.summary.insight;
      el("summary_insight_note").textContent = compressed.summary.insightNote;
      el("summary_recommendation").textContent = compressed.summary.recommendation;
      el("summary_recommendation_note").textContent = compressed.summary.recommendationNote;
      el("summary_status").textContent = compressed.summary.status;
      el("summary_next_step").textContent = compressed.summary.nextStep;
      el("summary_governance").textContent = compressed.summary.governance;
      el("summary_governance_note").textContent = compressed.summary.governanceNote;

      el("case_section").innerHTML = compressed.sections.caseHtml;
      el("runtime_section").innerHTML = compressed.sections.runtimeHtml;
      el("recommendation_section").innerHTML = compressed.sections.recommendationHtml;
      el("cognition_section").innerHTML = compressed.sections.cognitionHtml;
      el("pm_workflow_section").innerHTML = compressed.sections.workflowHtml;
      el("governance_section").innerHTML = compressed.sections.governanceHtml;
      el("raw_json").textContent = JSON.stringify(response, null, 2);

      renderBadges(el("top_badges"), compressed.topBadges);
    }

    function renderError(message, detail = "") {
      el("result_surface").classList.add("hidden");
      el("result_success").classList.add("hidden");
      const box = el("result_error");
      box.classList.remove("hidden");
      box.innerHTML = `
        <strong>Request Failed</strong>
        <div style="margin-top:6px;">${safeValue(message)}</div>
        ${detail ? `<div class="small" style="margin-top:8px;">${safeValue(detail)}</div>` : ""}
      `;
    }

    function showAuthHint(message) {
      const hint = el("auth_hint");
      hint.classList.remove("hidden");
      hint.innerHTML = `<strong>Auth Required</strong><div style="margin-top:6px;">${message}</div>`;
    }

    function hideAuthHint() {
      el("auth_hint").classList.add("hidden");
      el("auth_hint").innerHTML = "";
    }

    function buildPayload() {
      const requestId = el("request_id").value.trim();
      const symbol = el("symbol").value.trim();
      const headline = el("headline").value.trim();
      const priceChange = el("price_change_pct").value;
      const sector = el("sector").value;
      const confirmation = el("confirmation").value;

      return {
        request_id: requestId,
        symbol: symbol,
        headline: headline,
        price_change_pct: priceChange === "" ? null : Number(priceChange),
        sector: sector,
        confirmation: confirmation
      };
    }

    function getApiKey() {
      return el("api_key").value.trim();
    }

    function saveApiKeyToSession(apiKey) {
      try {
        sessionStorage.setItem(storageKey, apiKey);
      } catch (_) {
        // ignore storage errors
      }
    }

    function loadApiKeyFromSession() {
      try {
        const saved = sessionStorage.getItem(storageKey);
        if (saved) {
          el("api_key").value = saved;
        }
      } catch (_) {
        // ignore storage errors
      }
    }

    function loadSample() {
      el("request_id").value = "live-energy-001";
      el("symbol").value = "XLE";
      el("headline").value = "Energy rebound after necessity shock";
      el("price_change_pct").value = "2.4";
      el("sector").value = "energy";
      el("confirmation").value = "confirmed";
    }

    function clearForm() {
      el("request_id").value = "";
      el("symbol").value = "";
      el("headline").value = "";
      el("price_change_pct").value = "";
      el("sector").value = "energy";
      el("confirmation").value = "confirmed";
      el("result_surface").classList.add("hidden");
      el("result_error").classList.add("hidden");
      el("result_success").classList.add("hidden");
      el("raw_json").textContent = "";
      el("top_badges").innerHTML = "";
      hideAuthHint();
    }

    async function runLiveRoute() {
      const button = el("run_live_btn");
      button.disabled = true;
      button.textContent = "Running...";
      hideAuthHint();

      try {
        const apiKey = getApiKey();
        if (!apiKey) {
          showAuthHint("Enter your API key before running the protected live route.");
          renderError("Missing API key", "Provide the x-api-key value in the API Key field.");
          return;
        }

        saveApiKeyToSession(apiKey);

        const payload = buildPayload();

        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "x-api-key": apiKey
          },
          body: JSON.stringify(payload)
        });

        const text = await response.text();
        let data = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch (_) {
          data = { error: "non_json_response", detail: text };
        }

        if (!response.ok) {
          if (response.status === 401) {
            showAuthHint("The API rejected the current key. Check the value and try again.");
          }
          renderError(data.detail || data.error || `HTTP ${response.status}`, text);
          return;
        }

        renderResponse(data);
      } catch (error) {
        renderError("Network or runtime error", error && error.message ? error.message : String(error));
      } finally {
        button.disabled = false;
        button.textContent = "Run Live Route";
      }
    }

    el("run_live_btn").addEventListener("click", runLiveRoute);
    el("load_sample_btn").addEventListener("click", loadSample);
    el("clear_btn").addEventListener("click", clearForm);

    loadApiKeyFromSession();
    loadSample();
  </script>
</body>
</html>
"""


@router.get("/operator", response_class=HTMLResponse)
def operator_dashboard_page() -> HTMLResponse:
    return HTMLResponse(content=HTML_PAGE)

