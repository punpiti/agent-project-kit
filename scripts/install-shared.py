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

def default_home() -> Path:
    return Path(os.environ.get("APK_HOME",Path.home()/".local/share/agent-project-kit"))

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--source",default=str(Path(__file__).resolve().parent.parent));p.add_argument("--home",type=Path,default=default_home());p.add_argument("--version");p.add_argument("--force",action="store_true");p.add_argument("--bind-project",type=Path);a=p.parse_args()
    source=Path(a.source).resolve();manifest=json.loads((source/"manifest.json").read_text(encoding="utf-8"));version=a.version or manifest["version"]
    if version != manifest["version"]: raise SystemExit(f"Requested version {version} does not match source manifest {manifest['version']}")
    target=a.home.resolve()/"versions"/version
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
    bin_dir=a.home.resolve()/"bin";bin_dir.mkdir(parents=True,exist_ok=True)
    launcher=bin_dir/"apk";launcher_tmp=bin_dir/".apk.tmp"
    shutil.copy2(source/"scripts/apk.py",launcher_tmp);launcher_tmp.chmod(0o755);launcher_tmp.replace(launcher)
    checksums=json.loads((target/CHECKSUM_FILE).read_text(encoding="utf-8"))
    if content_manifest(target) != checksums: raise SystemExit(f"Shared runtime content verification failed: {target}")
    if a.bind_project:
        binding_path=a.bind_project.resolve()/".ai/apk.json";binding_path.parent.mkdir(parents=True,exist_ok=True)
        binding={"schema_version":1,"package":"agent-project-kit","version":version,"version_policy":"exact","content_sha256":checksums["content_sha256"],"profile":"standard","local_prompt_dirs":[".ai/prompts"]}
        binding_path.write_text(json.dumps(binding,indent=2)+"\n",encoding="utf-8")
        print(f"Binding: {binding_path}")
    print(target);print(f"Launcher: {launcher}");print(f"Content SHA256: {checksums['content_sha256']}");return 0
if __name__=="__main__":raise SystemExit(main())
