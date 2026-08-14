#!/usr/bin/env python3
"""Run reproducible Agent Project Kit value benchmarks.

The benchmark compares APK's selective context compiler with a documented
eager-loading reference, exercises persisted cadence behavior, and runs the
real transactional/state-preservation acceptance suites. It does not measure
model answer quality or claim causal productivity gains.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = ROOT / "benchmarks" / "cases.json"


def run(command: list[str], *, cwd: Path = ROOT, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode and not allow_failure:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {' '.join(command)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def compact_json_bytes(value: object) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def eager_reference(project_state: dict, task_state: dict) -> tuple[int, list[str]]:
    catalog = json.loads((ROOT / "prompts" / "catalog.json").read_text(encoding="utf-8"))
    prompt_paths = [
        ROOT / "prompts" / item["path"]
        for item in catalog["prompts"]
        if item.get("type") in {"primary", "secondary"}
    ]
    payload = {
        "project_context": [project_state, task_state],
        "prompts": [
            {"path": str(path.relative_to(ROOT)), "content": path.read_text(encoding="utf-8")}
            for path in prompt_paths
        ],
    }
    return compact_json_bytes(payload), [str(path.relative_to(ROOT)) for path in prompt_paths]


def validate_case(case: dict, route: dict) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if route["domain"] != case["domain"]:
        issues.append(f"domain={route['domain']} expected={case['domain']}")
    if route["deliverable"] != case["deliverable"]:
        issues.append(f"deliverable={route['deliverable']} expected={case['deliverable']}")
    missing_methods = sorted(set(case.get("required_methods", [])) - set(route["methods"]))
    if missing_methods:
        issues.append(f"missing methods={missing_methods}")
    missing_workflows = sorted(set(case.get("required_workflows", [])) - set(route["secondary_workflows"]))
    if missing_workflows:
        issues.append(f"missing workflows={missing_workflows}")
    forbidden = sorted(set(case.get("forbidden_workflows", [])) & set(route["secondary_workflows"]))
    if forbidden:
        issues.append(f"forbidden workflows={forbidden}")
    return not issues, issues


def context_benchmark() -> dict:
    fixture = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    project_state = {
        "schema_version": 1,
        "status": "configured",
        "name": "Benchmark fixture",
        "objective": "Measure selective task context",
    }
    task_state = {
        "schema_version": 1,
        "status": "configured",
        "active_task": "benchmark",
        "next_actions": [],
    }
    eager_bytes, eager_prompts = eager_reference(project_state, task_state)
    rows = []
    with tempfile.TemporaryDirectory(prefix="apk-benchmark-context-") as tmp:
        project = Path(tmp)
        (project / ".ai").mkdir()
        (project / ".ai" / "project.json").write_text(json.dumps(project_state), encoding="utf-8")
        (project / ".ai" / "state.json").write_text(json.dumps(task_state), encoding="utf-8")
        for case in fixture["cases"]:
            route_result = run([sys.executable, str(ROOT / "scripts" / "route_task.py"), case["request"]])
            route = json.loads(route_result.stdout)
            passed, issues = validate_case(case, route)
            context_result = run(
                [sys.executable, str(ROOT / "scripts" / "context.py"), case["request"], "--project", str(project)],
                allow_failure=True,
            )
            if context_result.returncode not in (0, 2):
                raise RuntimeError(context_result.stderr or context_result.stdout)
            bundle = json.loads(context_result.stdout)
            selected_paths = []
            if bundle.get("primary", {}).get("prompt"):
                selected_paths.append(bundle["primary"]["prompt"])
            selected_paths.extend(item["prompt"] for item in bundle.get("secondary", []) if item.get("prompt"))
            fast_payload = {
                "project_context": [project_state, task_state],
                "policies": bundle.get("policies", []),
                "prompts": [
                    {"path": path, "content": (ROOT / path).read_text(encoding="utf-8")}
                    for path in selected_paths
                ],
            }
            fast_bytes = compact_json_bytes(fast_payload)
            rows.append(
                {
                    "request": case["request"],
                    "expected_domain": case["domain"],
                    "actual_domain": route["domain"],
                    "expected_deliverable": case["deliverable"],
                    "actual_deliverable": route["deliverable"],
                    "fixture_pass": passed,
                    "issues": issues,
                    "fast_context_bytes": fast_bytes,
                    "fast_estimated_tokens": fast_bytes // 4,
                    "compiler_envelope_bytes": int(bundle["metrics"]["bytes"]),
                    "selected_prompt_paths": selected_paths,
                    "eager_reference_bytes": eager_bytes,
                    "eager_estimated_tokens": eager_bytes // 4,
                    "context_reduction_percent": round((1 - fast_bytes / eager_bytes) * 100, 2),
                    "primary_modules": int(bundle["metrics"]["primary_modules"]),
                    "secondary_modules": int(bundle["metrics"]["secondary_modules"]),
                    "needs_clarification": bool(route["needs_clarification"]),
                }
            )
    reductions = [row["context_reduction_percent"] for row in rows]
    fast_tokens = [row["fast_estimated_tokens"] for row in rows]
    return {
        "definition": {
            "selective": "One compiled primary route, up to two triggered secondary workflows, and configured project/task state.",
            "reference": "The same configured state plus every catalog entry classified as primary or secondary; one-time and legacy-reference prompts are excluded.",
            "token_estimate": "UTF-8 serialized bytes divided by four; this is a planning estimate, not provider-billed token usage.",
        },
        "fixture_cases": len(rows),
        "fixture_passed": sum(row["fixture_pass"] for row in rows),
        "fixture_pass_rate_percent": round(100 * sum(row["fixture_pass"] for row in rows) / len(rows), 2),
        "eager_prompt_count": len(eager_prompts),
        "eager_prompt_paths": eager_prompts,
        "eager_reference_bytes": eager_bytes,
        "median_fast_estimated_tokens": round(statistics.median(fast_tokens), 1),
        "p95_fast_estimated_tokens": round(percentile(fast_tokens, 0.95), 1),
        "median_context_reduction_percent": round(statistics.median(reductions), 2),
        "minimum_context_reduction_percent": round(min(reductions), 2),
        "maximum_secondary_modules": max(row["secondary_modules"] for row in rows),
        "rows": rows,
    }


def cadence_benchmark(starts: int = 10) -> dict:
    with tempfile.TemporaryDirectory(prefix="apk-benchmark-cadence-") as tmp:
        project = Path(tmp)
        (project / ".ai").mkdir()
        counter = project / "counter.txt"
        command = [
            sys.executable,
            str(ROOT / "scripts" / "run-once.py"),
            "--project",
            str(project),
            "--key",
            "benchmark-update-notice",
            "--ttl-days",
            "14",
            "--quiet-valid",
            "--",
            "sh",
            "-c",
            f"printf x >> {counter}",
        ]
        for _ in range(starts):
            run(command)
        executions = len(counter.read_text(encoding="utf-8"))
    return {
        "simulated_starts": starts,
        "expensive_action_executions": executions,
        "repeated_actions_avoided": starts - executions,
        "avoidance_percent": round(100 * (starts - executions) / starts, 2),
        "ttl_days": 14,
        "definition": "Ten starts occur inside one valid 14-day persisted cadence window; the command appends one byte whenever it really executes.",
    }


def safety_benchmark(skip: bool) -> dict:
    if skip:
        return {"status": "skipped", "reason": "--skip-safety was used"}
    transactional = run(["bash", str(ROOT / "tests" / "test-transactional-update.sh")], allow_failure=True)
    fast_start = run(["bash", str(ROOT / "tests" / "test-fast-start.sh")], allow_failure=True)
    return {
        "status": "passed" if transactional.returncode == 0 and fast_start.returncode == 0 else "failed",
        "transactional_suite": {
            "passed": transactional.returncode == 0,
            "covers": [
                "incomplete source rejected before active snapshot changes",
                "successful staged swap retains a previous snapshot",
                "post-swap failure restores snapshot, metadata, and control files",
                "project state survives update and rollback",
                "manifest git_ref wins when main advances",
                "advertised-version mismatch is rejected",
                "Bash and PowerShell installer paths execute under the current WSL test host",
            ],
            "stdout_tail": transactional.stdout.strip().splitlines()[-1:] or [],
            "stderr_tail": transactional.stderr.strip().splitlines()[-3:] or [],
        },
        "fast_start_suite": {
            "passed": fast_start.returncode == 0,
            "covers": [
                "project-local state preservation",
                "managed AGENTS block idempotency",
                "failed run-once commands are not cached",
                "manifest notice never installs package files",
            ],
            "stdout_tail": fast_start.stdout.strip().splitlines()[-1:] or [],
            "stderr_tail": fast_start.stderr.strip().splitlines()[-3:] or [],
        },
        "native_windows_verified": False,
        "native_windows_caveat": "PowerShell paths ran with pwsh on WSL; the result is not native-Windows certification.",
    }


def git_metadata() -> dict:
    commit = run(["git", "rev-parse", "HEAD"], allow_failure=True)
    status = run(["git", "status", "--porcelain"], allow_failure=True)
    return {
        "commit": commit.stdout.strip() if commit.returncode == 0 else "unknown",
        "working_tree_dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def metric_rows(result: dict) -> list[dict]:
    context = result["context"]
    cadence = result["cadence"]
    safety = result["safety"]
    return [
        {
            "metric": "Controlled routing fixture pass rate",
            "value": context["fixture_pass_rate_percent"],
            "unit": "%",
            "denominator": context["fixture_cases"],
            "claim_scope": "Bundled bilingual fixture only",
        },
        {
            "metric": "Median selective-context reduction",
            "value": context["median_context_reduction_percent"],
            "unit": "%",
            "denominator": context["fixture_cases"],
            "claim_scope": "Versus documented eager prompt-loading reference",
        },
        {
            "metric": "Maximum secondary workflows loaded",
            "value": context["maximum_secondary_modules"],
            "unit": "modules",
            "denominator": context["fixture_cases"],
            "claim_scope": "Controlled fixture",
        },
        {
            "metric": "Repeated cadence actions avoided",
            "value": cadence["avoidance_percent"],
            "unit": "%",
            "denominator": cadence["simulated_starts"],
            "claim_scope": "Ten starts inside one 14-day TTL window",
        },
        {
            "metric": "Transactional safety suites",
            "value": 1 if safety.get("status") == "passed" else 0,
            "unit": "pass",
            "denominator": 1,
            "claim_scope": "Local WSL host; native Windows excluded",
        },
    ]


def render_markdown(result: dict) -> str:
    context = result["context"]
    cadence = result["cadence"]
    safety = result["safety"]
    safety_text = "passed" if safety.get("status") == "passed" else safety.get("status", "unknown")
    return f"""# Agent Project Kit benchmark results

