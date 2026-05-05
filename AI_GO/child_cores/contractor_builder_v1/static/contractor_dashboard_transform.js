function transformDashboard(payload) {
    if (!payload) return {};

    return {
        project_id: payload.project_id || null,
        current_phase: payload.workflow?.current_phase || null,
        baseline_locked: payload.intake?.baseline_locked || false,

        blockers: {
            compliance: payload.compliance?.blocking_items || [],
            risks: payload.risk_register?.active || [],
            conflicts: payload.router?.conflicts || []
        },

        financials: {
            original_budget: payload.intake?.budget || null,
            approved_changes: payload.change?.approved_total || 0,
            projected_total: payload.change?.projected_total || null
        },

        next_action: payload.workflow?.next_required_action || "none"
    };
}