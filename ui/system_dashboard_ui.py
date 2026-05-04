from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["system-dashboard-ui"])


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>AI_GO System Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
        :root {
            color-scheme: dark;
            --bg: #0d1117;
            --panel: #161b22;
            --panel-2: #1f2630;
            --line: #30363d;
            --text: #e6edf3;
            --muted: #8b949e;
            --ok: #3fb950;
            --warn: #d29922;
            --bad: #f85149;
            --blue: #58a6ff;
        }
        * { box-sizing: border-box; }
        body { margin: 0; background: var(--bg); color: var(--text); font-family: Arial, Helvetica, sans-serif; }
        header { padding: 20px 24px; border-bottom: 1px solid var(--line); background: var(--panel); }
        h1 { margin: 0 0 8px 0; font-size: 24px; }
        .sub { color: var(--muted); font-size: 14px; }
        .actions { margin-top: 14px; display: flex; gap: 10px; flex-wrap: wrap; }
        button { background: var(--panel-2); color: var(--text); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; cursor: pointer; }
        button:hover { border-color: var(--blue); }
        main { padding: 20px 24px 40px; display: grid; grid-template-columns: repeat(12, 1fr); gap: 16px; }
        .card { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 16px; }
        .span-12 { grid-column: span 12; }
        .span-8 { grid-column: span 8; }
        .span-6 { grid-column: span 6; }
        .span-4 { grid-column: span 4; }
        .span-3 { grid-column: span 3; }
        @media (max-width: 1100px) { .span-8, .span-6, .span-4, .span-3 { grid-column: span 12; } }
        .label { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; }
        .value { font-size: 22px; font-weight: 700; }
        .mono { font-family: Consolas, Menlo, Monaco, monospace; font-size: 13px; white-space: pre-wrap; word-break: break-word; }
        .pill { display: inline-block; padding: 3px 8px; border-radius: 999px; border: 1px solid var(--line); font-size: 12px; margin-right: 6px; margin-bottom: 6px; }
        .ok { color: var(--ok); }
        .warn { color: var(--warn); }
        .bad { color: var(--bad); }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); vertical-align: top; }
        th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; }
        .tiny { color: var(--muted); font-size: 12px; }
        .footer { margin-top: 10px; color: var(--muted); font-size: 12px; }
    </style>
