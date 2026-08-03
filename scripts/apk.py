#!/usr/bin/env python3
"""Resolve and invoke a version-pinned shared Agent Project Kit runtime."""
from __future__ import annotations
import argparse,json,os,subprocess,sys
from pathlib import Path

def binding(project: Path) -> dict:
    path=project/".ai/apk.json"
    if not path.exists(): raise SystemExit(f"No project binding: {path}")
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("package")!="agent-project-kit" or not data.get("version"): raise SystemExit(f"Invalid project binding: {path}")
    return data

def runtime_home() -> Path:
    return Path(os.environ.get("APK_HOME",Path.home()/".local/share/agent-project-kit")).resolve()

def resolve(project: Path) -> tuple[Path,dict]:
    data=binding(project);runtime=runtime_home()/"versions"/data["version"]
    manifest=runtime/"manifest.json"
    if not manifest.exists(): raise SystemExit(f"Required Agent Project Kit {data['version']} is not installed at {runtime}")
    installed=json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("version_policy","exact")=="exact" and installed.get("version")!=data["version"]: raise SystemExit("Shared runtime version mismatch")
    return runtime,data

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--project",default=".");sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("resolve");c=sub.add_parser("context");c.add_argument("request",nargs="+");c.add_argument("--output");sub.add_parser("doctor");a=p.parse_args();project=Path(a.project).resolve();runtime,data=resolve(project)
    if a.command=="resolve": print(json.dumps({"runtime":str(runtime),"binding":data},indent=2));return 0
    if a.command=="context":
        cmd=[sys.executable,str(runtime/"scripts/context.py"),"--project",str(project)];
        if a.output:cmd.extend(["--output",a.output])
        cmd.extend(a.request);return subprocess.run(cmd,check=False).returncode
    return subprocess.run([sys.executable,str(runtime/"scripts/apk_doctor.py"),str(project),"--quick"],check=False).returncode
if __name__=="__main__":raise SystemExit(main())
