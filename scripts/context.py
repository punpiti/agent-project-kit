#!/usr/bin/env python3
"""Compile a minimal, auditable context bundle for one request."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
# A shared runtime is checksum-verified; importing route_task must not add
# __pycache__ files to it.
sys.dont_write_bytecode=True
from route_task import classify

ROOT=Path(__file__).resolve().parent.parent
def read_json(path: Path) -> dict|None:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError): return None

def project_context(project: Path, limit: int=2500) -> tuple[str,list[str]]:
    parts=[]; sources=[]; ai_dir=project/".ai"
    # PROJECT_STATE.md is the authoritative progress narrative. Structured
    # project.json supplies identity/configuration but must never hide newer
    # human-maintained state. state.json is legacy fallback only.
    state_path=ai_dir/"PROJECT_STATE.md"
    if state_path.exists():
        state_text=state_path.read_text(encoding="utf-8",errors="ignore").strip()
        if state_text:
            parts.append("[Current project state — authoritative]\n"+state_text[:limit])
            sources.append(str(state_path))
    project_path=ai_dir/"project.json"; project_data=read_json(project_path)
    if project_data and project_data.get("status") != "placeholder":
        parts.append("[Structured project metadata — identity/configuration]\n"+json.dumps(project_data,ensure_ascii=False))
        sources.append(str(project_path))
    if not state_path.exists():
        legacy_path=ai_dir/"state.json"; legacy_data=read_json(legacy_path)
        if legacy_data and legacy_data.get("status") != "placeholder":
            parts.append("[Legacy structured state — compatibility fallback]\n"+json.dumps(legacy_data,ensure_ascii=False))
            sources.append(str(legacy_path))
    return "\n".join(parts),sources

def refresh_metrics(bundle: dict, counts: dict) -> int:
    metrics={**counts,"bytes":0,"estimated_tokens":1}
    bundle["metrics"]=metrics
    for _ in range(12):
        size=len((json.dumps(bundle,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
        tokens=max(1,size//4)
        if metrics["bytes"]==size and metrics["estimated_tokens"]==tokens:
            return size
        metrics["bytes"]=size; metrics["estimated_tokens"]=tokens
    return len((json.dumps(bundle,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))

def compile_bundle(request: str, project: Path, max_bytes: int) -> dict:
    route=classify(request,project)
    registry=read_json(ROOT/"config"/"workflow-registry.json") or {}
    primary={"id":route["primary_pipeline"],**registry["primary_pipelines"][route["primary_pipeline"]]}

    def resolve(kind: str, ids: list[str]) -> list[dict]:
        items=registry["modules"][kind]
        return [{"id":module_id,**items[module_id]} for module_id in ids]

    workflow=route["workflow"]
    method_modules=resolve("methods",workflow["methods"])
    lifecycle_stages=resolve("stages",workflow["stages"])
    quality_gates=resolve("gates",workflow["gates"])
    state_actions=resolve("state_actions",workflow["state_actions"])
    secondary=[]; seen_prompts={primary.get("prompt")}
    for item in lifecycle_stages+method_modules+quality_gates+state_actions:
        prompt=item.get("prompt")
        if prompt and prompt not in seen_prompts:
            secondary.append(item);seen_prompts.add(prompt)
    state,sources=project_context(project)
    bundle={
      "schema_version":2,
      "routing":route,
      "primary":primary,
      "methods":method_modules,
      "stages":lifecycle_stages,
      "gates":quality_gates,
      "state_actions":state_actions,
      "secondary":secondary,
      "omitted":route["omitted"],
      "policies":[registry["policies"][key] for key in registry["always_policies"]],
      "project_context":state,
      "sources":sources}
    counts={
      "primary_modules":1,
      "method_modules":len(method_modules),
      "lifecycle_stages":len(lifecycle_stages),
      "quality_gates":len(quality_gates),
      "state_actions":len(state_actions),
      "secondary_modules":len(secondary),
      "omitted_modules":len(route["omitted"])}
    size=refresh_metrics(bundle,counts)
    if size>max_bytes:
        marker="\n[truncated to byte budget]"
        low,high,best_fit=0,len(state),None
        while low<=high:
            middle=(low+high)//2
            bundle["project_context"]=state[:middle]+(marker if middle<len(state) else "")
            candidate_size=refresh_metrics(bundle,counts)
            if candidate_size<=max_bytes:
                best_fit=bundle["project_context"]
                low=middle+1
            else:
                high=middle-1
        if best_fit is None:
            bundle["project_context"]=""
            minimum=refresh_metrics(bundle,counts)
            if minimum>max_bytes:
                raise ValueError(f"max-bytes {max_bytes} is below minimum bundle size {minimum}")
        else:
            bundle["project_context"]=best_fit
            refresh_metrics(bundle,counts)
    return bundle

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--project",default="."); p.add_argument("--max-bytes",type=int,default=12000); p.add_argument("--output"); a=p.parse_args()
    try: bundle=compile_bundle(" ".join(a.request),Path(a.project).resolve(),a.max_bytes)
    except ValueError as error: p.error(str(error))
    text=json.dumps(bundle,ensure_ascii=False,indent=2)+"\n"
    if a.output: Path(a.output).write_text(text,encoding="utf-8")
    else: print(text,end="")
    return 2 if bundle["routing"]["needs_clarification"] else 0
if __name__=="__main__": raise SystemExit(main())
