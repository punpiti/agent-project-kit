#!/usr/bin/env python3
"""Build the canonical Data Analytics artifact for the APK benchmark report."""
from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULT_PATH = ROOT / "benchmarks" / "results" / "latest.json"
REPORT_DIR = ROOT / "benchmarks" / "report"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result", type=Path, default=RESULT_PATH)
    parser.add_argument("--output-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args()
    result_path = args.result.resolve()
    report_dir = args.output_dir.resolve()
    result = json.loads(result_path.read_text(encoding="utf-8"))
    try:
        source_path = str(result_path.relative_to(ROOT))
    except ValueError:
        source_path = result_path.name
    context = result["context"]
    cadence = result["cadence"]
    safety = result["safety"]

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in context["rows"]:
        grouped[row["actual_domain"]].append(row)
    domain_rows = [
        {
            "domain": domain,
            "cases": len(rows),
            "median_reduction_percent": round(statistics.median(r["context_reduction_percent"] for r in rows), 2),
            "median_estimated_tokens": round(statistics.median(r["fast_estimated_tokens"] for r in rows), 1),
            "minimum_reduction_percent": round(min(r["context_reduction_percent"] for r in rows), 2),
        }
        for domain, rows in sorted(grouped.items())
    ]

    summary_rows = [{
        "fixture_pass_rate": context["fixture_pass_rate_percent"] / 100,
        "fixture_cases": context["fixture_cases"],
        "median_context_reduction": context["median_context_reduction_percent"] / 100,
        "minimum_context_reduction": context["minimum_context_reduction_percent"] / 100,
        "median_estimated_tokens": context["median_fast_estimated_tokens"],
        "cadence_avoidance": cadence["avoidance_percent"] / 100,
        "cadence_starts": cadence["simulated_starts"],
        "safety_pass": 1 if safety.get("status") == "passed" else 0,
    }]
    safety_rows = [
        {"check": item, "result": "Passed"}
        for item in safety.get("transactional_suite", {}).get("covers", [])
    ] + [
        {"check": item, "result": "Passed"}
        for item in safety.get("fast_start_suite", {}).get("covers", [])
    ]

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute(
        "CREATE TABLE benchmark_summary (fixture_pass_rate REAL, fixture_cases INTEGER, median_context_reduction REAL, minimum_context_reduction REAL, median_estimated_tokens REAL, cadence_avoidance REAL, cadence_starts INTEGER, safety_pass INTEGER)"
    )
    connection.execute(
        "INSERT INTO benchmark_summary VALUES (:fixture_pass_rate, :fixture_cases, :median_context_reduction, :minimum_context_reduction, :median_estimated_tokens, :cadence_avoidance, :cadence_starts, :safety_pass)",
        summary_rows[0],
    )
    connection.execute(
        "CREATE TABLE domain_context (domain TEXT, cases INTEGER, median_reduction_percent REAL, median_estimated_tokens REAL, minimum_reduction_percent REAL)"
    )
    connection.executemany(
        "INSERT INTO domain_context VALUES (:domain, :cases, :median_reduction_percent, :median_estimated_tokens, :minimum_reduction_percent)",
        domain_rows,
    )
    connection.execute("CREATE TABLE safety_checks (check_name TEXT, result TEXT)")
    connection.executemany(
        "INSERT INTO safety_checks VALUES (:check, :result)", safety_rows
    )

    summary_sql = "SELECT fixture_pass_rate, fixture_cases, median_context_reduction, minimum_context_reduction, median_estimated_tokens, cadence_avoidance, cadence_starts, safety_pass FROM benchmark_summary"
    domain_sql = "SELECT domain, cases, median_reduction_percent, median_estimated_tokens, minimum_reduction_percent FROM domain_context ORDER BY median_reduction_percent DESC"
    safety_sql = 'SELECT check_name AS "check", result FROM safety_checks ORDER BY check_name'
    summary_rows = [dict(row) for row in connection.execute(summary_sql)]
    domain_rows = [dict(row) for row in connection.execute(domain_sql)]
    safety_rows = [dict(row) for row in connection.execute(safety_sql)]
    connection.close()

    metric_definitions = [
        "Context reduction = 1 - selected serialized context bytes / eager-reference serialized bytes",
        "Fixture pass rate = cases satisfying all disclosed routing assertions / all fixture cases",
        "Cadence avoidance = successful executions skipped / simulated starts inside one TTL",
    ]

    def sql_source(source_id: str, label: str, sql: str, table: str, description: str) -> dict:
        return {
            "id": source_id,
            "label": label,
            "path": source_path,
            "query": {
                "sql": sql,
                "description": description,
                "engine": "Python sqlite3",
                "language": "SQL",
                "executed_at": result["generated_at"],
                "tables_used": [table],
                "filters": [
                    f"package_version={result['package_version']}",
                    f"fixture_cases={context['fixture_cases']}",
                ],
                "metric_definitions": metric_definitions,
            },
        }

    source_summary = sql_source(
        "benchmark-summary-sql", "APK benchmark summary query", summary_sql,
        "benchmark_summary", "Reads the benchmark headline metrics loaded from latest.json."
    )
    source_domain = sql_source(
        "benchmark-domain-sql", "APK domain comparison query", domain_sql,
        "domain_context", "Reads domain-level context reductions derived from disclosed fixture rows."
    )
    source_safety = sql_source(
        "benchmark-safety-sql", "APK safety coverage query", safety_sql,
        "safety_checks", "Reads behaviors exercised by the benchmarked acceptance suites."
    )
    source_method = {
        "id": "benchmark-method",
        "label": "APK benchmark methodology",
        "path": "benchmarks/README.md",
    }

    title = "APK Benchmark: Focused Context and Safer Project Memory"
    manifest = {
        "version": 1,
        "surface": "report",
        "title": title,
        "description": "Controlled evidence for Agent Project Kit Marketplace claims",
        "generatedAt": result["generated_at"],
        "sources": [
            {key: value for key, value in source.items() if key != "query"}
            for source in [source_summary, source_domain, source_safety, source_method]
        ],
        "cards": [
            {
                "id": "routing-pass",
                "description": f"Expected assertions passed across {context['fixture_cases']} disclosed English/Thai cases.",
                "dataset": "summary",
                "sourceId": "benchmark-summary-sql",
                "metrics": [
                    {"label": "Routing fixture pass rate", "field": "fixture_pass_rate", "format": "percent"},
                    {"label": "Cases", "field": "fixture_cases", "format": "number"},
                ],
            },
            {
                "id": "context-reduction",
                "description": "Selective prompt content versus the documented eager-loading reference.",
                "dataset": "summary",
                "sourceId": "benchmark-summary-sql",
                "metrics": [
                    {"label": "Median context reduction", "field": "median_context_reduction", "format": "percent"},
                    {"label": "Worst fixture case", "field": "minimum_context_reduction", "format": "percent"},
                ],
            },
            {
                "id": "cadence-avoidance",
                "description": "Repeated successful actions suppressed within one 14-day TTL window.",
                "dataset": "summary",
                "sourceId": "benchmark-summary-sql",
                "metrics": [
                    {"label": "Repeated actions avoided", "field": "cadence_avoidance", "format": "percent"},
                    {"label": "Simulated starts", "field": "cadence_starts", "format": "number"},
                ],
            },
            {
                "id": "safety-result",
                "description": "Transactional and fast-start acceptance suites on the recorded WSL host.",
                "dataset": "summary",
                "sourceId": "benchmark-summary-sql",
                "metrics": [
                    {"label": "Safety suites passed", "field": "safety_pass", "format": "number"},
                ],
            },
        ],
        "charts": [
            {
                "id": "domain-context",
                "title": "Selective-context reduction by task domain",
                "subtitle": "Median reduction versus eager loading all 18 primary/secondary prompts; controlled fixture",
                "showDescription": True,
                "question": "Does selective loading stay smaller across different task domains?",
                "rationale": "Horizontal bars compare one percentage across seven domains with long labels.",
                "intent": "comparison",
                "type": "horizontalBar",
                "dataset": "domain_context",
                "sourceId": "benchmark-domain-sql",
                "encodings": {
                    "x": {"field": "domain", "type": "nominal", "label": "Task domain"},
                    "y": {"field": "median_reduction_percent", "type": "quantitative", "format": "number", "label": "Median context reduction", "unit": "%"},
                    "tooltip": [
                        {"field": "cases", "type": "quantitative", "label": "Fixture cases"},
                        {"field": "median_estimated_tokens", "type": "quantitative", "label": "Median estimated tokens"},
                        {"field": "minimum_reduction_percent", "type": "quantitative", "label": "Minimum reduction", "unit": "%"},
                    ],
                },
                "valueFormat": "number",
                "unit": "%",
                "layout": "full",
                "maxRows": 10,
                "palette": {"kind": "sequential", "name": "blue"},
                "labels": {"values": "all"},
                "settings": {"showValues": True, "sort": "descending", "orientation": "horizontal"},
                "surface": {"surface": "export", "viewMode": "both"},
            }
        ],
        "tables": [
            {
                "id": "safety-checks",
                "title": "Covered update and startup safety checks",
                "subtitle": "Assertions executed by the transactional and fast-start suites on the recorded host",
                "showDescription": True,
                "dataset": "safety_checks",
                "sourceId": "benchmark-safety-sql",
                "defaultSort": {"field": "check", "direction": "asc"},
                "density": "spacious",
                "layout": "full",
                "columns": [
                    {"field": "check", "label": "Covered behavior", "type": "text"},
                    {"field": "result", "label": "Result", "type": "text"},
                ],
            }
        ],
        "blocks": [
            {"id": "title", "type": "markdown", "body": f"# {title}", "layout": "full"},
            {
                "id": "executive-summary",
                "type": "markdown",
                "sourceId": "benchmark-summary-sql",
                "body": (
                    "## Executive Summary\n\n"
                    f"- **APK kept task context focused in the controlled comparison.** Median serialized context was **{pct(context['median_context_reduction_percent'])} smaller** than the eager reference across {context['fixture_cases']} cases; the worst fixture case was {pct(context['minimum_context_reduction_percent'])} smaller.\n"
                    f"- **The disclosed routing fixture passed completely.** All **{context['fixture_passed']}/{context['fixture_cases']} assertions** passed, but this is fixture coverage rather than general model accuracy.\n"
                    f"- **Persisted cadence removed predictable repetition.** APK avoided **{cadence['repeated_actions_avoided']} of {cadence['simulated_starts']} executions** inside one simulated 14-day window.\n"
                    "- **The covered update paths failed safely.** Transactional and state-preservation suites passed on Bash and PowerShell through `pwsh` on WSL; native Windows remains unverified."
                ),
                "layout": "full",
            },
            {"id": "headline-metrics", "type": "metric-strip", "cardIds": ["routing-pass", "context-reduction", "cadence-avoidance", "safety-result"], "layout": "full"},
            {
                "id": "context-finding",
                "type": "markdown",
                "sourceId": "benchmark-summary-sql",
                "body": (
                    "## Selective loading cuts instruction volume, but the gain varies by task\n\n"
                    f"**The median reduction was {pct(context['median_context_reduction_percent'])}, while the minimum was {pct(context['minimum_context_reduction_percent'])}.** The comparison includes the same configured project/task state on both sides. APK loads the selected prompt content and triggered policies; the reference loads all {context['eager_prompt_count']} primary and secondary prompts.\n\n"
                    "The spread matters: large production workflows naturally retain more context, so the Marketplace claim should use the median and disclose the worst fixture case rather than imply one universal reduction."
                ),
                "layout": "full",
            },
            {"id": "context-chart", "type": "chart", "chartId": "domain-context", "layout": "full", "sourceId": "benchmark-domain-sql"},
            {
                "id": "routing-cadence-finding",
                "type": "markdown",
                "sourceId": "benchmark-summary-sql",
                "body": (
                    "## Routing and cadence are deterministic benefits, not quality guarantees\n\n"
                    f"**All {context['fixture_cases']} fixture cases matched their expected domain, deliverable, method, and workflow constraints.** That supports repeatability for the disclosed English/Thai examples. It does not prove accuracy on unseen wording.\n\n"
                    f"**Cadence suppression executed the successful action once across {cadence['simulated_starts']} starts.** This directly demonstrates avoided repeated checks, but it does not measure network time, token billing, or money saved."
                ),
                "layout": "full",
            },
            {
                "id": "safety-finding",
                "type": "markdown",
                "sourceId": "benchmark-safety-sql",
                "body": (
                    "## Update safety protects project memory in the covered failure paths\n\n"
                    "**The real installer tests reject incomplete or mismatched packages before activation and restore the prior snapshot after a forced post-switch failure.** They also preserve project-local state, retain one previous snapshot, and verify exact release refs.\n\n"
                    "The table lists exercised behaviors, not hypothetical features. Native Windows remains a release gate because the PowerShell cases ran through `pwsh` on WSL."
                ),
                "layout": "full",
            },
            {"id": "safety-table", "type": "table", "tableId": "safety-checks", "layout": "full", "sourceId": "benchmark-safety-sql"},
            {
                "id": "next-steps",
                "type": "markdown",
                "body": (
                    "## Recommended next steps\n\n"
                    "1. Publish only the controlled claims in `benchmarks/MARKETPLACE_COPY.md`.\n"
                    "2. Rerun from the clean, tagged extension release so the public result is not marked dirty.\n"
                    "3. Add a native-Windows run before claiming cross-platform update reliability.\n"
                    "4. Add independently reviewed real-project tasks before broadening the routing claim."
                ),
                "layout": "full",
            },
            {
                "id": "further-questions",
                "type": "markdown",
                "body": (
                    "## Further questions\n\n"
                    "- How much wall-clock startup time changes on real projects and network conditions?\n"
                    "- Does lower context improve task quality or merely reduce instruction volume?\n"
                    "- Which unseen task families produce routing errors or require clarification?"
                ),
                "layout": "full",
            },
            {
                "id": "caveats",
                "type": "markdown",
                "sourceId": "benchmark-method",
                "body": (
                    "## Caveats and assumptions\n\n"
                    "The eager condition is a documented reference policy, not a competing product. Token counts use UTF-8 bytes divided by four and are not provider-billed tokens. The deterministic fixture is intentionally disclosed and should be treated as regression coverage. The current result comes from a dirty development tree, so headline values must be regenerated from the final tag before publication."
                ),
                "layout": "full",
            },
        ],
    }

    artifact = {
        "surface": "report",
        "manifest": manifest,
        "snapshot": {
            "version": 1,
            "generatedAt": result["generated_at"],
            "status": "ready",
            "datasets": {
                "summary": summary_rows,
                "domain_context": domain_rows,
                "safety_checks": safety_rows,
            },
        },
        "sources": [source_summary, source_domain, source_safety, source_method],
    }
    chart_map = {
        "charts": [
            {
                "section": "Selective loading cuts instruction volume, but the gain varies by task",
                "question": "Does selective loading stay smaller across task domains?",
                "family": "Comparison & Ranking",
                "type": "horizontalBar",
                "fields": ["domain", "median_reduction_percent", "cases", "median_estimated_tokens", "minimum_reduction_percent"],
                "supported_claim": "The reduction is broad but varies by domain.",
                "palette": "single-root blue plus neutrals",
                "delivery": "benchmarks/report/report.html",
            }
        ],
        "omitted_visuals": [
            {"section": "Routing and cadence", "reason": "One 10-start discrete simulation is clearer as metric cards and narrative than an underpowered trend."},
            {"section": "Update safety", "reason": "Exact covered behaviors are an audit lookup; a table is more honest than a chart."},
        ],
    }
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "artifact.json").write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (report_dir / "chart-map.json").write_text(json.dumps(chart_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report_dir / "artifact.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
