function transformPortfolio(payload) {
    if (!payload || !payload.projects) return {};

    return {
        total_projects: payload.projects.length,

        active: payload.projects.filter(p => p.status === "active").length,
        blocked: payload.projects.filter(p => p.blocked === true).length,

        total_budget: payload.projects.reduce((sum, p) => {
            return sum + (p.budget || 0);
        }, 0),

        projects: payload.projects.map(p => ({
            id: p.project_id,
            phase: p.current_phase,
            status: p.status,
            risk: p.risk_level || "unknown"
        }))
    };
}