from __future__ import annotations

from PM_CORE.child_core_management.core_creation import create_child_core


def run() -> dict:
    """
    Draft-only Stage 12 smoke test.

    This intentionally uses create_child_core and does not call activate_child_core.
    """
    result = create_child_core(
        domain_focus="contractor_proposals",
        display_name="Contractor Proposals Core",
        core_id="contractor_proposals_core",
        notes="Stage 12 draft-only scaffold probe. No routing activation."
    )
    return result


if __name__ == "__main__":
    print(run())