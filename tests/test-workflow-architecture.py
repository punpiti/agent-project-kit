#!/usr/bin/env python3
"""Acceptance tests for Workflow Architecture v2 composition and reachability."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def route(request: str) -> dict:
    output = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts" / "route_task.py"), request], encoding="utf-8"
    )
    return json.loads(output)


def bundle(request: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        (project / ".ai").mkdir()
        (project / ".ai" / "project.json").write_text(
            json.dumps({"schema_version": 1, "status": "configured", "name": "Fixture"}),
            encoding="utf-8",
        )
        output = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "context.py"), request, "--project", str(project)],
            encoding="utf-8",
            capture_output=True,
            check=False,
        )
        assert output.returncode in (0, 2), output.stdout + output.stderr
        return json.loads(output.stdout)


primary_cases = {
    "analyze product metrics and build a dashboard": "data-analytics",
    "conduct thematic content analysis of interview transcripts": "content-analysis",
    "summarize the current situation": "general",
    "draft a policy recommendation using survey data": "educational-policy-development",
    "prepare a presentation for the university council": "presentation",
    "write a literature review for the rainfall paper": "research-activities",
    "implement a responsive website": "software-development-automation",
    "เขียนตำรากลศาสตร์ของไหล": "book-writing",
    "prepare a course exercise and rubric": "course-material-development",
    "prepare an official nomination letter": "administrative-professional-operations",
}
for request, expected in primary_cases.items():
    result = route(request)
    assert result["primary_pipeline"] == expected, (request, result)

policy = route("draft a policy recommendation using survey data")
assert policy["workflow"]["methods"] == ["data-analytics", "strategy"], policy
assert policy["workflow"]["gates"] == ["prose-style"], policy

book = bundle("revise and export the book manuscript to PDF")
assert book["primary"]["id"] == "book-writing", book
assert [item["id"] for item in book["stages"]] == ["publication-production"], book
assert [item["id"] for item in book["gates"]] == ["prose-style"], book
assert book["omitted"] == [], book
assert any("narrowest text/image/ml environment" in policy for policy in book["policies"]), book
assert any("250 MB" in policy and "isolation" in policy for policy in book["policies"]), book

feedback = route("incorporate student feedback into the course")
assert "external-feedback" in feedback["workflow"]["stages"], feedback

markdown = route("clean up and migrate these Markdown files")
assert "markdown-cleanup" in markdown["workflow"]["stages"], markdown

release = route("bump version, tag and release the package")
assert "package-release" in release["workflow"]["stages"], release
assert "release-boundary" in release["workflow"]["gates"], release

crowded = route("implement a responsive web dashboard using data and recommend product strategy")
assert len(crowded["workflow"]["methods"]) == 2, crowded
assert crowded["omitted"] and crowded["omitted"][0]["category"] == "method", crowded

# Prompt reuse across primary/method roles must not duplicate loaded prompt files.
research = bundle("write a literature review for the rainfall paper")
prompts = [research["primary"].get("prompt")] + [item.get("prompt") for item in research["secondary"]]
prompts = [prompt for prompt in prompts if prompt]
assert len(prompts) == len(set(prompts)), research

subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "sync_workflow_registry.py")], check=True
)
subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "check_release_boundary.py")], check=True
)

# Release mode must be able to identify untracked public candidates so a new
# canonical file cannot silently disappear from a tag or package.
boundary_path = ROOT / "scripts" / "check_release_boundary.py"
boundary_spec = importlib.util.spec_from_file_location("apk_release_boundary", boundary_path)
assert boundary_spec and boundary_spec.loader
boundary = importlib.util.module_from_spec(boundary_spec)
boundary_spec.loader.exec_module(boundary)
with tempfile.TemporaryDirectory() as tmp:
    fixture = Path(tmp)
    subprocess.run(["git", "init", "-q", str(fixture)], check=True)
    (fixture / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(fixture), "add", "tracked.txt"], check=True)
    (fixture / "new-public-file.txt").write_text("candidate\n", encoding="utf-8")
    assert boundary.untracked_files(fixture) == ["new-public-file.txt"]
    assert boundary.has_tracked_changes(fixture, staged=True)
assert boundary.is_private_path(".env")
assert boundary.is_private_path("config/.env.production")
assert not boundary.is_private_path("docs/environment.md")
path_rules = boundary.CONFIG["public_content_patterns"]
sample_home_path = str(Path("/", "home", "example", "project", "file.txt"))
assert any(
    re.search(item["regex"], sample_home_path) for item in path_rules
)
doctor_path = ROOT / "scripts" / "apk_doctor.py"
doctor_spec = importlib.util.spec_from_file_location("apk_doctor", doctor_path)
assert doctor_spec and doctor_spec.loader
doctor = importlib.util.module_from_spec(doctor_spec)
doctor_spec.loader.exec_module(doctor)
with tempfile.TemporaryDirectory() as tmp:
    canonical = Path(tmp)
    (canonical / "manifest.json").write_text("{}", encoding="utf-8")
    (canonical / "START_HERE.md").write_text("start", encoding="utf-8")
    (canonical / ".ai" / "agent-project-kit").mkdir(parents=True)
    (canonical / ".ai" / "agent-project-kit" / "manifest.json").write_text("{}", encoding="utf-8")
    selected, is_canonical = doctor.select_kit_root(canonical)
    assert selected == canonical and is_canonical
assert "<!-- BEGIN COMPUTING-ENVIRONMENT -->" not in (ROOT / "AGENTS.md").read_text(encoding="utf-8")
runbook = (ROOT / "templates" / "RUNBOOK.md").read_text(encoding="utf-8")
assert "python -m venv" not in runbook
assert "micromamba install -n <env>" in runbook
print("workflow architecture v2 tests: PASS")