Generated: {result['generated_at']}<br>
Package: `{result['package_version']}`<br>
Commit: `{result['git']['commit']}`<br>
Working tree dirty: `{str(result['git']['working_tree_dirty']).lower()}`

## Results

| Measure | Result | Scope |
|---|---:|---|
| Controlled routing fixture | {context['fixture_passed']}/{context['fixture_cases']} ({context['fixture_pass_rate_percent']:.1f}%) | Bundled English/Thai cases; not real-world accuracy |
| Median selective-context reduction | {context['median_context_reduction_percent']:.1f}% | Versus eager loading every primary/secondary prompt |
| Minimum selective-context reduction | {context['minimum_context_reduction_percent']:.1f}% | Worst case in the controlled fixture |
| Median selective context | {context['median_fast_estimated_tokens']:.0f} estimated tokens | UTF-8 bytes / 4, not billed usage |
| Secondary workflow cap observed | {context['maximum_secondary_modules']} | Controlled fixture |
| Repeated cadence actions avoided | {cadence['repeated_actions_avoided']}/{cadence['simulated_starts']} ({cadence['avoidance_percent']:.1f}%) | Ten starts within a 14-day TTL |
| Transactional/state safety suites | {safety_text} | Bash + PowerShell via pwsh on WSL; native Windows not certified |

