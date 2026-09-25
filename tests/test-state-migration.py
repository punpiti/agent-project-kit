#!/usr/bin/env python3
"""Legacy state.json migration follows config/STATE_MIGRATION.md."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = [sys.executable, "-B"]


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(list(args), capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return result


def migrate(project: Path, *flags: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(*PY, str(ROOT / "scripts" / "migrate_state.py"), "--project", str(project), *flags, check=check)


def tree_digest(path: Path) -> str:
    items = sorted((p.relative_to(path).as_posix(), p.read_bytes()) for p in path.rglob("*") if p.is_file())
    return hashlib.sha256(repr(items).encode()).hexdigest()


def install(project: Path) -> None:
    env = {k: v for k, v in os.environ.items() if not k.startswith("APK_")}
    subprocess.run(["bash", str(ROOT / "scripts" / "install-to-project.sh"), str(project), str(ROOT)],
                   check=True, capture_output=True, env=env)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)

        # Fresh install: placeholder state.json holds nothing to migrate.
        fresh = base / "fresh"; fresh.mkdir()
        install(fresh)
        assert "placeholder" in migrate(fresh).stdout
        assert (fresh / ".ai" / "state.json").is_file()
        doctor = run(*PY, str(ROOT / "scripts" / "apk_doctor.py"), str(fresh), "--quick", check=False)
        assert "status=placeholder" in doctor.stdout and "invalid Last updated" not in doctor.stdout, doctor.stdout
        migrate(fresh, "--write", "--retire-placeholder")
        assert not (fresh / ".ai" / "state.json").exists()
        assert list((fresh / ".ai").glob("state.json.migrated-*"))
        install(fresh)  # an update must not recreate the retired legacy file
        assert not (fresh / ".ai" / "state.json").exists(), "installer recreated state.json after migration"

        # Configured legacy state beside authoritative Markdown.
        project = base / "project"; project.mkdir()
        install(project)
        ai = project / ".ai"
        original_md = (ai / "PROJECT_STATE.md").read_bytes()
        legacy = {"schema_version": 1, "status": "configured", "active_task": "ส่งรายงานฉบับร่าง",
                  "next_actions": ["review", {"id": 2}], "custom_field": "keep-me"}
        (ai / "state.json").write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")
        doctor = run(*PY, str(ROOT / "scripts" / "apk_doctor.py"), str(project), "--quick", check=False)
        assert "migrate_state.py" in doctor.stdout, doctor.stdout

        before = tree_digest(project)
        dry = migrate(project)
        assert "DRY RUN" in dry.stdout and "ส่งรายงานฉบับร่าง" in dry.stdout and "keep-me" in dry.stdout
        assert tree_digest(project) == before, "dry run changed files"

        migrate(project, "--write")
        text = (ai / "PROJECT_STATE.md").read_bytes()
        assert text.startswith(original_md), "existing PROJECT_STATE.md content was rewritten"
        assert "ส่งรายงานฉบับร่าง" in text.decode("utf-8") and "keep-me" in text.decode("utf-8")
        assert not (ai / "state.json").exists()
        backups = list(ai.glob("state.json.migrated-*"))
        assert len(backups) == 1 and json.loads(backups[0].read_text(encoding="utf-8")) == legacy
        after = tree_digest(project)
        assert "nothing to do" in migrate(project, "--write").stdout
        assert tree_digest(project) == after, "second run was not a no-op"
        doctor = run(*PY, str(ROOT / "scripts" / "apk_doctor.py"), str(project), "--quick", check=False)
        assert "migrate_state.py" not in doctor.stdout

        # Restoring the same state.json is recognized as already migrated.
        backups[0].rename(ai / "state.json")
        assert "already migrated" in migrate(project, "--write").stdout
        (ai / "state.json").unlink()

        # No PROJECT_STATE.md yet: the file is created with the section.
        bare = base / "bare"; (bare / ".ai").mkdir(parents=True)
        (bare / ".ai" / "state.json").write_text(json.dumps({"schema_version": 1, "status": "configured",
                                                             "active_task": "x"}), encoding="utf-8")
        migrate(bare, "--write")
        assert (bare / ".ai" / "PROJECT_STATE.md").read_text(encoding="utf-8").startswith("# PROJECT_STATE\n")

        # Refusals leave everything untouched.
        bad = base / "bad"; (bad / ".ai").mkdir(parents=True)
        (bad / ".ai" / "PROJECT_STATE.md").write_text("# PROJECT_STATE\n", encoding="utf-8")
        for content in ("not json", json.dumps({"schema_version": 2, "status": "configured"}),
                        json.dumps({"schema_version": 1, "status": "configured", "blockers": "one"})):
            (bad / ".ai" / "state.json").write_text(content, encoding="utf-8")
            snapshot = tree_digest(bad)
            result = migrate(bad, "--write", check=False)
            assert result.returncode == 1 and "REFUSED" in result.stdout, result.stdout
            assert tree_digest(bad) == snapshot
        (bad / ".ai" / "state.json").unlink()
        target = bad / "elsewhere.json"
        target.write_text(json.dumps({"schema_version": 1, "status": "configured"}), encoding="utf-8")
        (bad / ".ai" / "state.json").symlink_to(target)
        assert migrate(bad, "--write", check=False).returncode == 1
        (bad / ".ai" / "state.json").unlink()

        collide = base / "collide"; (collide / ".ai").mkdir(parents=True)
        (collide / ".ai" / "state.json").write_text(json.dumps({"schema_version": 1, "status": "configured",
                                                                "active_task": "y"}), encoding="utf-8")
        import datetime as dt
        (collide / ".ai" / f"state.json.migrated-{dt.date.today():%Y%m%d}").write_text("{}", encoding="utf-8")
        snapshot = tree_digest(collide)
        result = migrate(collide, "--write", check=False)
        assert result.returncode == 1 and "backup already exists" in result.stdout
        assert tree_digest(collide) == snapshot

    print("state migration tests: PASS")


if __name__ == "__main__":
    main()
