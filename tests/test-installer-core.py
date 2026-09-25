#!/usr/bin/env python3
"""Rollback invariants of scripts/apk_install.py that shell tests cannot force."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("apk_install", ROOT / "scripts" / "apk_install.py")
assert spec and spec.loader
core = importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)


def installer(root: Path):
    (root / ".ai").mkdir()
    return core.Installer(root, root, "test")


def main() -> None:
    real_replace = core.replace

    # A failed restore must never delete the only good copy in .previous.
    with tempfile.TemporaryDirectory() as tmp:
        inst = installer(Path(tmp))
        inst.previous.mkdir(); (inst.previous / "active.txt").write_text("only copy")
        inst.older_previous.mkdir(); (inst.older_previous / "old.txt").write_text("older")
        inst.had_target = inst.target_moved = inst.previous_rotated = True

        def fail_restore(src, dst):
            if Path(src) == inst.previous:
                raise PermissionError(5, "Access is denied")
            return real_replace(src, dst)
        core.replace = fail_restore
        try:
            inst.rollback()
        finally:
            core.replace = real_replace
        assert (inst.previous / "active.txt").read_text() == "only copy"
        assert (inst.older_previous / "old.txt").is_file()

    # A successful rollback restores active, previous, and control files.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        inst = installer(root)
        (root / "AGENTS.md").write_text("user rules\n")
        inst.backup_controls()
        (root / "AGENTS.md").write_text("half-written\n")
        inst.previous.mkdir(); (inst.previous / "v.txt").write_text("active")
        inst.older_previous.mkdir(); (inst.older_previous / "v.txt").write_text("previous")
        inst.target.mkdir(); (inst.target / "v.txt").write_text("new")
        inst.had_target = inst.target_moved = inst.previous_rotated = inst.snapshot_swapped = True
        inst.rollback()
        inst.cleanup(False)
        assert (inst.target / "v.txt").read_text() == "active"
        assert (inst.previous / "v.txt").read_text() == "previous"
        assert not inst.older_previous.exists()
        assert (root / "AGENTS.md").read_text() == "user rules\n"
        assert not inst.control_backup.exists()

    # Windows sharing violations are retried; other platforms fail fast.
    calls = []
    real_os_replace = core.os.replace

    def flaky(src, dst):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError(32, "in use")
    core.os.replace = flaky
    real_name, real_sleep = core.os.name, core.time.sleep
    try:
        core.os.name = "nt"; core.time.sleep = lambda _s: None
        core.replace(Path("a"), Path("b"))
        assert len(calls) == 3
        calls.clear(); core.os.name = "posix"
        try:
            core.replace(Path("a"), Path("b"))
        except PermissionError:
            assert len(calls) == 1
        else:
            raise AssertionError("posix PermissionError was retried")
    finally:
        core.os.replace, core.os.name, core.time.sleep = real_os_replace, real_name, real_sleep

    print("installer core tests: PASS")


if __name__ == "__main__":
    main()
