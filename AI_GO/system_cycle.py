from __future__ import annotations

import argparse
import importlib
import inspect
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from AI_GO.core.governance.governed_persistence import governed_write_json


SYSTEM_CYCLE_VERSION = "northstar_system_cycle_v1"
MUTATION_CLASS = "awareness_persistence"
PERSISTENCE_TYPE_STATUS = "system_cycle_status"
PERSISTENCE_TYPE_RECEIPT = "system_cycle_receipt"


AUTHORITY_METADATA: dict[str, Any] = {
    "advisory_only": True,
    "can_execute": False,
    "can_mutate_workflow_state": False,
    "can_mutate_project_truth": False,
    "can_mutate_pm_authority": False,
    "can_override_governance": False,
    "can_override_watcher": False,
    "can_override_execution_gate": False,
    "authority_scope": "system_cycle_awareness_only",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_for_persistence(
    *,
    payload: dict[str, Any],
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
) -> dict[str, Any]:
    normalized = dict(payload)
    normalized.setdefault("artifact_version", SYSTEM_CYCLE_VERSION)
    normalized["persistence_type"] = persistence_type
    normalized["mutation_class"] = mutation_class
    normalized["advisory_only"] = True
    normalized["authority_metadata"] = dict(AUTHORITY_METADATA)
    normalized["execution_allowed"] = False
    normalized["approval_required"] = True
    return normalized


def _governed_write(
    *,
    path: Path,
    payload: dict[str, Any],
    persistence_type: str,
    mutation_class: str = MUTATION_CLASS,
) -> str:
    normalized = _normalize_for_persistence(
        payload=payload,
        persistence_type=persistence_type,
        mutation_class=mutation_class,
    )

    kwargs = {
        "path": path,
        "output_path": path,
        "payload": normalized,
        "data": normalized,
        "persistence_type": persistence_type,
        "mutation_class": mutation_class,
        "advisory_only": True,
        "authority_metadata": dict(AUTHORITY_METADATA),
    }

    signature = inspect.signature(governed_write_json)
    accepted = {
        key: value
        for key, value in kwargs.items()
        if key in signature.parameters
    }

    if any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in signature.parameters.values()
    ):
        result = governed_write_json(**kwargs)
    elif accepted:
        result = governed_write_json(**accepted)
    else:
        result = governed_write_json(path, normalized)

    if isinstance(result, dict):
        return str(result.get("path") or result.get("output_path") or path)

    return str(path)


def safe_json_dump(path: Path, payload: dict[str, Any]) -> None:
    _governed_write(
        path=path,
        payload=payload,
        persistence_type=PERSISTENCE_TYPE_STATUS,
    )


@dataclass
class StepResult:
    step_name: str
    status: str
    started_at: str
    ended_at: str
    detail: str = ""
    outputs: dict[str, Any] = field(default_factory=dict)


@dataclass
class CycleRunResult:
    cycle_id: str
    started_at: str
    ended_at: str
    status: str
    mode: str
    iteration: int
    steps: list[StepResult]
    project_root: str
    receipts_dir: str
    current_status_path: str


