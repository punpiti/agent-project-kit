#!/usr/bin/env python3
"""Offline tests for scripts/projects_sync.py using throwaway local repos."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "projects_sync.py"


def sh(*a, cwd=None):
    r = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"command failed: {a}\n{r.stderr}")
    return r.stdout.strip()


def run(mode, root, inv, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), mode, "--root", str(root),
                           "--inventory", str(inv), "--hostname", "node-a", "--no-extras",
                           *extra], capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        g = ["-c", "user.name=T", "-c", "user.email=t@example.invalid"]
        sh("git", "init", "-q", "--bare", "-b", "main", str(t / "origin.git"))
        sh("git", "init", "-q", "--bare", "-b", "main", str(t / "backup.git"))
        seed = t / "seed"
        sh("git", "clone", "-q", str(t / "origin.git"), str(seed))
        (seed / "a.txt").write_text("1\n")
        sh("git", *g, "-C", str(seed), "add", "a.txt")
        sh("git", *g, "-C", str(seed), "commit", "-q", "-m", "one")
        sh("git", "-C", str(seed), "push", "-q", "origin", "HEAD:main")
        for node in ("A", "B"):
            (t / node).mkdir()
            sh("git", "clone", "-q", str(t / "origin.git"), str(t / node / "repo"))
            sh("git", "-C", str(t / node / "repo"), "remote", "add", "backup", str(t / "backup.git"))
        inv = t / "inv.json"
        inv.write_text(json.dumps({"nodes": [{"name": "hub", "hostnames": ["hub"]}],
                                   "projects_sync": {"hub": "hub", "backup_remote": "backup"}}))

        # end on A pushes a new commit to origin and mirrors to backup
        a = t / "A" / "repo"
        (a / "a.txt").write_text("2\n")
        sh("git", *g, "-C", str(a), "commit", "-q", "-am", "two")
        r = run("end", t / "A", inv)
        assert r.returncode == 0, r.stdout + r.stderr
        head = sh("git", "-C", str(a), "rev-parse", "HEAD")
        assert sh("git", "--git-dir", str(t / "origin.git"), "rev-parse", "main") == head
        assert sh("git", "--git-dir", str(t / "backup.git"), "rev-parse", "main") == head

        # start on B fast-forwards
        b = t / "B" / "repo"
        r = run("start", t / "B", inv)
        assert r.returncode == 0, r.stdout + r.stderr
        assert sh("git", "-C", str(b), "rev-parse", "HEAD") == head

        # uncommitted work is reported at end and exit code is 1; nothing committed
        (b / "a.txt").write_text("dirty\n")
        r = run("end", t / "B", inv)
        assert r.returncode == 1 and "uncommitted" in r.stdout, r.stdout
        assert sh("git", "-C", str(b), "rev-parse", "HEAD") == head

        # diverged branch is reported, not merged
        sh("git", "-C", str(b), "checkout", "-q", "--", "a.txt")
        (a / "a.txt").write_text("3\n")
        sh("git", *g, "-C", str(a), "commit", "-q", "-am", "three-a")
        sh("git", "-C", str(a), "push", "-q", "origin", "main")
        (b / "b.txt").write_text("x\n")
        sh("git", *g, "-C", str(b), "add", "b.txt")
        sh("git", *g, "-C", str(b), "commit", "-q", "-m", "three-b")
        before = sh("git", "-C", str(b), "rev-parse", "HEAD")
        r = run("start", t / "B", inv)
        assert r.returncode == 1 and "diverged" in r.stdout, r.stdout
        assert sh("git", "-C", str(b), "rev-parse", "HEAD") == before

        # hub detection
        r = subprocess.run([sys.executable, str(SCRIPT), "status", "--root", str(t / "A"),
                            "--inventory", str(inv), "--hostname", "hub"],
                           capture_output=True, text=True)
        assert "(hub)" in r.stdout, r.stdout
    print("projects_sync tests passed")


if __name__ == "__main__":
    main()
