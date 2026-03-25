(function (global) {
  "use strict";

  function safeValue(value, fallback) {
    if (value === null || value === undefined || value === "") {
      return fallback === undefined ? "Not available" : fallback;
    }
    return String(value);
  }

  function titleCase(input) {
    return safeValue(input, "")
      .replace(/[_-]+/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .replace(/\b\w/g, function (char) {
        return char.toUpperCase();
      }) || "Unknown";
  }

  function normalizeConfidence(value) {
    var raw = safeValue(value, "").toLowerCase();
    if (!raw) return "Unknown";
    if (["high", "strong", "reinforced_support"].indexOf(raw) >= 0) return "High";
    if (["medium", "moderate", "partial"].indexOf(raw) >= 0) return "Medium";
    if (["low", "weak", "down"].indexOf(raw) >= 0) return "Low";
    return titleCase(raw);
  }

  function governanceText(governance) {
    var executionAllowed = !!(governance && governance.execution_allowed);
    var approvalRequired = !!(governance && governance.approval_required);
    var watcherPassed = governance && governance.watcher_passed;

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

  function deriveRecommendation(response) {
    var panel = response.recommendation_panel || {};
    var recommendations = Array.isArray(panel.recommendations) ? panel.recommendations : [];
    var first = recommendations[0];

    if (!first) {
      return {
        title: "No recommendation",
        note: "The system did not produce a candidate recommendation.",
        confidence: "Unknown",
        symbol: null,
        entry: null,
        exit: null
      };
    }

    return {
      title: safeValue(first.symbol, "Unknown Symbol"),
      note: safeValue(first.entry, "No entry logic") + " to " + safeValue(first.exit, "No exit logic"),
      confidence: normalizeConfidence(first.confidence),
      symbol: first.symbol || null,
      entry: first.entry || null,
      exit: first.exit || null
    };
  }

  function deriveCognition(response) {
    var cognition = response.cognition_panel || response.refinement_panel || {};
    var signal = cognition.signal || cognition.primary_signal || null;
    var insight = cognition.insight || cognition.summary || cognition.narrative || null;
    var riskFlag = cognition.risk_flag || cognition.risk || null;
    var narrative = cognition.narrative || cognition.explanation || null;
    var adjustment = cognition.confidence_adjustment || cognition.adjustment || null;

    var operatorInsight = "No refinement insight";
    var operatorNote = "No cognition layer output was surfaced.";

    if (insight) {
      operatorInsight = insight;
      operatorNote = signal ? "Signal: " + titleCase(signal) : "Derived from bounded refinement output.";
    } else if (riskFlag) {
      operatorInsight = titleCase(riskFlag);
      operatorNote = "Risk surfaced without narrative expansion.";
    } else if (signal) {
      operatorInsight = titleCase(signal);
      operatorNote = "Signal surfaced without additional narrative.";
    }

    return {
      insight: operatorInsight,
      note: operatorNote,
      signal: signal,
      riskFlag: riskFlag,
      narrative: narrative,
      adjustment: adjustment
    };
  }

  function derivePmWorkflow(response) {
    var workflow = response.pm_workflow_panel || {};
    var dispatch = workflow.dispatch || workflow.dispatch_record || {};
    var queue = workflow.queue || workflow.queue_record || {};
    var planning = workflow.planning || workflow.planning_record || {};
    var review = workflow.review || workflow.review_record || {};
    var strategy = workflow.strategy || workflow.strategy_record || {};

    var status =
      dispatch.dispatch_class ||
      planning.next_step_class ||
      planning.plan_class ||
      review.review_class ||
      strategy.strategy_class ||
      "monitor";

    var nextStep =
      dispatch.dispatch_target ||
      queue.queue_target ||
      planning.next_step_class ||
      review.review_class ||
      strategy.strategy_class ||
      "await_more_information";

    return {
      status: titleCase(status),
      next_step: titleCase(nextStep),
      strategy: strategy.strategy_class ? titleCase(strategy.strategy_class) : null,
      review: review.review_class ? titleCase(review.review_class) : null,
      planning: planning.plan_class ? titleCase(planning.plan_class) : null,
      queue_lane: queue.queue_lane ? titleCase(queue.queue_lane) : null,
      queue_status: queue.queue_status ? titleCase(queue.queue_status) : null,
      dispatch: dispatch.dispatch_class ? titleCase(dispatch.dispatch_class) : null
    };
  }

  function deriveGovernance(response) {
    var governance = response.governance_panel || {};
    return {
      state: governanceText(governance),
      mode: safeValue(response.mode || governance.mode || "advisory"),
      execution_allowed: !!governance.execution_allowed,
      approval_required: !!governance.approval_required,
      watcher_passed: governance.watcher_passed,
      requires_review: !!governance.requires_review,
      receipt_id: governance.receipt_id || null,
      watcher_validation_id: governance.watcher_validation_id || null,
      closeout_id: governance.closeout_id || null
    };
  }

  function deriveRuntime(response) {
    var runtime = response.runtime_panel || response.market_panel || {};
    var casePanel = response.case_panel || {};

    return {
      case_id: casePanel.case_id || response.case_id || response.request_id || null,
      title: casePanel.title || runtime.headline || response.headline || null,
      observed_at: casePanel.observed_at || response.observed_at || null,
      market_regime: runtime.market_regime ? titleCase(runtime.market_regime) : "Unknown",
      event_theme: runtime.event_theme ? titleCase(runtime.event_theme) : "Unknown",
      macro_bias: runtime.macro_bias ? titleCase(runtime.macro_bias) : "Unknown",
      headline: runtime.headline || response.headline || null
    };
  }

  function compressSystemView(response) {
    var recommendation = deriveRecommendation(response);
    var cognition = deriveCognition(response);
    var workflow = derivePmWorkflow(response);
    var governance = deriveGovernance(response);
    var runtime = deriveRuntime(response);

    return {
      summary: {
        insight: cognition.insight,
        insight_note: cognition.note,
        recommendation: recommendation.title,
        recommendation_note: recommendation.note,
        confidence: recommendation.confidence,
        status: workflow.status,
        next_step: workflow.next_step,
        governance: governance.state
      },
      recommendation: recommendation,
      cognition: cognition,
      pm_workflow: workflow,
      governance: governance,
      runtime: runtime,
      raw: response
    };
  }

  global.AIGOOperatorTransform = {
    safeValue: safeValue,
    titleCase: titleCase,
    normalizeConfidence: normalizeConfidence,
    compressSystemView: compressSystemView
  };
})(window);