## What the evidence supports

- APK can materially reduce the instruction context assembled for these tasks compared with an eager-load policy.
- The deterministic router satisfies all expected assertions in the bundled fixture.
- Persisted cadence prevents repeated successful checks inside the configured TTL.
- The tested installer paths preserve project state and recover from the covered update failures.

## What it does not support

- No claim that APK improves model answer quality by a specific percentage.
- No claim that the fixture pass rate generalizes to every prompt or project.
- No claim of measured human time savings, cost savings, or native-Windows reliability yet.

See `benchmarks/README.md` for definitions and `benchmarks/results/latest.json` for case-level evidence.
"""


def render_marketplace_copy(result: dict) -> str:
    context = result["context"]
    cadence = result["cadence"]
    return f"""# Marketplace benchmark copy

## Evidence-backed short version

Agent Project Kit keeps AI workspace context focused and project memory durable. In the bundled {context['fixture_cases']}-case English/Thai routing benchmark, APK loaded one primary route and no more than {context['maximum_secondary_modules']} secondary workflows while reducing serialized task context by a median of **{context['median_context_reduction_percent']:.1f}%** versus an eager policy that loads every primary and secondary prompt. All **{context['fixture_passed']}/{context['fixture_cases']} fixture assertions passed**.

Persisted cadence also avoided **{cadence['repeated_actions_avoided']} of {cadence['simulated_starts']} repeated checks** inside a simulated 14-day window. Transactional update tests verified staged SHA-256 checks, project-state preservation, exact release refs, retained previous snapshots, and automatic rollback on the tested Bash and PowerShell paths.

