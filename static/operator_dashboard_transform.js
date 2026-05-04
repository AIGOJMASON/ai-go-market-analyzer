(function () {
  "use strict";

  const INDICATOR_CONFIG = [
    {
      key: "SPY",
      label: "SPY",
      fullName: "SPDR S&P 500 ETF Trust",
      meaning: "Broad market risk appetite."
    },
    {
      key: "QQQ",
      label: "QQQ",
      fullName: "Invesco QQQ Trust",
      meaning: "Growth and tech leadership."
    },
    {
      key: "XLE",
      label: "XLE",
      fullName: "Energy Select Sector SPDR Fund",
      meaning: "Energy sector strength and supply-shock response."
    },
    {
      key: "XLP",
      label: "XLP",
      fullName: "Consumer Staples Select Sector SPDR Fund",
      meaning: "Defensive consumer rotation."
    },
    {
      key: "XLU",
      label: "XLU",
      fullName: "Utilities Select Sector SPDR Fund",
      meaning: "Safety, defensiveness, and yield sensitivity."
    },
    {
      key: "TLT",
      label: "TLT",
      fullName: "iShares 20+ Year Treasury Bond ETF",
      meaning: "Bond flow, macro safety, and rate-pressure release."
    },
    {
      key: "COMMODITIES",
      label: "Commodities",
      fullName: "Tracked Commodity Board",
      meaning: "Raw materials pressure, inflation signals, and supply-driven market stress."
    }
  ];

  const FULL_NAME_MAP = {
    SPY: "SPDR S&P 500 ETF Trust",
    QQQ: "Invesco QQQ Trust",
    XLE: "Energy Select Sector SPDR Fund",
    XLP: "Consumer Staples Select Sector SPDR Fund",
    XLU: "Utilities Select Sector SPDR Fund",
    TLT: "iShares 20+ Year Treasury Bond ETF",
    XOM: "Exxon Mobil Corporation",
    CVX: "Chevron Corporation",
    KMI: "Kinder Morgan, Inc.",
    MRO: "Marathon Oil Corporation",
    APA: "APA Corporation",
    NEE: "NextEra Energy, Inc.",
    DUK: "Duke Energy Corporation",
    SO: "The Southern Company",
    AEP: "American Electric Power Company, Inc.",
    EXC: "Exelon Corporation",
    D: "Dominion Energy, Inc.",
    KRE: "SPDR S&P Regional Banking ETF",
    IWM: "iShares Russell 2000 ETF",
    GLD: "SPDR Gold Shares",
    USO: "United States Oil Fund, LP",
    CL: "Crude Oil",
    NG: "Natural Gas",
    GC: "Gold",
    SI: "Silver",
    HG: "Copper",
    ZW: "Wheat",
    ZC: "Corn",
    ZS: "Soybeans",
    SB: "Sugar",
    KC: "Coffee",
    CC: "Cocoa",
    CT: "Cotton",
    KHC: "The Kraft Heinz Company",
    MDLZ: "Mondelez International, Inc.",
    MO: "Altria Group, Inc.",
    PG: "The Procter & Gamble Company",
    KO: "The Coca-Cola Company",
    PEP: "PepsiCo, Inc.",
    XLY: "Consumer Discretionary Select Sector SPDR Fund",
    TSLA: "Tesla, Inc.",
    AMZN: "Amazon.com, Inc."
  };

  const COMMODITY_FALLBACKS = {
    energy: [
      { symbol: "CL", full_name: "Crude Oil", reason: "Watch for continued confirmation of the energy move." },
      { symbol: "USO", full_name: "United States Oil Fund, LP", reason: "Watch for alignment with crude strength." }
    ],
    utilities: [
      { symbol: "TLT", full_name: "iShares 20+ Year Treasury Bond ETF", reason: "Watch for continued confirmation of defensive bond support." },
      { symbol: "GLD", full_name: "SPDR Gold Shares", reason: "Watch for continued confirmation of defensive metals support." }
    ],
    staples: [
      { symbol: "GC", full_name: "Gold", reason: "Watch for defensive commodity confirmation." },
      { symbol: "ZW", full_name: "Wheat", reason: "Watch for continued stress in necessity-linked commodities." }
    ],
    macro: [
      { symbol: "GC", full_name: "Gold", reason: "Watch for broad risk-off confirmation." },
      { symbol: "CL", full_name: "Crude Oil", reason: "Watch for inflationary commodity pressure." }
    ],
    default: [
      { symbol: "GC", full_name: "Gold", reason: "Watch for commodity confirmation when live drivers are not yet populated." },
      { symbol: "CL", full_name: "Crude Oil", reason: "Watch for broad commodity leadership when live drivers are not yet populated." }
    ]
  };

  const PLACEHOLDER_MOVE = "Awaiting dedicated live panel data.";
  const PLACEHOLDER_READ = "Awaiting dedicated live panel data.";

  function byId(id) {
    return document.getElementById(id);
  }

  function safe(value, fallback = "—") {
    if (value === null || value === undefined) return fallback;
    if (typeof value === "string" && value.trim() === "") return fallback;
    return String(value);
  }

  function prettyBool(value) {
    if (value === true) return "Yes";
    if (value === false) return "No";
    return "—";
  }

  function formatJson(value) {
    try {
      return JSON.stringify(value || {}, null, 2);
    } catch (_error) {
      return "{}";
    }
  }

  function setStatus(message) {
    const node = byId("dashboard-status");
    if (!node) return;
    node.textContent = message;
  }

  function setHtml(id, html) {
    const node = byId(id);
    if (!node) return;
    node.innerHTML = html;
  }

  function escapeHtml(value) {
    return safe(value, "").replace(/[&<>"']/g, function (char) {
      const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "\"": "&quot;",
        "'": "&#39;"
      };
      return map[char] || char;
    });
  }

  function explanation(payload) {
    return payload && typeof payload === "object" ? (payload.operator_explanation || {}) : {};
  }

  function buildFallbackNarrative(payload) {
    const governancePanel =
      payload && payload.governance_panel && typeof payload.governance_panel === "object"
        ? payload.governance_panel
        : {};

    return {
      what_to_watch: "No current advisor explanation is available.",
      why_it_matters: "The system did not return a complete advisor narrative for this payload.",
      whats_been_happening: "Recent memory context could not be summarized from this payload.",
      what_this_looks_like: "Historical comparison could not be summarized from this payload.",
      what_to_watch_next: "Wait for a fresh governed run before relying on this surface.",
      posture: "This remains advisory-only until a fresh payload is available.",
      advisory_only: true,
      approval_required: governancePanel.approval_required,
      execution_allowed: governancePanel.execution_allowed
    };
  }

  function getHeaderPanel(payload) {
    return payload && typeof payload === "object" && payload.header_panel && typeof payload.header_panel === "object"
      ? payload.header_panel
      : {};
  }

  function getIndicatorPanels(payload) {
    return payload && typeof payload === "object" && Array.isArray(payload.indicator_panels)
      ? payload.indicator_panels
      : [];
  }

  function getCommodityBoard(payload) {
    return payload && typeof payload === "object" && payload.commodity_board && typeof payload.commodity_board === "object"
      ? payload.commodity_board
      : {};
  }

  function getActionBoard(payload) {
    return payload && typeof payload === "object" && payload.action_board && typeof payload.action_board === "object"
      ? payload.action_board
      : {};
  }

  function getWatchBoard(payload) {
    return payload && typeof payload === "object" && payload.watch_board && typeof payload.watch_board === "object"
      ? payload.watch_board
      : {};
  }

  function getHistoricalBoard(payload) {
    return payload && typeof payload === "object" && payload.historical_board && typeof payload.historical_board === "object"
      ? payload.historical_board
      : {};
  }

  function getRecentMemoryBoard(payload) {
    return payload && typeof payload === "object" && payload.recent_memory_board && typeof payload.recent_memory_board === "object"
      ? payload.recent_memory_board
      : {};
  }

  function getGovernanceBoard(payload) {
    return payload && typeof payload === "object" && payload.governance_board && typeof payload.governance_board === "object"
      ? payload.governance_board
      : {};
  }

  function getLiveEventPanel(payload) {
    return payload && typeof payload === "object" && payload.live_event_panel && typeof payload.live_event_panel === "object"
      ? payload.live_event_panel
      : {};
  }

  function getWatchlistPanel(payload) {
    return payload && typeof payload === "object" && payload.watchlist_panel && typeof payload.watchlist_panel === "object"
      ? payload.watchlist_panel
      : {};
  }

  function getHistoricalPanelLegacy(payload) {
    const summary =
      payload &&
      payload.source_2_summary &&
      typeof payload.source_2_summary === "object" &&
      payload.source_2_summary.historical_context &&
      typeof payload.source_2_summary.historical_context === "object"
        ? payload.source_2_summary.historical_context
        : {};

    return summary.setup_history_panel && typeof summary.setup_history_panel === "object"
      ? summary.setup_history_panel
      : {};
  }

  function getRecentMemorySummaryLegacy(payload) {
    if (
      payload &&
      payload.external_memory_packet &&
      typeof payload.external_memory_packet === "object" &&
      payload.external_memory_packet.advisory_summary &&
      typeof payload.external_memory_packet.advisory_summary === "object"
    ) {
      return payload.external_memory_packet.advisory_summary;
    }

    if (
      payload &&
      payload.source_1_summary &&
      typeof payload.source_1_summary === "object" &&
      payload.source_1_summary.promotion_artifact &&
      typeof payload.source_1_summary.promotion_artifact === "object" &&
      payload.source_1_summary.promotion_artifact.advisory_summary &&
      typeof payload.source_1_summary.promotion_artifact.advisory_summary === "object"
    ) {
      return payload.source_1_summary.promotion_artifact.advisory_summary;
    }

    return {};
  }

  function formatMovePct(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (Number.isNaN(number)) return safe(value);
    const sign = number > 0 ? "+" : "";
    return `${sign}${number.toFixed(1)}%`;
  }

  function formatRatePct(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (Number.isNaN(number)) return safe(value);
    return `${number.toFixed(2)}%`;
  }

  function normalizeWatchlistItems(items) {
    if (!Array.isArray(items)) return [];
    return items.filter(function (item) {
      return item && typeof item === "object";
    });
  }

  function groupWatchlistItems(panel) {
    const items = normalizeWatchlistItems(panel && panel.items);
    const grouped = {
      buy: [],
      avoid: [],
      fade: [],
      driver: []
    };

    items.forEach(function (item) {
      const bucket = typeof item.bucket === "string" ? item.bucket.trim().toLowerCase() : "";
      if (grouped[bucket]) {
        grouped[bucket].push(item);
      }
    });

    return grouped;
  }

  function fullNameForSymbol(symbol, fallbackName) {
    const normalized = typeof symbol === "string" ? symbol.trim().toUpperCase() : "";
    const fallback = typeof fallbackName === "string" ? fallbackName.trim() : "";

    if (fallback && fallback.toUpperCase() !== normalized) {
      return fallback;
    }

    return FULL_NAME_MAP[normalized] || normalized || "Unknown";
  }

  function sentenceNormalize(text) {
    return safe(text, "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .replace(/[.]+/g, ".")
      .trim();
  }

  function sentenceList(text) {
    const normalized = safe(text, "");
    if (!normalized) return [];
    return normalized
      .split(/(?<=[.!?])\s+/)
      .map(function (part) {
        return part.trim();
      })
      .filter(Boolean);
  }

  function compressSupportLine(primary, secondary) {
    const primaryNorm = sentenceNormalize(primary);
    if (!primaryNorm) return secondary || "";

    const secondarySentences = sentenceList(secondary);
    const kept = secondarySentences.filter(function (sentence) {
      const sentenceNorm = sentenceNormalize(sentence);
      return sentenceNorm && !primaryNorm.includes(sentenceNorm);
    });

    return kept.join(" ");
  }

  function renderListItems(items, options = {}) {
    const showFullName = options.showFullName !== false;

    if (!Array.isArray(items) || !items.length) {
      return `<div class="empty-state">None right now.</div>`;
    }

    return `
      <ul class="symbol-list">
        ${items
          .map(function (item) {
            const symbol = escapeHtml(item.symbol || "—");
            const resolvedName = fullNameForSymbol(item.symbol, item.full_name);
            const fullName = escapeHtml(resolvedName);
            const note = escapeHtml(item.note || item.reason || "No note provided.");

            return `
              <li class="symbol-list-item">
                <div class="symbol-row">
                  <span class="symbol-pill">${symbol}</span>
                  <span class="symbol-note">
                    ${showFullName ? `<strong>${fullName}</strong><br />` : ""}
                    ${note}
                  </span>
                </div>
              </li>
            `;
          })
          .join("")}
      </ul>
    `;
  }

  function renderTopBuys(payload) {
    const actionBoard = getActionBoard(payload);
    if (actionBoard && Object.keys(actionBoard).length) {
      return `
        <article class="board-card">
          <header class="board-card-header">
            <h2>${escapeHtml(actionBoard.primary_title || "Top 5 Buys Right Now")}</h2>
            <p>${escapeHtml(actionBoard.primary_subtitle || "Governed long candidates from the current board.")}</p>
          </header>
          <div class="board-card-body">
            ${renderListItems(actionBoard.primary_list || [], { showFullName: true })}
          </div>
        </article>
      `;
    }

    const watchlist = getWatchlistPanel(payload);
    const grouped = groupWatchlistItems(watchlist);
    const noTradeState = watchlist.no_trade_state && typeof watchlist.no_trade_state === "object"
      ? watchlist.no_trade_state
      : {};

    const buyItems = grouped.buy.slice(0, 5);
    const conditionalItems = grouped.avoid.slice(0, 5);

    let title = "Top 5 Buys Right Now";
    let subtitle = "Governed long candidates from the current board.";
    let body = renderListItems(buyItems, { showFullName: true });

    if (!buyItems.length || noTradeState.is_no_trade === true) {
      title = "No Governed Buys Right Now";
      subtitle = "Best conditional longs if this setup improves.";
      body = renderListItems(conditionalItems, { showFullName: true });
    }

    return `
      <article class="board-card">
        <header class="board-card-header">
          <h2>${escapeHtml(title)}</h2>
          <p>${escapeHtml(subtitle)}</p>
        </header>
        <div class="board-card-body">
          ${body}
        </div>
      </article>
    `;
  }

  function renderWatchTriggers(payload, effectiveExplanation) {
    const watchBoard = getWatchBoard(payload);
    const triggerBlocks = [];

    if (watchBoard && Object.keys(watchBoard).length) {
      if (typeof watchBoard.primary_watch_text === "string" && watchBoard.primary_watch_text.trim()) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">Primary Watch</div>
            <div class="trigger-text">${escapeHtml(watchBoard.primary_watch_text.trim())}</div>
          </div>
        `);
      }

      const triggerItems = Array.isArray(watchBoard.trigger_items) ? watchBoard.trigger_items.slice(0, 5) : [];
      triggerItems.forEach(function (item) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">${escapeHtml(item.symbol || "Trigger")}</div>
            <div class="trigger-text">${escapeHtml(item.reason || "Confirmation signal.")}</div>
          </div>
        `);
      });

      const riskItems = Array.isArray(watchBoard.risk_items) ? watchBoard.risk_items.slice(0, 3) : [];
      riskItems.forEach(function (item) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">${escapeHtml(item.symbol || "Risk")}</div>
            <div class="trigger-text">${escapeHtml(item.reason || "Failure expression if momentum fades.")}</div>
          </div>
        `);
      });
    } else {
      const watchlist = getWatchlistPanel(payload);
      const grouped = groupWatchlistItems(watchlist);
      const driverItems = grouped.driver.slice(0, 5);
      const fadeItems = grouped.fade.slice(0, 3);

      if (typeof effectiveExplanation.what_to_watch_next === "string" && effectiveExplanation.what_to_watch_next.trim()) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">Primary Watch</div>
            <div class="trigger-text">${escapeHtml(effectiveExplanation.what_to_watch_next.trim())}</div>
          </div>
        `);
      }

      driverItems.forEach(function (item) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">${escapeHtml(item.symbol || "Driver")}</div>
            <div class="trigger-text">${escapeHtml(item.note || "Confirmation signal.")}</div>
          </div>
        `);
      });

      fadeItems.forEach(function (item) {
        triggerBlocks.push(`
          <div class="trigger-block">
            <div class="trigger-label">${escapeHtml(item.symbol || "Risk")}</div>
            <div class="trigger-text">${escapeHtml(item.note || "Failure expression if momentum fades.")}</div>
          </div>
        `);
      });
    }

    if (!triggerBlocks.length) {
      triggerBlocks.push(`
        <div class="empty-state">No watch triggers available from the current payload.</div>
      `);
    }

    return `
      <article class="board-card">
        <header class="board-card-header">
          <h2>What to Watch</h2>
          <p>The next conditions that matter most from the current governed read.</p>
        </header>
        <div class="board-card-body trigger-grid">
          ${triggerBlocks.join("")}
        </div>
      </article>
    `;
  }

  function renderHistoricalRead(payload) {
    const historicalBoard = getHistoricalBoard(payload);
    const history = historicalBoard && Object.keys(historicalBoard).length
      ? historicalBoard
      : getHistoricalPanelLegacy(payload);

    const operatorSummary =
      historicalBoard && typeof historicalBoard.operator_summary === "string" && historicalBoard.operator_summary.trim()
        ? historicalBoard.operator_summary
        : payload &&
          payload.source_2_summary &&
          payload.source_2_summary.historical_context &&
          typeof payload.source_2_summary.historical_context.operator_summary === "string"
            ? payload.source_2_summary.historical_context.operator_summary
            : "Historical context is not available.";

    const hasHistory =
      (history.historical_posture && String(history.historical_posture).trim()) ||
      (history.follow_through_rate_pct !== null && history.follow_through_rate_pct !== undefined) ||
      (history.failure_rate_pct !== null && history.failure_rate_pct !== undefined);

    if (!hasHistory) {
      return `
        <article class="board-card">
          <header class="board-card-header">
            <h2>Historical Read</h2>
            <p>How similar setups have behaved before.</p>
          </header>
          <div class="board-card-body">
            <div class="empty-state">${escapeHtml(operatorSummary)}</div>
          </div>
        </article>
      `;
    }

    return `
      <article class="board-card">
        <header class="board-card-header">
          <h2>Historical Read</h2>
          <p>How similar setups have behaved before.</p>
        </header>
        <div class="board-card-body">
          <div class="metric-grid three-up">
            <div class="metric-box">
              <span class="metric-label">Posture</span>
              <span class="metric-value">${escapeHtml(history.historical_posture || "—")}</span>
            </div>
            <div class="metric-box">
              <span class="metric-label">Follow-through</span>
              <span class="metric-value">${escapeHtml(formatRatePct(history.follow_through_rate_pct))}</span>
            </div>
            <div class="metric-box">
              <span class="metric-label">Failure</span>
              <span class="metric-value">${escapeHtml(formatRatePct(history.failure_rate_pct))}</span>
            </div>
          </div>
          <p class="support-text">${escapeHtml(operatorSummary)}</p>
        </div>
      </article>
    `;
  }

  function renderRecentMemory(payload) {
    const recentMemoryBoard = getRecentMemoryBoard(payload);
    const memory = recentMemoryBoard && Object.keys(recentMemoryBoard).length
      ? recentMemoryBoard
      : getRecentMemorySummaryLegacy(payload);

    const flags = Array.isArray(memory.coherence_flags) ? memory.coherence_flags.slice(0, 6) : [];
    const posture = memory.advisory_posture || memory.decision || "";
    const recordCount = memory.record_count;
    const promotionScore = memory.promotion_score;

    const hasStructuredMemory =
      Boolean(posture) ||
      (recordCount !== null && recordCount !== undefined) ||
      (promotionScore !== null && promotionScore !== undefined) ||
      flags.length > 0;

    if (!hasStructuredMemory) {
      return `
        <article class="board-card">
          <header class="board-card-header">
            <h2>Recent Memory</h2>
            <p>How recent promoted records align with the current case.</p>
          </header>
          <div class="board-card-body">
            <div class="empty-state">Recent memory context is not available for this case.</div>
          </div>
        </article>
      `;
    }

    return `
      <article class="board-card">
        <header class="board-card-header">
          <h2>Recent Memory</h2>
          <p>How recent promoted records align with the current case.</p>
        </header>
        <div class="board-card-body">
          <div class="metric-grid three-up">
            <div class="metric-box">
              <span class="metric-label">Posture</span>
              <span class="metric-value">${escapeHtml(posture || "—")}</span>
            </div>
            <div class="metric-box">
              <span class="metric-label">Promoted Records</span>
              <span class="metric-value">${escapeHtml(recordCount || "—")}</span>
            </div>
            <div class="metric-box">
              <span class="metric-label">Promotion Score</span>
              <span class="metric-value">${escapeHtml(promotionScore || "—")}</span>
            </div>
          </div>
          <div class="tag-row">
            ${
              flags.length
                ? flags.map(function (flag) {
                    return `<span class="tag">${escapeHtml(flag)}</span>`;
                  }).join("")
                : `<span class="empty-state">No coherence flags present.</span>`
            }
          </div>
        </div>
      </article>
    `;
  }

  function buildIndicatorCardFromBoard(config, panel) {
    if (!panel || typeof panel !== "object") return null;

    const badge =
      panel.system_read && panel.system_read.posture_label
        ? panel.system_read.posture_label
        : panel.system_read && panel.system_read.historical_posture
          ? panel.system_read.historical_posture
          : panel.state === "placeholder"
            ? "Placeholder"
            : "Active";

    const currentMove = panel.current_move && panel.current_move.status === "ok"
      ? [
          formatMovePct(panel.current_move.price_change_pct),
          safe(panel.current_move.confirmation, "—"),
          panel.current_move.headline ? safe(panel.current_move.headline, "—") : safe(panel.category, "—")
        ].join(" | ")
      : PLACEHOLDER_MOVE;

    const systemRead = panel.system_read && panel.system_read.summary
      ? panel.system_read.summary
      : PLACEHOLDER_READ;

    const watchText = panel.what_to_watch && panel.what_to_watch.summary
      ? panel.what_to_watch.summary
      : "No specific trigger available.";

    return `
      <article class="indicator-card ${panel.state === "placeholder" ? "placeholder" : "active"}">
        <div class="indicator-header">
          <div>
            <div class="indicator-symbol">${escapeHtml(config.label)}</div>
            <div class="indicator-name">${escapeHtml(config.fullName)}</div>
          </div>
          <span class="indicator-badge ${panel.state === "placeholder" ? "muted" : ""}">${escapeHtml(badge)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">What it means</span>
          <span class="section-value">${escapeHtml(config.meaning)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">Current move</span>
          <span class="section-value">${escapeHtml(currentMove)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">System read</span>
          <span class="section-value">${escapeHtml(systemRead)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">What to watch</span>
          <span class="section-value">${escapeHtml(watchText)}</span>
        </div>
      </article>
    `;
  }

  function buildIndicatorCardLegacy(config, payload, effectiveExplanation) {
    const live = getLiveEventPanel(payload);
    const watchlist = getWatchlistPanel(payload);
    const history = getHistoricalPanelLegacy(payload);
    const grouped = groupWatchlistItems(watchlist);

    if (config.key === "COMMODITIES") {
      return buildCommoditiesCard(payload);
    }

    const isActive = live.symbol === config.key;

    if (!isActive) {
      return `
        <article class="indicator-card placeholder">
          <div class="indicator-header">
            <div>
              <div class="indicator-symbol">${escapeHtml(config.label)}</div>
              <div class="indicator-name">${escapeHtml(config.fullName)}</div>
            </div>
            <span class="indicator-badge muted">Placeholder</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">What it means</span>
            <span class="section-value">${escapeHtml(config.meaning)}</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">Current move</span>
            <span class="section-value">${escapeHtml(PLACEHOLDER_MOVE)}</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">System read</span>
            <span class="section-value">${escapeHtml(PLACEHOLDER_READ)}</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">What to watch</span>
            <span class="section-value">No panel-specific trigger available yet.</span>
          </div>
        </article>
      `;
    }

    const badge = watchlist.posture_label || history.historical_posture || "Active";
    const driverSymbols = grouped.driver.slice(0, 3).map(function (item) {
      return item.symbol;
    }).filter(Boolean);

    const currentMove = [
      formatMovePct(live.price_change_pct),
      safe(live.confirmation, "—"),
      watchlist.active_lane ? `${watchlist.active_lane} lane active` : safe(live.sector, "—")
    ].join(" | ");

    const systemReadParts = [];
    if (watchlist.posture_label) systemReadParts.push(watchlist.posture_label);
    if (watchlist.no_trade_state && watchlist.no_trade_state.is_no_trade === true) systemReadParts.push("no-trade");
    if (history.historical_posture) systemReadParts.push(history.historical_posture);

    const watchLine = driverSymbols.length
      ? `Watch: ${driverSymbols.join(", ")}`
      : effectiveExplanation.what_to_watch_next || "No specific trigger available.";

    return `
      <article class="indicator-card active">
        <div class="indicator-header">
          <div>
            <div class="indicator-symbol">${escapeHtml(config.label)}</div>
            <div class="indicator-name">${escapeHtml(config.fullName)}</div>
          </div>
          <span class="indicator-badge">${escapeHtml(badge)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">What it means</span>
          <span class="section-value">${escapeHtml(config.meaning)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">Current move</span>
          <span class="section-value">${escapeHtml(currentMove)}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">System read</span>
          <span class="section-value">${escapeHtml(systemReadParts.join(" | ") || "—")}</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">What to watch</span>
          <span class="section-value">${escapeHtml(watchLine)}</span>
        </div>
      </article>
    `;
  }

  function pickCommodityFallback(lane) {
    const normalized = typeof lane === "string" ? lane.trim().toLowerCase() : "";
    return COMMODITY_FALLBACKS[normalized] || COMMODITY_FALLBACKS.default;
  }

  function commodityBoardLooksStale(board, lane) {
    if (!board || typeof board !== "object" || !Object.keys(board).length) return true;
    const summary =
      board.summary_line && typeof board.summary_line.text === "string"
        ? board.summary_line.text.toLowerCase()
        : "";
    const watchItems =
      board.what_to_watch && Array.isArray(board.what_to_watch.items)
        ? board.what_to_watch.items
        : [];
    const watchSymbols = watchItems
      .map(function (item) {
        return String(item.symbol || "").toUpperCase();
      })
      .filter(Boolean);

    if (lane === "staples") {
      if (summary.includes("energy signal")) return true;
      if (watchSymbols.includes("CL") || watchSymbols.includes("USO")) return true;
    }
    if (lane === "utilities") {
      if (summary.includes("energy signal")) return true;
      if (watchSymbols.includes("CL") || watchSymbols.includes("USO")) return true;
    }
    return false;
  }

  function buildCommodityFallbackCard(lane, watchlist) {
    const grouped = groupWatchlistItems(watchlist);
    const drivers = grouped.driver.filter(function (item) {
      return ["CL", "USO", "NG", "GC", "SI", "HG", "ZW", "ZC", "ZS", "GLD", "TLT"].includes(item.symbol);
    });

    const fallbackItems = pickCommodityFallback(lane);
    const displayRows = drivers.length ? drivers : fallbackItems;
    const watchBlocks = drivers.length ? drivers.slice(0, 3) : fallbackItems.slice(0, 3);

    const summary =
      lane === "energy"
        ? "Commodities are currently serving as confirmation for the live energy signal."
        : lane === "utilities"
          ? "Defensive commodities are more relevant than energy commodities for this utilities-led case."
          : lane === "staples"
            ? "Defensive and necessity-linked commodities matter more than energy commodities for this staples-led case."
            : "Commodity confirmation data is not yet fully populated in this payload.";

    return `
      <article class="indicator-card commodities">
        <div class="indicator-header">
          <div>
            <div class="indicator-symbol">Commodities</div>
            <div class="indicator-name">Tracked Commodity Board</div>
          </div>
          <span class="indicator-badge muted">Starter</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">What it means</span>
          <span class="section-value">Raw materials pressure, inflation signals, and supply-driven stress.</span>
        </div>
        <div class="indicator-section">
          <span class="section-label">System read</span>
          <span class="section-value">${escapeHtml(summary)}</span>
        </div>
        <div class="commodity-board">
          ${displayRows.map(function (item) {
            return `
              <div class="commodity-row">
                <span class="commodity-name">${escapeHtml(item.full_name || fullNameForSymbol(item.symbol))}</span>
                <span class="commodity-move">${escapeHtml(item.display_move || "move unavailable")}</span>
              </div>
            `;
          }).join("")}
        </div>
        <div class="commodity-summary">
          <span class="section-label">Summary</span>
          <span class="section-value">${escapeHtml(summary)}</span>
        </div>
        <div class="commodity-watch">
          <span class="section-label">Commodity Watch Triggers</span>
          <div class="trigger-grid compact">
            ${watchBlocks.map(function (item) {
              return `
                <div class="trigger-block compact">
                  <div class="trigger-label">${escapeHtml(item.symbol || "Commodity")}</div>
                  <div class="trigger-text">${escapeHtml(item.note || item.reason || "Watch for confirmation behavior.")}</div>
                </div>
              `;
            }).join("")}
          </div>
        </div>
      </article>
    `;
  }

  function buildCommoditiesCard(payload) {
    const commodityBoard = getCommodityBoard(payload);
    const watchlist = getWatchlistPanel(payload);
    const lane = String(watchlist.active_lane || "").toLowerCase();

    if (commodityBoard && Object.keys(commodityBoard).length && !commodityBoardLooksStale(commodityBoard, lane)) {
      const rows = Array.isArray(commodityBoard.commodity_rows) ? commodityBoard.commodity_rows.slice(0, 12) : [];
      const watchItems =
        commodityBoard.what_to_watch && Array.isArray(commodityBoard.what_to_watch.items)
          ? commodityBoard.what_to_watch.items.slice(0, 5)
          : [];

      return `
        <article class="indicator-card commodities">
          <div class="indicator-header">
            <div>
              <div class="indicator-symbol">Commodities</div>
              <div class="indicator-name">${escapeHtml(commodityBoard.full_name || "Tracked Commodity Board")}</div>
            </div>
            <span class="indicator-badge muted">${escapeHtml(commodityBoard.state || "Starter")}</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">What it means</span>
            <span class="section-value">${escapeHtml(commodityBoard.meaning || "Raw materials pressure, inflation signals, and supply-driven stress.")}</span>
          </div>
          <div class="indicator-section">
            <span class="section-label">System read</span>
            <span class="section-value">${escapeHtml(
              commodityBoard.system_read && commodityBoard.system_read.summary
                ? commodityBoard.system_read.summary
                : "Commodity confirmation data is not yet fully populated in this payload."
            )}</span>
          </div>
          <div class="commodity-board">
            ${
              rows.length
                ? rows.map(function (row) {
                    return `
                      <div class="commodity-row">
                        <span class="commodity-name">${escapeHtml(row.full_name || fullNameForSymbol(row.symbol))}</span>
                        <span class="commodity-move">${escapeHtml(row.display_move || "move unavailable")}</span>
                      </div>
                    `;
                  }).join("")
                : `<div class="empty-state">No commodity rows available.</div>`
            }
          </div>
          <div class="commodity-summary">
            <span class="section-label">Summary</span>
            <span class="section-value">${escapeHtml(
              commodityBoard.summary_line && commodityBoard.summary_line.text
                ? commodityBoard.summary_line.text
                : "Commodity confirmation data is not yet fully populated in this payload."
            )}</span>
          </div>
          <div class="commodity-watch">
            <span class="section-label">Commodity Watch Triggers</span>
            <div class="trigger-grid compact">
              ${
                watchItems.length
                  ? watchItems.map(function (item) {
                      return `
                        <div class="trigger-block compact">
                          <div class="trigger-label">${escapeHtml(item.symbol || "Commodity")}</div>
                          <div class="trigger-text">${escapeHtml(item.reason || "Watch for confirmation behavior.")}</div>
                        </div>
                      `;
                    }).join("")
                  : `<div class="empty-state">No commodity watch triggers available.</div>`
              }
            </div>
          </div>
        </article>
      `;
    }

    return buildCommodityFallbackCard(lane, watchlist);
  }

  function renderIndicatorGrid(payload, effectiveExplanation) {
    const boardPanels = getIndicatorPanels(payload);
    const panelById = {};
    boardPanels.forEach(function (panel) {
      if (panel && typeof panel === "object" && panel.panel_id) {
        panelById[String(panel.panel_id).toUpperCase()] = panel;
      }
    });

    const html = INDICATOR_CONFIG.map(function (config) {
      if (config.key === "COMMODITIES") {
        return buildCommoditiesCard(payload);
      }

      const boardPanel = panelById[config.key];
      if (boardPanel) {
        return buildIndicatorCardFromBoard(config, boardPanel);
      }
      return buildIndicatorCardLegacy(config, payload, effectiveExplanation);
    }).join("");

    setHtml("indicator-grid", html);
  }

  function renderHeader(payload) {
    const headerPanel = getHeaderPanel(payload);
    const governance = payload && payload.governance_panel && typeof payload.governance_panel === "object"
      ? payload.governance_panel
      : {};

    const chips = [
      { label: "Mode", value: headerPanel.mode || payload.mode },
      { label: "Route", value: headerPanel.route_mode || payload.route_mode || governance.route_path },
      {
        label: "Approval Required",
        value: prettyBool(
          headerPanel.approval_required !== undefined
            ? headerPanel.approval_required
            : governance.approval_required
        )
      },
      {
        label: "Execution Allowed",
        value: prettyBool(
          headerPanel.execution_allowed !== undefined
            ? headerPanel.execution_allowed
            : governance.execution_allowed
        )
      }
    ];

    setHtml(
      "status-chip-row",
      chips
        .map(function (chip) {
          return `
            <div class="status-chip">
              <span class="status-chip-label">${escapeHtml(chip.label)}</span>
              <span class="status-chip-value">${escapeHtml(chip.value)}</span>
            </div>
          `;
        })
        .join("")
    );
  }

  function renderNarrativeSummary(payload, effectiveExplanation) {
    const watchlist = getWatchlistPanel(payload);
    const topLine = typeof watchlist.summary === "string" && watchlist.summary.trim()
      ? watchlist.summary.trim()
      : effectiveExplanation.what_to_watch || "No current board summary available.";

    const supportLine = effectiveExplanation.why_it_matters || "";
    const finalSupport = compressSupportLine(topLine, supportLine);

    setHtml(
      "board-summary",
      `
        <article class="board-card summary-card">
          <header class="board-card-header">
            <h2>Current Read</h2>
            <p>The highest-priority governed takeaway from the latest payload.</p>
          </header>
          <div class="board-card-body">
            <p class="summary-line">${escapeHtml(topLine)}</p>
            ${finalSupport ? `<p class="support-text">${escapeHtml(finalSupport)}</p>` : ""}
          </div>
        </article>
      `
    );
  }

  function renderGovernanceFooter(payload, effectiveExplanation) {
    const governanceBoard = getGovernanceBoard(payload);
    const governance = payload && payload.governance_panel && typeof payload.governance_panel === "object"
      ? payload.governance_panel
      : {};

    const footerItems = [
      {
        label: "Advisory Only",
        value: prettyBool(
          governanceBoard.advisory_only !== undefined
            ? governanceBoard.advisory_only
            : effectiveExplanation.advisory_only !== undefined
              ? effectiveExplanation.advisory_only
              : true
        )
      },
      {
        label: "Approval Required",
        value: prettyBool(
          governanceBoard.approval_required !== undefined
            ? governanceBoard.approval_required
            : effectiveExplanation.approval_required !== undefined
              ? effectiveExplanation.approval_required
              : governance.approval_required
        )
      },
      {
        label: "Execution Allowed",
        value: prettyBool(
          governanceBoard.execution_allowed !== undefined
            ? governanceBoard.execution_allowed
            : effectiveExplanation.execution_allowed !== undefined
              ? effectiveExplanation.execution_allowed
              : governance.execution_allowed
        )
      },
      {
        label: "Request ID",
        value: safe(payload.request_id)
      }
    ];

    setHtml(
      "governance-footer",
      footerItems
        .map(function (item) {
          return `
            <div class="footer-metric">
              <span class="footer-label">${escapeHtml(item.label)}</span>
              <span class="footer-value">${escapeHtml(item.value)}</span>
            </div>
          `;
        })
        .join("")
    );
  }

  function renderRawResponse(payload) {
    const rawNode = byId("raw-response-content");
    if (!rawNode) return;
    rawNode.textContent = formatJson(payload);
  }

  function renderDashboard(payload) {
    if (!payload || typeof payload !== "object") {
      setStatus("Latest payload was empty or invalid.");
      return;
    }

    const exp = explanation(payload);
    const effective = exp && Object.keys(exp).length > 0 ? exp : buildFallbackNarrative(payload);

    renderHeader(payload);
    renderNarrativeSummary(payload, effective);
    renderIndicatorGrid(payload, effective);
    setHtml("historical-read-slot", renderHistoricalRead(payload));
    setHtml("recent-memory-slot", renderRecentMemory(payload));
    setHtml("watch-triggers-slot", renderWatchTriggers(payload, effective));
    setHtml("top-buys-slot", renderTopBuys(payload));
    renderGovernanceFooter(payload, effective);
    renderRawResponse(payload);
  }

  async function fetchLatestPayload() {
    setStatus("Loading latest market board payload.");

    try {
      const response = await fetch("/market-analyzer/operator/latest", {
        method: "GET",
        headers: {
          "Accept": "application/json"
        },
        cache: "no-store"
      });

      if (!response.ok) {
        throw new Error(`Latest payload request failed with status ${response.status}`);
      }

      const payload = await response.json();

      if (payload && payload.state === "absent") {
        setStatus("No governed operator payload has been recorded yet.");
        renderRawResponse(payload);
        return;
      }

      renderDashboard(payload);
      setStatus("Latest market board payload loaded.");
    } catch (error) {
      setStatus(`Failed to load latest market board payload: ${error.message}`);
    }
  }

  function installRawToggle() {
    const button = byId("toggle-raw-response");
    const panel = byId("raw-response-panel");
    if (!button || !panel) return;

    button.addEventListener("click", function () {
      const hidden = panel.classList.contains("hidden");
      if (hidden) {
        panel.classList.remove("hidden");
        button.textContent = "Hide Raw Response";
      } else {
        panel.classList.add("hidden");
        button.textContent = "Show Raw Response";
      }
    });
  }

  function installRefresh() {
    const button = byId("refresh-live-view");
    if (!button) return;

    button.addEventListener("click", function () {
      fetchLatestPayload();
    });
  }

  function init() {
    installRawToggle();
    installRefresh();

    if (window.__AI_GO_OPERATOR_INITIAL_PAYLOAD__) {
      renderDashboard(window.__AI_GO_OPERATOR_INITIAL_PAYLOAD__);
      setStatus("Latest market board payload loaded.");
      return;
    }

    fetchLatestPayload();
  }

  window.OperatorDashboardTransform = {
    init: init,
    renderDashboard: renderDashboard,
    fetchLatestPayload: fetchLatestPayload
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();