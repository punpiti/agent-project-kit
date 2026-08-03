#!/usr/bin/env python3
"""Check the published manifest and notify without installing anything."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import urllib.request
from pathlib import Path

DEFAULT_MANIFEST = "https://punpiti.github.io/agent-project-kit/manifest.json"


def read_field(path: Path, label: str) -> str:
    if not path.exists():
        return ""
    prefix = f"- {label}:"
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def version_key(value: str) -> tuple[int, int, int]:
    match = re.match(r"^[vV]?(\d+)(?:\.(\d+))?(?:\.(\d+))?", value)
    if not match:
        return (0, 0, 0)
    return tuple(int(part or 0) for part in match.groups())


def has_update(current: str, latest: str, current_updated: str, latest_updated: str) -> bool:
    if not latest or current == latest:
        return False
    current_key, latest_key = version_key(current), version_key(latest)
    if latest_key != current_key:
        return latest_key > current_key
    if latest_updated and current_updated and latest_updated > current_updated:
        return True
    return current != latest


def update_metadata(path: Path, latest: str, source: str) -> None:
    if not path.exists():
        return
    replacements = {
        "Last update check": dt.datetime.now().astimezone().isoformat(),
        "Latest known upstream version": latest,
        "Update check source": source,
    }
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        for label, value in replacements.items():
            if line.startswith(f"- {label}:"):
                lines[index] = f"- {label}: {value}"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=".")
    parser.add_argument("--manifest-url", default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    project = Path(args.project).resolve()
    version_file = project / ".ai" / "COMPUTING_ENVIRONMENT_VERSION.md"
    try:
        with urllib.request.urlopen(args.manifest_url, timeout=10) as response:
            manifest = json.load(response)
    except Exception as exc:
        print(f"Agent Project Kit update check failed: {exc}")
        return 1

    current = read_field(version_file, "Package version") or "none"
    current_updated = read_field(version_file, "Package updated")
    latest = str(manifest.get("version") or "unknown")
    latest_updated = str(manifest.get("updated") or "")
    update_metadata(version_file, latest, args.manifest_url)
    if has_update(current, latest, current_updated, latest_updated):
        print(f"Agent Project Kit update available: {current} -> {latest}")
        print("Preview only: bash .ai/agent-project-kit/scripts/update-from-pages.sh --dry-run .")
        print("No package files were installed or updated.")
    else:
        print(f"Agent Project Kit is current: {current}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
