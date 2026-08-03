#!/usr/bin/env python3
"""Compile a minimal, auditable context bundle for one request."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from route_task import classify

ROOT=Path(__file__).resolve().parent.parent
def read_json(path: Path) -> dict|None:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return None

def project_context(project: Path, limit: int=2500) -> tuple[str,list[str]]:
    parts=[]; sources=[]
    for name in ("project.json","state.json"):
        path=project/".ai"/name; data=read_json(path)
        if data and data.get("status") != "placeholder": parts.append(json.dumps(data,ensure_ascii=False)); sources.append(str(path))
    if not parts:
        path=project/".ai"/"PROJECT_STATE.md"
        if path.exists(): parts.append(path.read_text(encoding="utf-8",errors="ignore")[:limit]); sources.append(str(path)+" (compatibility excerpt)")
    return "\n".join(parts),sources

def compile_bundle(request: str, project: Path, max_bytes: int) -> dict:
    route=classify(request); routes=read_json(ROOT/"config"/"routes.json") or {}; workflows=read_json(ROOT/"config"/"workflows.json") or {}; policies=read_json(ROOT/"config"/"policies.json") or {}
    primary=routes.get("routes",{}).get(route["domain"],routes.get("routes",{}).get("general",{}))
    secondary=[]
    for key in route["secondary_workflows"][:2]:
        item=workflows.get("workflows",{}).get(key)
        if item: secondary.append({"id":key,**item})
    state,sources=project_context(project)
    bundle={"routing":route,"primary":primary,"secondary":secondary,"policies":[policies.get("policies",{}).get(k) for k in policies.get("always",[])],"project_context":state,"sources":sources}
    encoded=json.dumps(bundle,ensure_ascii=False,indent=2).encode()
    if len(encoded)>max_bytes:
        bundle["project_context"]=state[:max(0,max_bytes//3)]+"\n[truncated]"; encoded=json.dumps(bundle,ensure_ascii=False,indent=2).encode()
    bundle["metrics"]={"bytes":len(encoded),"estimated_tokens":max(1,len(encoded)//4),"primary_modules":1,"secondary_modules":len(secondary)}
    return bundle

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--project",default="."); p.add_argument("--max-bytes",type=int,default=12000); p.add_argument("--output"); a=p.parse_args()
    bundle=compile_bundle(" ".join(a.request),Path(a.project).resolve(),a.max_bytes); text=json.dumps(bundle,ensure_ascii=False,indent=2)+"\n"
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 2 if bundle["routing"]["needs_clarification"] else 0
if __name__=="__main__": raise SystemExit(main())