class SystemCycle:
    def __init__(
        self,
        project_root: Path | None = None,
        interval_seconds: int = 300,
        once: bool = False,
        iterations: int | None = None,
        live_request_json: str | None = None,
        live_request_file: str | None = None,
        enable_live_trigger: bool = False,
        stop_on_error: bool = False,
        quiet: bool = False,
    ) -> None:
        self.project_root = project_root or Path(__file__).resolve().parent
        self.interval_seconds = max(1, int(interval_seconds))
        self.once = once
        self.iterations = iterations
        self.live_request_json = live_request_json
        self.live_request_file = live_request_file
        self.enable_live_trigger = enable_live_trigger
        self.stop_on_error = stop_on_error
        self.quiet = quiet

        self.state_root = self.project_root / "state" / "system_cycle"
        self.current_root = self.state_root / "current"
        self.receipts_root = self.state_root / "receipts"
        self.current_status_path = self.current_root / "latest_cycle_status.json"

    def _log(self, message: str) -> None:
        if not self.quiet:
            print(message)

    def _call_function(
        self,
        dotted_path: str,
        candidate_names: Iterable[str],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        module = importlib.import_module(dotted_path)

        for name in candidate_names:
            candidate = getattr(module, name, None)
            if callable(candidate):
                signature = inspect.signature(candidate)
                accepted_kwargs = {
                    key: value
                    for key, value in kwargs.items()
                    if key in signature.parameters
                }
                return candidate(*args, **accepted_kwargs)

        raise AttributeError(
            f"No callable found in {dotted_path}: {', '.join(candidate_names)}"
        )

    def _run_step(
        self,
        *,
        step_name: str,
        callable_ref: Callable[[], Any],
    ) -> StepResult:
        started_at = utc_now_iso()

        try:
            output = callable_ref()
            ended_at = utc_now_iso()
            return StepResult(
                step_name=step_name,
                status="passed",
                started_at=started_at,
                ended_at=ended_at,
                outputs=output if isinstance(output, dict) else {"result": output},
            )
        except Exception as exc:
            ended_at = utc_now_iso()
            return StepResult(
                step_name=step_name,
                status="failed",
                started_at=started_at,
                ended_at=ended_at,
                detail=f"{type(exc).__name__}: {exc}",
                outputs={},
            )

    def _run_live_trigger(self) -> Any:
        if self.enable_live_trigger:
            return self._call_function(
                "AI_GO.core.live_trigger.synthetic_live_trigger",
                ["run_synthetic_live_trigger", "run_once", "main_run"],
            )

        if self.live_request_json or self.live_request_file:
            return self._call_function(
                "AI_GO.api.market_analyzer_api",
                ["run_market_analyzer_live_request", "run_live_request"],
                request_json=self.live_request_json,
                request_file=self.live_request_file,
            )

        return {
            "status": "skipped",
            "reason": "live trigger not enabled",
            "advisory_only": True,
            "execution_allowed": False,
        }

    def _build_steps(self) -> list[tuple[str, Callable[[], Any]]]:
        return [
            ("live_trigger", self._run_live_trigger),
            (
                "continuity_weighting",
                lambda: self._call_function(
                    "AI_GO.core.continuity_weighting.continuity_weighting_record",
                    ["build_continuity_weighting_record"],
                    persist=True,
                ),
            ),
            (
                "continuity_weighting_refinement_bridge",
                lambda: self._call_function(
                    "AI_GO.core.refinement.continuity_weighting_bridge",
                    ["generate_and_persist_continuity_weighting_refinement_packet"],
                ),
            ),
            (
                "refinement_to_pm_bridge",
                lambda: self._call_function(
                    "AI_GO.core.refinement.refinement_to_pm_bridge",
                    ["generate_and_persist_pm_refinement_intake_record"],
                ),
            ),
            (
                "visibility_generation",
                lambda: self._call_function(
                    "AI_GO.core.visibility.visibility_router",
                    ["build_system_eyes_packet"],
                ),
            ),
        ]

    def run_once(self, iteration: int = 1) -> CycleRunResult:
        started_at = utc_now_iso()
        cycle_id = f"system_cycle_{started_at.replace(':', '-')}_{iteration}"

        step_results: list[StepResult] = []

        for step_name, callable_ref in self._build_steps():
            self._log(f"[SYSTEM CYCLE] running {step_name}")
            result = self._run_step(step_name=step_name, callable_ref=callable_ref)
            step_results.append(result)

            if result.status != "passed" and self.stop_on_error:
                break

        ended_at = utc_now_iso()
        status = (
            "passed"
            if all(step.status == "passed" for step in step_results)
            else "failed"
        )

        cycle_result = CycleRunResult(
            cycle_id=cycle_id,
            started_at=started_at,
            ended_at=ended_at,
            status=status,
            mode="once" if self.once else "loop",
            iteration=iteration,
            steps=step_results,
            project_root=str(self.project_root),
            receipts_dir=str(self.receipts_root),
            current_status_path=str(self.current_status_path),
        )

        self.persist_cycle_result(cycle_result)
        return cycle_result

    def persist_cycle_result(self, result: CycleRunResult) -> dict[str, Any]:
        payload = asdict(result)
        payload["artifact_type"] = "system_cycle_result"
        payload["sealed"] = True

        latest_path = _governed_write(
            path=self.current_status_path,
            payload=payload,
            persistence_type=PERSISTENCE_TYPE_STATUS,
        )

        receipt_path = _governed_write(
            path=self.receipts_root / f"{result.cycle_id}.json",
            payload=payload,
            persistence_type=PERSISTENCE_TYPE_RECEIPT,
            mutation_class="receipt",
        )

        return {
            "status": "persisted",
            "latest_path": latest_path,
            "receipt_path": receipt_path,
        }

    def run(self) -> list[CycleRunResult]:
        results: list[CycleRunResult] = []
        iteration = 1

        while True:
            result = self.run_once(iteration=iteration)
            results.append(result)

            if self.once:
                break

            if self.iterations is not None and iteration >= self.iterations:
                break

            iteration += 1
            time.sleep(self.interval_seconds)

        return results


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AI_GO governed system cycle.")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--iterations", type=int, default=None)
    parser.add_argument("--interval-seconds", type=int, default=300)
    parser.add_argument("--live-request-json", default=None)
    parser.add_argument("--live-request-file", default=None)
    parser.add_argument("--enable-live-trigger", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    cycle = SystemCycle(
        interval_seconds=args.interval_seconds,
        once=args.once or args.iterations == 1,
        iterations=args.iterations,
        live_request_json=args.live_request_json,
        live_request_file=args.live_request_file,
        enable_live_trigger=args.enable_live_trigger,
        stop_on_error=args.stop_on_error,
        quiet=args.quiet,
    )

    results = cycle.run()
    final = asdict(results[-1]) if results else {"status": "not_run"}
    print(json.dumps(final, indent=2, ensure_ascii=False))
    return 0 if final.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))