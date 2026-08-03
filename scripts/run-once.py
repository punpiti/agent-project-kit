#!/usr/bin/env python3
"""Run a command once per project/machine, optionally with a TTL."""
from __future__ import annotations
import argparse, datetime as dt, json, platform, subprocess
from pathlib import Path

def load(path: Path) -> dict:
    if not path.exists(): return {"schema_version": 1, "checks": {}}
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc: raise SystemExit(f"Cannot read {path}: {exc}")
    if not isinstance(data.get("checks"), dict): raise SystemExit(f"Invalid state ledger: {path}")
    return data

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", default="."); p.add_argument("--key", required=True)
    p.add_argument("--scope", choices=("project", "machine"), default="project")
    p.add_argument("--ttl-days", type=int); p.add_argument("--force", action="store_true")
    p.add_argument("command", nargs=argparse.REMAINDER); a = p.parse_args()
    command = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not command: p.error("a command is required after --")
    root = Path(a.project).resolve(); path = root / ".ai" / "AGENT_PROJECT_KIT_STATE.json"
    state = load(path); key = f"{a.scope}:{platform.node().lower()}:{a.key}" if a.scope == "machine" else f"project:{a.key}"
    now = dt.datetime.now(dt.timezone.utc); entry = state["checks"].get(key); valid = False
    if entry and entry.get("status") == "passed" and not a.force:
        valid = a.ttl_days is None
        if a.ttl_days is not None:
            try: valid = now - dt.datetime.fromisoformat(entry["completed_at"]) < dt.timedelta(days=a.ttl_days)
            except (KeyError, TypeError, ValueError): pass
    if valid: print(f"SKIP {key}: successful result is still valid"); return 0
    result = subprocess.run(command, cwd=root, check=False)
    if result.returncode: print(f"NOT RECORDED {key}: exit {result.returncode}"); return result.returncode
    path.parent.mkdir(parents=True, exist_ok=True)
    state["checks"][key] = {"status":"passed","completed_at":now.isoformat(),"ttl_days":a.ttl_days,"command":command}
    path.write_text(json.dumps(state, indent=2)+"\n", encoding="utf-8"); print(f"RECORDED {key}"); return 0

if __name__ == "__main__": raise SystemExit(main())
