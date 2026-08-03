#!/usr/bin/env python3
"""Install an immutable versioned Agent Project Kit shared-runtime canary."""
from __future__ import annotations
import argparse, json, os, shutil, tempfile
from pathlib import Path

INCLUDE=("config","prompts","scripts","checklists","templates","STARTUP.md","SHARED_RUNTIME_EXPERIMENT.md","manifest.json","PACKAGE_CONTENTS.md")

def default_home() -> Path:
    return Path(os.environ.get("APK_HOME",Path.home()/".local/share/agent-project-kit"))

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--source",default=str(Path(__file__).resolve().parent.parent));p.add_argument("--home",type=Path,default=default_home());p.add_argument("--version");p.add_argument("--force",action="store_true");a=p.parse_args()
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
            if target.exists(): shutil.rmtree(target)
            stage.rename(target)
        finally:
            if stage.exists(): shutil.rmtree(stage)
    bin_dir=a.home.resolve()/"bin";bin_dir.mkdir(parents=True,exist_ok=True)
    launcher=bin_dir/"apk";launcher_tmp=bin_dir/".apk.tmp"
    shutil.copy2(source/"scripts/apk.py",launcher_tmp);launcher_tmp.chmod(0o755);launcher_tmp.replace(launcher)
    print(target);print(f"Launcher: {launcher}");return 0
if __name__=="__main__":raise SystemExit(main())
