def build_phase_document_payload(project_profile, phase_id):
    return {
        "project_id": project_profile["project_id"],
        "phase_id": phase_id,
        "phase_name": phase_id
    }