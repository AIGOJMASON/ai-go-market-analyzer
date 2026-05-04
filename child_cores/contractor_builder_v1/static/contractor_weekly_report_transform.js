function transformWeeklyReport(payload) {
    if (!payload) return {};

    return {
        project_id: payload.project_id,
        week: payload.week,

        progress: payload.workflow?.progress_summary || {},

        changes: payload.change?.weekly_changes || [],

        risks: payload.risk_register?.active || [],

        compliance: {
            permits: payload.compliance?.permits || [],
            inspections: payload.compliance?.inspections || []
        },

        summary: payload.summary || ""
    };
}