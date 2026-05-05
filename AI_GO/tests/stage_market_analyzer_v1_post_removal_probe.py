from __future__ import annotations

import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _module_absent(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return False
    except ModuleNotFoundError:
        return True


def _file_absent(relative_path: str) -> bool:
    return not (PROJECT_ROOT / relative_path).exists()


def _imports_cleanly(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except Exception:
        return False


def run_probe() -> dict:
    results: list[dict] = []

    removed_modules = [
        "AI_GO.core.strategy.pm_market_analyzer_route",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_shadow_packet_adapter",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_shadow_runner",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_shadow_cli_report",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_adapter",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_source",
        "AI_GO.child_cores.market_analyzer_v1.ui.live_data_runner",
        "AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_builder",
        "AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_runner",
        "AI_GO.child_cores.market_analyzer_v1.ui.operator_dashboard_cli_report",
    ]

    removed_files = [
        "core/strategy/pm_market_analyzer_route.py",
        "child_cores/market_analyzer_v1/ui/live_shadow_packet_adapter.py",
        "child_cores/market_analyzer_v1/ui/live_shadow_runner.py",
        "child_cores/market_analyzer_v1/ui/live_shadow_cli_report.py",
        "child_cores/market_analyzer_v1/ui/live_data_adapter.py",
        "child_cores/market_analyzer_v1/ui/live_data_source.py",
        "child_cores/market_analyzer_v1/ui/live_data_runner.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_builder.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_cli_report.py",
        "tests/stage_market_analyzer_v1_live_shadow_probe.py",
        "tests/stage_market_analyzer_v1_live_data_ingress_probe.py",
        "tests/stage_market_analyzer_v1_operator_dashboard_probe.py",
        "tests/stage_market_analyzer_v1_pm_routing_probe.py",
    ]

    # Case 01: removed PM/shadow/live/dashboard modules no longer import.
    case_01_pass = all(_module_absent(module_name) for module_name in removed_modules)
    results.append(
        {
            "case": "case_01_removed_modules_absent",
            "status": "passed" if case_01_pass else "failed",
        }
    )

    # Case 02: removed files are gone from active tree.
    case_02_pass = all(_file_absent(relative_path) for relative_path in removed_files)
    results.append(
        {
            "case": "case_02_removed_files_absent",
            "status": "passed" if case_02_pass else "failed",
        }
    )

    # Case 03: core execution surface still imports.
    case_03_pass = _imports_cleanly(
        "AI_GO.child_cores.market_analyzer_v1.execution.run"
    )
    results.append(
        {
            "case": "case_03_execution_surface_still_imports",
            "status": "passed" if case_03_pass else "failed",
        }
    )

    # Case 04: watcher surface still imports.
    case_04_pass = _imports_cleanly(
        "AI_GO.child_cores.market_analyzer_v1.watcher.core_watcher"
    )
    results.append(
        {
            "case": "case_04_watcher_surface_still_imports",
            "status": "passed" if case_04_pass else "failed",
        }
    )

    # Case 05: outputs surface still imports.
    case_05_pass = _imports_cleanly(
        "AI_GO.child_cores.market_analyzer_v1.outputs.output_builder"
    )
    results.append(
        {
            "case": "case_05_output_surface_still_imports",
            "status": "passed" if case_05_pass else "failed",
        }
    )

    # Case 06: replay harness remains available as regression tooling.
    case_06_pass = _imports_cleanly(
        "AI_GO.child_cores.market_analyzer_v1.ui.historical_replay_runner"
    )
    results.append(
        {
            "case": "case_06_historical_replay_harness_still_imports",
            "status": "passed" if case_06_pass else "failed",
        }
    )

    # Case 07: historical replay probe remains available.
    case_07_pass = _imports_cleanly(
        "AI_GO.tests.stage_market_analyzer_v1_historical_replay_probe"
    )
    results.append(
        {
            "case": "case_07_historical_replay_probe_still_imports",
            "status": "passed" if case_07_pass else "failed",
        }
    )

    # Case 08: no local PM routing surface remains in active strategy path.
    case_08_pass = _file_absent("core/strategy/pm_market_analyzer_route.py")
    results.append(
        {
            "case": "case_08_no_local_pm_routing_surface_remains",
            "status": "passed" if case_08_pass else "failed",
        }
    )

    # Case 09: no local live ingress/dashboard surface remains in child-core ui path.
    forbidden_ui_files = [
        "child_cores/market_analyzer_v1/ui/live_shadow_packet_adapter.py",
        "child_cores/market_analyzer_v1/ui/live_shadow_runner.py",
        "child_cores/market_analyzer_v1/ui/live_shadow_cli_report.py",
        "child_cores/market_analyzer_v1/ui/live_data_adapter.py",
        "child_cores/market_analyzer_v1/ui/live_data_source.py",
        "child_cores/market_analyzer_v1/ui/live_data_runner.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_builder.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_runner.py",
        "child_cores/market_analyzer_v1/ui/operator_dashboard_cli_report.py",
    ]
    case_09_pass = all(_file_absent(path) for path in forbidden_ui_files)
    results.append(
        {
            "case": "case_09_no_local_ui_ingress_or_dashboard_path_remains",
            "status": "passed" if case_09_pass else "failed",
        }
    )

    # Case 10: active market analyzer tree is clean enough for Stage 74-77 realignment.
    case_10_pass = all(
        item["status"] == "passed"
        for item in results[:9]
    )
    results.append(
        {
            "case": "case_10_tree_ready_for_stage_74_77_realignment",
            "status": "passed" if case_10_pass else "failed",
        }
    )

    passed = sum(1 for item in results if item["status"] == "passed")
    failed = sum(1 for item in results if item["status"] == "failed")

    return {
        "passed": passed,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    print(run_probe())