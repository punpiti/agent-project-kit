#!/usr/bin/env python3
"""Resolve and invoke a version-pinned shared Agent Project Kit runtime."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path

def binding(project: Path) -> dict:
    path=project/".ai/apk.json"
    if not path.exists(): raise SystemExit(f"No project binding: {path}")
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version",1) not in (1,2): raise SystemExit(f"Unsupported project binding schema: {path}")
    if data.get("package")!="agent-project-kit" or not data.get("version"): raise SystemExit(f"Invalid project binding: {path}")
    return data

def legacy_home() -> Path:
    return Path(os.environ.get("APK_HOME",Path.home()/".local/share/agent-project-kit"))

def machine_home() -> Path:
    return Path(os.environ.get("APK_MACHINE_HOME",legacy_home())).resolve()

def runtime_home() -> Path:
    if os.environ.get("APK_SHARED_ROOT"): return Path(os.environ["APK_SHARED_ROOT"]).resolve()
    config_path=machine_home()/"config.json"
    if config_path.exists():
        config=json.loads(config_path.read_text(encoding="utf-8"))
        if config.get("shared_root"): return Path(config["shared_root"]).resolve()
    return legacy_home().resolve()

def verify_content(runtime: Path, expected: str) -> None:
    checksum_path=runtime/"PACKAGE_CHECKSUMS.json"
    if not expected: raise SystemExit("Project binding has no content_sha256; recreate it with install-shared.py --bind-project")
    if not checksum_path.exists(): raise SystemExit(f"Shared runtime has no content checksum manifest: {checksum_path}")
    checksums=json.loads(checksum_path.read_text(encoding="utf-8"));actual_files={}
    for path in sorted(p for p in runtime.rglob("*") if p.is_file() and p.name != checksum_path.name):
        name=path.relative_to(runtime).as_posix();actual_files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    aggregate=hashlib.sha256("".join(f"{name}\0{digest}\n" for name,digest in actual_files.items()).encode()).hexdigest()
    if actual_files != checksums.get("files") or aggregate != checksums.get("content_sha256") or aggregate != expected:
        raise SystemExit(f"Shared runtime content checksum mismatch: {runtime}")

def resolve(project: Path) -> tuple[Path,dict]:
    data=binding(project);runtime=runtime_home()/"versions"/data["version"]
    manifest=runtime/"manifest.json"
    if not manifest.exists(): raise SystemExit(f"Required Agent Project Kit {data['version']} is not installed at {runtime}")
    installed=json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("version_policy","exact")=="exact" and installed.get("version")!=data["version"]: raise SystemExit("Shared runtime version mismatch")
    verify_content(runtime,data.get("content_sha256",""))
    return runtime,data

def rollback(project: Path) -> Path:
    active=project/".ai/apk.json";disabled=project/".ai/apk.json.disabled"
    if not active.exists(): raise SystemExit(f"No active project binding: {active}")
    if disabled.exists(): raise SystemExit(f"Refusing to overwrite existing rollback binding: {disabled}")
    active.replace(disabled);return disabled

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--project",default=".");sub=p.add_subparsers(dest="command",required=True)
    sub.add_parser("resolve");c=sub.add_parser("context");c.add_argument("request",nargs="+");c.add_argument("--output");sub.add_parser("doctor");sub.add_parser("rollback");a=p.parse_args();project=Path(a.project).resolve()
    if a.command=="rollback": print(rollback(project));return 0
    runtime,data=resolve(project)
    if a.command=="resolve": print(json.dumps({"runtime":str(runtime),"binding":data},indent=2));return 0
    if a.command=="context":
        cmd=[sys.executable,str(runtime/"scripts/context.py"),"--project",str(project)];
        if a.output:cmd.extend(["--output",a.output])
        cmd.extend(a.request);return subprocess.run(cmd,check=False).returncode
    return subprocess.run([sys.executable,str(runtime/"scripts/apk_doctor.py"),str(project),"--quick"],check=False).returncode
if __name__=="__main__":raise SystemExit(main())
