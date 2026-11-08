#!/usr/bin/env python3
"""Safely migrate an existing Git working tree out of cloud-synced storage.

Dry-run is the default because applying the migration reads the entire working
tree (which may hydrate cloud placeholders) and changes the path users open.
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path


def load_update_module():
    path = Path(__file__).with_name("apk_update.py")
    spec = importlib.util.spec_from_file_location("apk_update_storage", path)
    if not spec or not spec.loader:
        raise RuntimeError(f"Cannot load storage policy helpers: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STORAGE = load_update_module()


def git_root(source: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "--show-toplevel"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"Not a Git working tree: {source}")
    return Path(result.stdout.strip()).resolve()


def default_target(source: Path) -> Path:
    configured = os.environ.get("PROJECT_GIT_ROOT")
    if configured:
        base = Path(configured).expanduser()
    elif os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "git-worktrees"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache") / "git-worktrees"
    return (base / source.name).resolve(strict=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=".")
    parser.add_argument("--target", help="new machine-local working-tree path")
    parser.add_argument("--apply", action="store_true", help="copy, verify, then retire the cloud .git directory")
    args = parser.parse_args()
    try:
        source = git_root(Path(args.source).expanduser().resolve())
        metadata = source / ".git"
        target = (Path(args.target).expanduser().resolve(strict=False)
                  if args.target else default_target(source))
        if not metadata.is_dir():
            raise RuntimeError("Linked worktrees and .git files require manual migration; no files were changed.")
        if not STORAGE.is_cloud_synced_path(source):
            print(f"No migration needed: Git working tree is not under a detected cloud drive: {source}")
            return 0
        STORAGE.require_local_git_path(target)
        if target == source or source in target.parents:
            raise RuntimeError("Target must be outside the source working tree.")
        print("Git cloud-storage migration")
        print(f"Source: {source}")
        print(f"Target: {target}")
        print("Action: copy the complete working tree, verify SHA-256, then remove only source/.git")
        print("Cloud source files remain as a non-Git snapshot.")
        if not args.apply:
            print("Preview only. Re-run with --apply after reviewing cloud hydration/network cost.")
            return 0
        if target.exists():
            raise RuntimeError(f"Target already exists; refusing to merge or overwrite: {target}")
        shutil.copytree(source, target, symlinks=True)
        if STORAGE.tree_digest(source) != STORAGE.tree_digest(target):
            shutil.rmtree(target, ignore_errors=True)
            raise RuntimeError("Copy verification failed; source was preserved and incomplete target removed.")
        check = subprocess.run(["git", "-C", str(target), "status", "--porcelain"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check.returncode:
            shutil.rmtree(target, ignore_errors=True)
            raise RuntimeError("Copied repository failed git status; source was preserved.")
        shutil.rmtree(metadata)
        (source / "GIT_METADATA_MIGRATED.txt").write_text(
            f"Git working tree migrated to machine-local storage:\n{target}\n"
            "This cloud directory is now a non-Git snapshot. Open the local path for future work.\n",
            encoding="utf-8",
        )
        print(f"Migration complete. Open this path for future Git work: {target}")
        return 0
    except (OSError, RuntimeError, STORAGE.UpdateError) as error:
        print(f"Migration failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