## Suggested Marketplace bullets

- **Loads only task-relevant guidance:** median {context['median_context_reduction_percent']:.1f}% less serialized context than the documented eager-loading reference across {context['fixture_cases']} controlled cases.
- **Routes repeatably:** {context['fixture_passed']}/{context['fixture_cases']} expected English/Thai routing assertions passed in the bundled fixture.
- **Avoids repeated startup work:** {cadence['avoidance_percent']:.0f}% of repeated cadence-controlled actions were skipped across ten starts inside one TTL window.
- **Protects project memory:** update tests preserve project-local state and retain a recoverable previous snapshot.
- **Fails safely:** incomplete, mismatched, or post-switch failures are rejected or rolled back in the covered installer tests.

## Required footnote

Benchmark results are from the repository's controlled fixture on `{result['host']['system']} / {result['host']['machine']}` at commit `{result['git']['commit'][:12]}`. Context reduction is measured against the documented eager-loading reference, not against another product. Token counts are byte-based estimates. Routing results are fixture assertions, not general model-accuracy claims. PowerShell ran through `pwsh` on WSL; native Windows remains a separate validation gate.

Publication status: `working_tree_dirty={str(result['git']['working_tree_dirty']).lower()}`. Regenerate from the clean tagged Marketplace release before publishing headline values.

## README placement

Place the short version after the feature overview, then link to:

- `benchmarks/results/latest.md` for the readable result
- `benchmarks/results/latest.json` for case-level evidence
- `benchmarks/README.md` for methodology and rerun instructions

VS Code Marketplace renders the extension root `README.md`; use HTTPS for remote images and keep benchmark claims in normal Markdown text.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "results")
    parser.add_argument("--marketplace-copy", type=Path, default=ROOT / "benchmarks" / "MARKETPLACE_COPY.md")
    parser.add_argument("--skip-safety", action="store_true", help="Skip slower installer acceptance suites")
    args = parser.parse_args()

    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    result = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package_version": manifest["version"],
        "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "git": git_metadata(),
        "context": context_benchmark(),
        "cadence": cadence_benchmark(),
        "safety": safety_benchmark(args.skip_safety),
    }
    result["metrics"] = metric_rows(result)

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "latest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "latest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["metric", "value", "unit", "denominator", "claim_scope"])
        writer.writeheader()
        writer.writerows(result["metrics"])
    (output / "latest.md").write_text(render_markdown(result), encoding="utf-8")
    args.marketplace_copy.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.marketplace_copy.resolve().write_text(render_marketplace_copy(result), encoding="utf-8")

    print(json.dumps({
        "output": str(output),
        "fixture": f"{result['context']['fixture_passed']}/{result['context']['fixture_cases']}",
        "median_context_reduction_percent": result["context"]["median_context_reduction_percent"],
        "cadence_actions_avoided": result["cadence"]["repeated_actions_avoided"],
        "safety": result["safety"].get("status"),
    }, indent=2))
    benchmark_passed = (
        result["context"]["fixture_passed"] == result["context"]["fixture_cases"]
        and result["cadence"]["expensive_action_executions"] == 1
        and (args.skip_safety or result["safety"].get("status") == "passed")
    )
    return 0 if benchmark_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
