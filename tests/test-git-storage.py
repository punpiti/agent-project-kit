#!/usr/bin/env python3
"""Regression tests for keeping APK Git metadata out of cloud drives."""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("apk_update", ROOT / "scripts" / "apk_update.py")
assert SPEC and SPEC.loader
APK_UPDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APK_UPDATE)


with tempfile.TemporaryDirectory() as raw:
    root = Path(raw)
    cloud_project = root / "OneDrive" / "project"
    legacy_git = cloud_project / ".ai" / "agent-project-kit-source" / ".git"
    legacy_git.mkdir(parents=True)
    (legacy_git / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (legacy_git / "objects").mkdir()
    (legacy_git / "objects" / "fixture").write_bytes(b"git-object")

    local_clone = root / "local" / "agent-project-kit"
    local_clone.mkdir(parents=True)
    assert APK_UPDATE.is_cloud_synced_path(cloud_project)
    assert not APK_UPDATE.is_cloud_synced_path(local_clone)

    os.environ["APK_GIT_ROOT"] = str(local_clone)
    assert APK_UPDATE.default_clone_dir(cloud_project) == local_clone.resolve()
    try:
        APK_UPDATE.require_local_git_path(cloud_project / "repo")
    except APK_UPDATE.UpdateError:
        pass
    else:
        raise AssertionError("cloud Git destination should be rejected")

    backup = APK_UPDATE.retire_legacy_cloud_clone(cloud_project, local_clone)
    assert backup and (backup / "HEAD").is_file()
    assert not legacy_git.exists()
    marker = cloud_project / ".ai" / "agent-project-kit-source" / "GIT_METADATA_MIGRATED.txt"
    assert marker.is_file() and str(local_clone) in marker.read_text(encoding="utf-8")

    old_repo = root / "Dropbox" / "old-project"
    subprocess.run(["git", "init", "-q", str(old_repo)], check=True)
    (old_repo / "draft.txt").write_text("uncommitted work\n", encoding="utf-8")
    migrated_repo = root / "local" / "old-project"
    command = [sys.executable, str(ROOT / "scripts" / "migrate_git_out_of_cloud.py"), str(old_repo),
               "--target", str(migrated_repo)]
    preview = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
    assert "Preview only" in preview.stdout and (old_repo / ".git").is_dir()
    subprocess.run([*command, "--apply"], check=True, stdout=subprocess.PIPE)
    assert not (old_repo / ".git").exists()
    assert (migrated_repo / ".git").is_dir()
    assert (migrated_repo / "draft.txt").read_text(encoding="utf-8") == "uncommitted work\n"

print("git storage regression tests: PASS")