</head>
<body>
    <header>
        <h1>AI_GO System Dashboard</h1>
        <div class="sub">Read-only operator surface for cycle state, Eyes packet, continuity/refinement posture, and live trigger activity.</div>
        <div class="actions">
            <button onclick="refreshAll()">Refresh now</button>
            <button onclick="toggleAutoRefresh()" id="auto-refresh-btn">Auto refresh: on</button>
        </div>
        <div class="footer" id="page-status">Loading…</div>
    </header>

    <main>
        <section class="card span-3"><div class="label">Latest cycle</div><div class="value mono" id="latest-cycle-id">—</div></section>
        <section class="card span-3"><div class="label">Cycle status</div><div class="value" id="latest-cycle-status">—</div></section>
        <section class="card span-3"><div class="label">Eyes generated</div><div class="value mono" id="eyes-generated-at">—</div></section>
        <section class="card span-3"><div class="label">System status</div><div class="value" id="system-status">—</div></section>

        <section class="card span-6"><div class="label">Step statuses</div><div id="step-statuses"></div></section>
        <section class="card span-6"><div class="label">Active child cores</div><div id="active-child-cores"></div></section>

        <section class="card span-4">
            <div class="label">Runtime</div>
            <table><tbody>
                <tr><th>Runtime status</th><td id="runtime-status">—</td></tr>
                <tr><th>Current stage</th><td id="current-stage">—</td></tr>
                <tr><th>Continuity status</th><td id="continuity-status">—</td></tr>
                <tr><th>Pressure</th><td id="continuity-pressure">—</td></tr>
            </tbody></table>
        </section>

        <section class="card span-4">
            <div class="label">Counts</div>
            <table><tbody>
                <tr><th>Child cores</th><td id="active-child-core-count">—</td></tr>
                <tr><th>Recent failures</th><td id="recent-failure-count">—</td></tr>
                <tr><th>Watcher failures</th><td id="recent-watcher-failures">—</td></tr>
            </tbody></table>
        </section>

        <section class="card span-4">
            <div class="label">Cycle timing</div>
            <table><tbody>
                <tr><th>Started</th><td class="mono" id="latest-started-at">—</td></tr>
                <tr><th>Ended</th><td class="mono" id="latest-ended-at">—</td></tr>
            </tbody></table>
        </section>

        <section class="card span-8">
            <div class="label">Live trigger</div>
            <table><tbody>
                <tr><th>Status</th><td id="live-trigger-status">—</td></tr>
                <tr><th>Last request id</th><td class="mono" id="live-trigger-last-request-id">—</td></tr>
                <tr><th>Last triggered at</th><td class="mono" id="live-trigger-last-triggered-at">—</td></tr>
                <tr><th>Last HTTP status</th><td id="live-trigger-last-http-status">—</td></tr>
                <tr><th>Target URL</th><td class="mono" id="live-trigger-last-target-url">—</td></tr>
            </tbody></table>
        </section>

        <section class="card span-4">
            <div class="label">Live trigger counts</div>
            <table><tbody>
                <tr><th>Total triggers</th><td id="live-trigger-total-triggers">—</td></tr>
                <tr><th>Total successes</th><td id="live-trigger-total-successes">—</td></tr>
                <tr><th>Total failures</th><td id="live-trigger-total-failures">—</td></tr>
            </tbody></table>
        </section>

        <section class="card span-12">
            <div class="label">Artifact metadata</div>
            <table>
                <thead><tr><th>Artifact</th><th>Exists</th><th>Modified at</th><th>Size</th><th>Path</th></tr></thead>
                <tbody id="artifact-meta-table"></tbody>
            </table>
        </section>

        <section class="card span-12">
            <div class="label">Eyes summary</div>
            <div class="mono" id="eyes-summary-json">—</div>
        </section>
    </main>

    <script>
        let autoRefreshEnabled = true;
        let refreshTimer = null;

        function statusClass(value) {
            const text = String(value || "").toLowerCase();
            if (text.includes("ok") || text.includes("healthy") || text.includes("stable") || text.includes("running") || text.includes("active")) return "ok";
            if (text.includes("warn") || text.includes("degraded") || text.includes("pending") || text.includes("skipped")) return "warn";
            if (text.includes("error") || text.includes("fail") || text.includes("bad") || text.includes("missing")) return "bad";
            return "";
        }

        function pill(text) {
            const cls = statusClass(text);
            return `<span class="pill ${cls}">${text}</span>`;
        }

        function setText(id, value) {
            const el = document.getElementById(id);
            el.textContent = value ?? "—";
            el.className = `value ${statusClass(value)}`.trim();
        }

        function setPlainText(id, value) {
            document.getElementById(id).textContent = value ?? "—";
        }

        function renderPills(id, values) {
            const el = document.getElementById(id);
            if (!Array.isArray(values) || values.length === 0) {
                el.innerHTML = '<span class="tiny">none</span>';
                return;
            }
            el.innerHTML = values.map(v => pill(v)).join("");
        }

        function renderStepStatuses(stepStatuses) {
            const el = document.getElementById("step-statuses");
            const entries = Object.entries(stepStatuses || {});
            if (entries.length === 0) {
                el.innerHTML = '<span class="tiny">no step statuses</span>';
                return;
            }
            el.innerHTML = entries.map(([key, value]) => `<span class="pill ${statusClass(value)}">${key}: ${value}</span>`).join("");
        }

        function renderArtifactTable(artifacts) {
            const tbody = document.getElementById("artifact-meta-table");
            const rows = Object.entries(artifacts || {}).map(([name, info]) => {
                const meta = info.meta || {};
                return `
                    <tr>
                        <td>${name}</td>
                        <td>${meta.exists ? "yes" : "no"}</td>
                        <td class="mono">${meta.modified_at || "—"}</td>
                        <td>${meta.size_bytes ?? "—"}</td>
                        <td class="mono">${meta.path || "—"}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = rows.length ? rows.join("") : '<tr><td colspan="5">No artifact metadata available.</td></tr>';
        }

        async function fetchJson(url) {
            const response = await fetch(url, { cache: "no-store" });
            if (!response.ok) throw new Error(`${url} returned ${response.status}`);
            return response.json();
        }

        async function refreshAll() {
            const pageStatus = document.getElementById("page-status");
            pageStatus.textContent = "Refreshing…";

            try {
                const [summary, state] = await Promise.all([
                    fetchJson("/system/summary"),
                    fetchJson("/system/state"),
                ]);

                setPlainText("latest-cycle-id", summary.latest_cycle_id);
                setText("latest-cycle-status", summary.latest_cycle_status);
                setPlainText("eyes-generated-at", summary.eyes_generated_at);
                setText("system-status", summary.system_status);

                setPlainText("runtime-status", summary.runtime_status);
                setPlainText("current-stage", summary.current_stage);
                setPlainText("continuity-status", summary.continuity_status);
                setPlainText("continuity-pressure", summary.continuity_pressure);

                setPlainText("active-child-core-count", summary.active_child_core_count);
                setPlainText("recent-failure-count", summary.recent_failure_count);
                setPlainText("recent-watcher-failures", summary.recent_watcher_failures);

                setPlainText("latest-started-at", summary.latest_started_at);
                setPlainText("latest-ended-at", summary.latest_ended_at);

                setPlainText("live-trigger-status", summary.live_trigger_status);
                setPlainText("live-trigger-last-request-id", summary.live_trigger_last_request_id);
                setPlainText("live-trigger-last-triggered-at", summary.live_trigger_last_triggered_at);
                setPlainText("live-trigger-last-http-status", summary.live_trigger_last_http_status);
                setPlainText("live-trigger-last-target-url", summary.live_trigger_last_target_url);
                setPlainText("live-trigger-total-triggers", summary.live_trigger_total_triggers);
                setPlainText("live-trigger-total-successes", summary.live_trigger_total_successes);
                setPlainText("live-trigger-total-failures", summary.live_trigger_total_failures);

                renderStepStatuses(summary.step_statuses);
                renderPills("active-child-cores", summary.active_child_cores);

                const eyesPayload = state.artifacts?.system_eyes_packet?.payload || {};
                const eyesSummary = eyesPayload.summary || {};
                document.getElementById("eyes-summary-json").textContent = JSON.stringify(eyesSummary, null, 2);

                renderArtifactTable(state.artifacts || {});
                pageStatus.textContent = `Last refresh: ${new Date().toLocaleTimeString()}`;
            } catch (error) {
                pageStatus.textContent = `Refresh failed: ${error.message}`;
            }
        }

        function toggleAutoRefresh() {
            autoRefreshEnabled = !autoRefreshEnabled;
            const btn = document.getElementById("auto-refresh-btn");
            btn.textContent = `Auto refresh: ${autoRefreshEnabled ? "on" : "off"}`;
            if (autoRefreshEnabled) startAutoRefresh();
            else if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; }
        }

        function startAutoRefresh() {
            if (refreshTimer) clearInterval(refreshTimer);
            refreshTimer = setInterval(() => {
                if (autoRefreshEnabled) refreshAll();
            }, 15000);
        }

        refreshAll();
        startAutoRefresh();
    </script>
</body>
</html>
"""


@router.get("/system-dashboard", response_class=HTMLResponse)
def system_dashboard() -> HTMLResponse:
    return HTMLResponse(content=DASHBOARD_HTML)