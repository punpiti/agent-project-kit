#!/usr/bin/env python3
"""Sync working clones at the start and end of a work session.

Git repositories live outside synced folders (DATA_FLOW_POLICY.md), so nothing
moves between machines unless it is pushed. This script does the routine part
for every clone under one root (default ~/projects):

  start  fetch all remotes; fast-forward each branch that is only behind its
         upstream; pull newer non-Git files (e.g. .ai/, .env.local) from the hub
  end    push each branch that is only ahead of its upstream; mirror all
         branches and tags to the backup remote; push newer non-Git files to
         the hub; list uncommitted work, which is NOT backed up anywhere
  status show ahead/behind/uncommitted counts without changing anything

It never commits, merges diverged branches, rebases, stashes, or deletes.
Anything it cannot do safely is reported for a person to decide.

Settings come from the private node inventory read by compute_nodes.py
(--inventory, $APK_COMPUTE_NODES, ~/.config/agent-project-kit/compute-nodes.json),
key "projects_sync":

  "projects_sync": {
    "root": "~/projects",            # where clones live on every node
    "hub": "office-desktop",         # node holding backup bare repos and the
                                     # reference copy of non-Git files
    "backup_remote": "backup",       # remote name pointing at the hub's bare repo
    "extra_paths": [".ai", ".env.local"]   # per-repo files outside Git
  }

The hub is found by matching this machine's hostname against the hub node's
"hostnames"; on the hub, non-Git files are not copied (it is the reference).
Non-Git files are copied with rsync --update (newer file wins, nothing is
deleted).

  python3 scripts/projects_sync.py start
  python3 scripts/projects_sync.py end
  python3 scripts/projects_sync.py status
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

DEFAULTS = {"root": "~/projects", "hub": None, "backup_remote": None,
            "extra_paths": [".ai"]}
GIT_TIMEOUT = 180


def inventory_path(cli: str | None) -> Path | None:
    for cand in (cli, os.environ.get("APK_COMPUTE_NODES"),
                 "~/.config/agent-project-kit/compute-nodes.json"):
        if cand:
            p = Path(cand).expanduser()
            if p.is_file():
                return p
    return None


def load_config(args) -> dict:
    cfg = dict(DEFAULTS)
    hub_node = None
    inv = inventory_path(args.inventory)
    if inv:
        data = json.loads(inv.read_text(encoding="utf-8"))
        cfg.update(data.get("projects_sync") or {})
        for node in data.get("nodes", []):
            if node.get("name") == cfg.get("hub"):
                hub_node = node
    if args.root:
        cfg["root"] = args.root
    host = (args.hostname or socket.gethostname()).lower()
    cfg["root_path"] = Path(cfg["root"]).expanduser()
    cfg["is_hub"] = bool(hub_node) and host in {
        h.lower() for h in hub_node.get("hostnames", [hub_node.get("name", "")])}
    cfg["hub_ssh"] = (hub_node or {}).get("ssh")
    cfg["host"] = host
    return cfg


def git(repo: Path, *a, check=False, timeout=GIT_TIMEOUT):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                       text=True, timeout=timeout)
    if check and r.returncode:
        raise RuntimeError((r.stderr or r.stdout).strip().splitlines()[-1:]
                           or [f"git {a[0]} failed"])
    return r


def branches(repo: Path):
    """(branch, upstream_remote, upstream_ref, ahead, behind) for tracked branches."""
    out = git(repo, "for-each-ref", "--format=%(refname:short)\t%(upstream:remotename)"
              "\t%(upstream:short)", "refs/heads").stdout
    res = []
    for line in out.splitlines():
        name, remote, up = (line.split("\t") + ["", ""])[:3]
        if not up:
            continue
        r = git(repo, "rev-list", "--left-right", "--count", f"{name}...{up}")
        if r.returncode:
            continue  # upstream ref missing (e.g. deleted on the remote)
        ahead, behind = map(int, r.stdout.split())
        res.append((name, remote, up, ahead, behind))
    return res


def uncommitted(repo: Path, extras) -> int:
    lines = git(repo, "status", "--porcelain").stdout.splitlines()
    skip = tuple(e.rstrip("/") for e in extras)
    return sum(1 for l in lines
               if not l[3:].strip('"').startswith(skip))


def remotes(repo: Path):
    return set(git(repo, "remote").stdout.split())


def sync_repo(repo: Path, mode: str, cfg: dict, dry: bool):
    notes, problems = [], []
    name = repo.name
    try:
        if mode in ("start", "end"):
            r = git(repo, "fetch", "--all", "--prune", "--quiet")
            if r.returncode:
                problems.append("fetch failed: " + (r.stderr.strip().splitlines() or ["?"])[-1])
        current = git(repo, "branch", "--show-current").stdout.strip()
        for br, remote, up, ahead, behind in branches(repo):
            if ahead and behind:
                problems.append(f"{br} diverged from {up} ({ahead} ahead, {behind} behind): merge or rebase by hand")
            elif mode == "start" and behind:
                if dry:
                    notes.append(f"would fast-forward {br} by {behind}")
                elif br == current:
                    r = git(repo, "merge", "--ff-only", "--quiet", up)
                    (notes if not r.returncode else problems).append(
                        f"{br} fast-forwarded {behind}" if not r.returncode else
                        f"{br} cannot fast-forward (local changes in the way?)")
                else:
                    r = git(repo, "update-ref", f"refs/heads/{br}", up)
                    notes.append(f"{br} fast-forwarded {behind}")
            elif mode == "end" and ahead:
                if dry:
                    notes.append(f"would push {br} to {remote} ({ahead})")
                else:
                    r = git(repo, "push", "--quiet", remote, f"{br}:{up.split('/', 1)[1]}")
                    (notes if not r.returncode else problems).append(
                        f"pushed {br} to {remote} ({ahead})" if not r.returncode else
                        f"push {br} to {remote} failed: " + (r.stderr.strip().splitlines() or ["?"])[-1])
            elif mode == "status" and (ahead or behind):
                notes.append(f"{br}: {ahead} ahead, {behind} behind {up}")
        bk = cfg.get("backup_remote")
        if mode == "end" and bk and bk in remotes(repo) and not dry:
            for what in ("--all", "--tags"):
                r = git(repo, "push", "--quiet", bk, what)
                if r.returncode:
                    problems.append(f"backup push {what} to {bk} failed: "
                                    + (r.stderr.strip().splitlines() or ["?"])[-1])
        elif mode == "end" and bk and bk not in remotes(repo):
            problems.append(f"no '{bk}' remote: not backed up to the hub")
        n = uncommitted(repo, cfg.get("extra_paths", []))
        if n and mode != "start":
            problems.append(f"{n} uncommitted change(s): not backed up until committed and pushed")
        elif n:
            notes.append(f"{n} uncommitted change(s)")
    except subprocess.TimeoutExpired:
        problems.append("git timed out (network?)")
    except Exception as e:  # report and continue with the other repos
        problems.append(f"error: {e}")
    return name, notes, problems


def rsync_extras(repo_names, mode, cfg, dry):
    """Copy non-Git files between this node and the hub (newer wins)."""
    if cfg["is_hub"] or not cfg.get("hub_ssh") or not cfg.get("extra_paths"):
        return []
    problems = []
    root = cfg["root_path"]
    try:
        remote_root = "~/" + str(root.relative_to(Path.home()))
    except ValueError:
        remote_root = str(root)
    for name in repo_names:
        for extra in cfg["extra_paths"]:
            local = root / name / extra
            remote = f"{cfg['hub_ssh']}:{remote_root}/{name}/{extra}"
            is_dir = local.is_dir() or (mode == "start" and not local.suffix)
            src, dst = ((remote, str(local)) if mode == "start" else (str(local), remote))
            if mode == "end" and not local.exists():
                continue
            if is_dir:
                src, dst = src.rstrip("/") + "/", dst.rstrip("/") + "/"
            cmd = ["rsync", "-a", "--update", "--timeout=60"] + (["-n"] if dry else []) + [src, dst]
            if mode == "end":
                # make sure the parent exists on the hub
                cmd[1:1] = ["--mkpath"]
            r = subprocess.run(cmd, capture_output=True, text=True)
            # 23 = some files missing on the source side: normal when the hub has no such path
            if r.returncode not in (0, 23):
                problems.append(f"{name}/{extra}: rsync failed ({r.returncode}) "
                                + (r.stderr.strip().splitlines() or [""])[-1])
                if r.returncode == 255:  # hub unreachable: stop trying
                    return problems + ["hub unreachable over SSH: non-Git files not synced"]
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", choices=["start", "end", "status"])
    ap.add_argument("--root")
    ap.add_argument("--inventory")
    ap.add_argument("--hostname", help=argparse.SUPPRESS)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-extras", action="store_true", help="skip non-Git file sync")
    args = ap.parse_args(argv)
    cfg = load_config(args)
    root = cfg["root_path"]
    repos = sorted(p for p in root.iterdir() if (p / ".git").exists()) if root.is_dir() else []
    role = "hub" if cfg["is_hub"] else "node"
    print(f"projects-sync {args.mode} on {cfg['host']} ({role}), {len(repos)} repos in {root}")
    if not repos:
        return 0
    with cf.ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(lambda r: sync_repo(r, args.mode, cfg, args.dry_run), repos))
    extra_problems = []
    if args.mode in ("start", "end") and not args.no_extras:
        extra_problems = rsync_extras([r.name for r in repos], args.mode, cfg, args.dry_run)
    bad = 0
    for name, notes, problems in results:
        if problems:
            bad += 1
            print(f"  ! {name}: " + "; ".join(problems + notes))
        elif notes:
            print(f"  · {name}: " + "; ".join(notes))
    for p in extra_problems:
        print(f"  ! {p}")
    ok = len(repos) - bad
    print(f"done: {ok} clean, {bad} need attention" + (" (dry run)" if args.dry_run else ""))
    return 1 if bad or extra_problems else 0


if __name__ == "__main__":
    sys.exit(main())
