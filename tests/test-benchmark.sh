#!/usr/bin/env bash
set -euo pipefail

SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

python3 "$SOURCE/benchmarks/run_benchmark.py" \
  --skip-safety --output-dir "$TEST_ROOT/results" \
  --marketplace-copy "$TEST_ROOT/MARKETPLACE_COPY.md" >/dev/null

python3 - "$TEST_ROOT/results/latest.json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1],encoding="utf-8"))
context=data["context"]
assert context["fixture_cases"] >= 25
assert context["fixture_passed"] == context["fixture_cases"]
assert context["median_context_reduction_percent"] > 50
assert context["maximum_secondary_modules"] <= 2
assert data["cadence"]["simulated_starts"] == 10
assert data["cadence"]["expensive_action_executions"] == 1
assert data["safety"]["status"] == "skipped"
PY

python3 "$SOURCE/benchmarks/build_report.py" \
  --result "$TEST_ROOT/results/latest.json" \
  --output-dir "$TEST_ROOT/report" >/dev/null

test -s "$TEST_ROOT/results/latest.csv"
test -s "$TEST_ROOT/results/latest.md"
test -s "$TEST_ROOT/report/artifact.json"
test -s "$TEST_ROOT/report/chart-map.json"
grep -q 'fixture assertions' "$TEST_ROOT/MARKETPLACE_COPY.md"
grep -q 'working_tree_dirty=' "$TEST_ROOT/MARKETPLACE_COPY.md"

echo 'benchmark smoke tests: PASS'
