#!/usr/bin/env python3
"""Install an immutable versioned Agent Project Kit shared-runtime canary."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, tempfile
from pathlib import Path

INCLUDE=("config","prompts","scripts","checklists","templates","STARTUP.md","SHARED_RUNTIME_EXPERIMENT.md","manifest.json","PACKAGE_CONTENTS.md")
CHECKSUM_FILE="PACKAGE_CHECKSUMS.json"

def content_manifest(root: Path) -> dict:
    files={}
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != CHECKSUM_FILE):
        relative=path.relative_to(root).as_posix()
        files[relative]=hashlib.sha256(path.read_bytes()).hexdigest()
    aggregate=hashlib.sha256("".join(f"{name}\0{digest}\n" for name,digest in files.items()).encode()).hexdigest()
    return {"algorithm":"sha256","content_sha256":aggregate,"files":files}

def legacy_home() -> Path:
    return Path(os.environ.get("APK_HOME", Path.home()/".local/share/agent-project-kit"))

def shared_root() -> Path:
    return Path(os.environ.get("APK_SHARED_ROOT", legacy_home()))

def machine_home() -> Path:
    return Path(os.environ.get("APK_MACHINE_HOME", legacy_home()))

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--source",default=str(Path(__file__).resolve().parent.parent));p.add_argument("--shared-root",type=Path);p.add_argument("--machine-home",type=Path);p.add_argument("--home",type=Path,help="deprecated compatibility option: use one directory for shared and machine state");p.add_argument("--version");p.add_argument("--force",action="store_true");p.add_argument("--bind-project",type=Path);a=p.parse_args()
    if a.home and (a.shared_root or a.machine_home): raise SystemExit("Use --home alone, or use --shared-root and --machine-home")
    package_root=(a.home or a.shared_root or shared_root()).resolve()
    local_home=(a.home or a.machine_home or machine_home()).resolve()
    source=Path(a.source).resolve();manifest=json.loads((source/"manifest.json").read_text(encoding="utf-8"));version=a.version or manifest["version"]
    if version != manifest["version"]: raise SystemExit(f"Requested version {version} does not match source manifest {manifest['version']}")
    target=package_root/"versions"/version
    reuse=False
    if target.exists() and not a.force:
        installed=json.loads((target/"manifest.json").read_text(encoding="utf-8")) if (target/"manifest.json").exists() else {}
        if installed.get("version")==version: reuse=True
        else: raise SystemExit(f"Refusing to overwrite non-matching shared runtime: {target}")
    if not reuse:
        target.parent.mkdir(parents=True,exist_ok=True)
        stage=Path(tempfile.mkdtemp(prefix=f".{version}.",dir=target.parent))
        try:
            for name in INCLUDE:
                src=source/name
                if not src.exists(): raise SystemExit(f"Missing package item: {src}")
                shutil.copytree(src,stage/name) if src.is_dir() else shutil.copy2(src,stage/name)
            (stage/"SHARED_RUNTIME").write_text("immutable versioned canary\n",encoding="utf-8")
            checksums=content_manifest(stage)
            (stage/CHECKSUM_FILE).write_text(json.dumps(checksums,indent=2)+"\n",encoding="utf-8")
            if target.exists(): shutil.rmtree(target)
            stage.rename(target)
        finally:
            if stage.exists(): shutil.rmtree(stage)
    bin_dir=local_home/"bin";bin_dir.mkdir(parents=True,exist_ok=True)
    launcher=bin_dir/"apk";launcher_tmp=bin_dir/".apk.tmp"
    shutil.copy2(source/"scripts/apk.py",launcher_tmp);launcher_tmp.chmod(0o755);launcher_tmp.replace(launcher)
    config_path=local_home/"config.json";config_tmp=local_home/".config.json.tmp"
    config_tmp.write_text(json.dumps({"schema_version":1,"shared_root":str(package_root)},indent=2)+"\n",encoding="utf-8");config_tmp.replace(config_path)
    checksums=json.loads((target/CHECKSUM_FILE).read_text(encoding="utf-8"))
    if content_manifest(target) != checksums: raise SystemExit(f"Shared runtime content verification failed: {target}")
    if a.bind_project:
        binding_path=a.bind_project.resolve()/".ai/apk.json";binding_path.parent.mkdir(parents=True,exist_ok=True)
        binding={"schema_version":2,"package":"agent-project-kit","version":version,"version_policy":"exact","content_sha256":checksums["content_sha256"],"profile":"standard","local_prompt_dirs":[".ai/prompts"],"runtime_mode":"shared-with-snapshot-fallback"}
        binding_path.write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")
        print(f"Binding: {binding_path}")
    print(target);print(f"Launcher: {launcher}");print(f"Machine config: {config_path}");print(f"Content SHA256: {checksums['content_sha256']}");return 0
if __name__=="__main__":raise SystemExit(main())
