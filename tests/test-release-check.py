#!/usr/bin/env python3
"""Version-consistency and tag invariants of scripts/release_check.py."""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True  # never add caches to the source tree
import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("apk_release_check", ROOT / "scripts" / "release_check.py")
assert spec and spec.loader
release_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_check)

VERSION_FILES = ("manifest.json", "templates/apk.json", "CHANGELOG.md", *release_check.VERSION_LINES)


def fixture() -> Path:
    root = Path(tempfile.mkdtemp(prefix="apk-release-check-"))
    for name in VERSION_FILES:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, root / name)
    # Model a release-ready changelog regardless of what is Unreleased right now.
    changelog = root / "CHANGELOG.md"
    text = changelog.read_text(encoding="utf-8")
    start = text.index("## Unreleased\n") + len("## Unreleased\n")
    changelog.write_text(text[:start] + "\n" + text[text.index("\n## ", start) + 1:], encoding="utf-8")
    return root


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, (path, old)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> None:
    version = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["version"]

    root = fixture()
    try:
        assert release_check.version_errors(root) == [], release_check.version_errors(root)

        edit(root / "README.th.md", f"`{version}`", "`0.0.1-stale`")
        errors = release_check.version_errors(root)
        assert len(errors) == 1 and errors[0].startswith("README.th.md"), errors
        shutil.copy2(ROOT / "README.th.md", root / "README.th.md")

        edit(root / "manifest.json", f'"git_ref": "v{version}"', '"git_ref": "main"')
        assert any("git_ref" in e for e in release_check.version_errors(root))
        shutil.copy2(ROOT / "manifest.json", root / "manifest.json")

        edit(root / "templates/apk.json", f'"{version}"', '"0.0.1-stale"')
        assert any(e.startswith("templates/apk.json") for e in release_check.version_errors(root))
        shutil.copy2(ROOT / "templates/apk.json", root / "templates/apk.json")

        edit(root / "CHANGELOG.md", "## Unreleased\n", "## Unreleased\n\n- pending change\n")
        assert any("Unreleased" in e for e in release_check.version_errors(root))
        edit(root / "CHANGELOG.md", f"## {version}", "## 0.0.0-other")
        assert any("no '## " in e for e in release_check.version_errors(root))
    finally:
        shutil.rmtree(root)

    repo = Path(tempfile.mkdtemp(prefix="apk-release-tag-"))
    try:
        run = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
        run("init", "-q")
        run("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "one")
        assert release_check.tag_errors(repo, "1.0.0") == ["tag v1.0.0 does not exist"]
        run("tag", "v1.0.0")
        assert any("lightweight" in e for e in release_check.tag_errors(repo, "1.0.0"))
        run("tag", "-d", "v1.0.0")
        run("-c", "user.name=t", "-c", "user.email=t@example.invalid", "tag", "-a", "v1.0.0", "-m", "r")
        assert release_check.tag_errors(repo, "1.0.0") == []
        run("-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "two")
        assert release_check.tag_errors(repo, "1.0.0") == ["tag v1.0.0 does not point to HEAD"]
    finally:
        shutil.rmtree(repo)

    print("release check tests: PASS")


if __name__ == "__main__":
    main()
