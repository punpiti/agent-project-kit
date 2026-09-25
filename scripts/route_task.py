#!/usr/bin/env python3
"""Deterministically classify a request into structured Agent Project Kit axes."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = json.loads((ROOT / "config" / "workflow-registry.json").read_text(encoding="utf-8"))

# Vocabulary lives in config/routing-rules.json; priority, word boundaries,
# and combination logic stay here.
ROUTING = json.loads((ROOT / "config" / "routing-rules.json").read_text(encoding="utf-8"))
RULES = ROUTING["axes"]
PHRASES = ROUTING["phrases"]
DEFAULTS = ROUTING["defaults"]

def matches(text: str, terms: list[str]) -> int:
    folded=text.casefold()
    score=0
    for term in terms:
        needle=term.casefold()
        if needle.isascii():
            # A dot followed by a word character continues a token, so the file
            # name "project.json" does not match the phrase "new project".
            score += bool(re.search(rf"(?<![a-z0-9_.]){re.escape(needle)}(?![a-z0-9_]|\.[a-z0-9])", folded))
        else:
            score += needle in folded
    return score

def best(text: str, group: str, default: str) -> tuple[str,float]:
    scores={key:matches(text,terms) for key,terms in RULES[group].items()}; top=max(scores,key=scores.get)
    if scores[top]==0: return default,0.25
    ordered=sorted(scores.values(),reverse=True); confidence=0.9 if len(ordered)<2 or ordered[0]>ordered[1] else 0.6
    return top,confidence

SOURCE_FILE=re.compile(ROUTING["source_file_pattern"], re.IGNORECASE)

REQUIRED_PHRASES = (
    "package_release", "data_analytics_confirm", "data_analytics_bare_terms",
    "reviewer_response", "publication_production", "publication_verbs",
    "publication_formats", "presentation_production", "external_feedback",
    "markdown_cleanup", "markdown_topic", "markdown_verbs", "prose_writing",
    "secret_check", "machine_needed", "alternative_markers",
)


def validate_rules(routing: dict = ROUTING, registry: dict = REGISTRY) -> list[str]:
    """Return every structural problem in the routing vocabulary."""
    errors: list[str] = []
    axes = routing.get("axes", {})

    def check_terms(where: str, terms: object) -> None:
        if not isinstance(terms, list) or not terms:
            errors.append(f"{where}: must be a non-empty list"); return
        for term in terms:
            if not isinstance(term, str) or not term or term != term.strip():
                errors.append(f"{where}: invalid phrase {term!r}")
        folded = [term.casefold() for term in terms if isinstance(term, str)]
        for term in sorted({term for term in folded if folded.count(term) > 1}):
            errors.append(f"{where}: duplicate phrase {term!r}")

    for axis in ("domain", "deliverable", "method", "lifecycle"):
        if axis not in axes:
            errors.append(f"axes.{axis}: missing"); continue
        owner: dict[str, str] = {}
        for key, terms in axes[axis].items():
            check_terms(f"axes.{axis}.{key}", terms)
            for term in terms if isinstance(terms, list) else []:
                other = owner.setdefault(term.casefold(), key)
                if other != key:
                    errors.append(f"axes.{axis}: {term!r} in both {other} and {key}")
    if routing.get("defaults", {}).get("deliverable") not in axes.get("deliverable", {}):
        errors.append("defaults.deliverable: not a deliverable axis key")
    for name, axis in (("strong_domains", "domain"), ("strong_outputs", "deliverable")):
        for index, item in enumerate(routing.get(name, [])):
            if item.get("id") not in axes.get(axis, {}):
                errors.append(f"{name}[{index}]: unknown {axis} {item.get('id')!r}")
            check_terms(f"{name}[{index}]", item.get("phrases"))
    for domain, deliverable in routing.get("preferred_deliverable", {}).items():
        if domain not in axes.get("domain", {}) or deliverable not in axes.get("deliverable", {}):
            errors.append(f"preferred_deliverable: {domain!r} -> {deliverable!r} not in axes")
    known_modules = set(registry["modules"]["methods"]) | set(registry["primary_pipelines"])
    for method, module in routing.get("method_modules", {}).items():
        if method not in axes.get("method", {}):
            errors.append(f"method_modules: unknown method {method!r}")
        if module not in known_modules:
            errors.append(f"method_modules: {method!r} maps to unregistered module {module!r}")
    for method in axes.get("method", {}):
        if method not in routing.get("method_modules", {}):
            errors.append(f"method_modules: no module for method {method!r}")
    for name in REQUIRED_PHRASES:
        check_terms(f"phrases.{name}", routing.get("phrases", {}).get(name))
    for name in sorted(set(routing.get("phrases", {})) - set(REQUIRED_PHRASES)):
        errors.append(f"phrases.{name}: not used by route_task.py")
    try:
        re.compile(routing.get("source_file_pattern", ""))
    except re.error as error:
        errors.append(f"source_file_pattern: {error}")
    return errors


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(matches(text,[phrase]) for phrase in phrases)


def select_primary(domain: str, deliverable: str, methods: list[str]) -> tuple[str, list[dict]]:
    scored = []
    for pipeline_id, item in REGISTRY["primary_pipelines"].items():
        selectors = item["selectors"]
        score = 0
        reasons = []
        matching_methods = sorted(set(methods) & set(selectors["methods"]))
        specialist_ready = not selectors.get("requires_method") or bool(matching_methods)
        if specialist_ready and deliverable in selectors["deliverables"]:
            score += 100
            reasons.append(f"deliverable:{deliverable}")
        if matching_methods:
            score += 80
            reasons.extend(f"method:{method}" for method in matching_methods)
        if domain in selectors["domains"]:
            score += 40
            reasons.append(f"domain:{domain}")
        if pipeline_id == "general":
            score += 1
            reasons.append("fallback")
        scored.append({"id": pipeline_id, "score": score, "reasons": reasons})
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[0]["id"], scored


def bounded(items: list[str], limit: int, category: str) -> tuple[list[str], list[dict]]:
    unique = list(dict.fromkeys(items))
    selected = unique[:limit]
    omitted = [
        {"id": item, "category": category, "reason": f"{category} limit {limit} reached"}
        for item in unique[limit:]
    ]
    return selected, omitted

def classify(request: str, project: Path | None = None) -> dict:
    domain,dc=best(request,"domain",DEFAULTS["domain"]); deliverable,oc=best(request,"deliverable",DEFAULTS["deliverable"])
    for candidate,hints in ((item["id"],item["phrases"]) for item in ROUTING["strong_domains"]):
        if contains_any(request,hints): domain,dc=candidate,0.95; break
    package_release=contains_any(request,PHRASES["package_release"])
    if domain=="general" and (package_release or SOURCE_FILE.search(request)):
        domain,dc="software",0.8
    # Strong output phrases outrank subject-matter mentions. Merely mentioning a
    # thesis, policy, test, or document does not select that output by itself.
    strong_output=False
    for candidate,hints in ((item["id"],item["phrases"]) for item in ROUTING["strong_outputs"]):
        if contains_any(request,hints): deliverable,oc,strong_output=candidate,0.95,True; break
    if not strong_output:
        preferred=ROUTING["preferred_deliverable"].get(domain)
        if preferred and matches(request,RULES["deliverable"][preferred]): deliverable,oc=preferred,0.8
        # Engineering work in a software domain produces code unless the
        # request names some other output.
        elif domain=="software" and oc<0.5: deliverable,oc="code",0.8
    methods=[key for key,terms in RULES["method"].items() if matches(request,terms)]
    # In software work "data" usually means configuration or fixtures.
    bare_data=[] if domain=="software" else PHRASES["data_analytics_bare_terms"]
    if "data-analytics" in methods and not contains_any(request,bare_data+PHRASES["data_analytics_confirm"]):
        methods.remove("data-analytics")
    lifecycle,lc=best(request,"lifecycle",DEFAULTS["lifecycle"])
    primary_pipeline, primary_scores = select_primary(domain, deliverable, methods)
    method_candidates=[]
    method_map=ROUTING["method_modules"]
    for method in methods:
        module_id=method_map.get(method)
        if module_id and module_id != primary_pipeline:
            method_candidates.append(module_id)
    method_modules,omitted=bounded(
      method_candidates,REGISTRY["composition"]["method_max"],"method")
    stages=[]
    if deliverable=="code": stages.append("implementation")
    if deliverable=="paper" and contains_any(request,PHRASES["reviewer_response"]): stages.append("reviewer-response")
    publication_production=contains_any(request,PHRASES["publication_production"])
    publication_production = publication_production or (
      contains_any(request,PHRASES["publication_verbs"])
      and contains_any(request,PHRASES["publication_formats"])
    )
    presentation_production=contains_any(request,PHRASES["presentation_production"])
    if publication_production and deliverable != "presentation":
        stages.append("publication-production")
    if deliverable == "presentation" and presentation_production:
        stages.append("presentation-production")
    if contains_any(request,PHRASES["external_feedback"]):
        stages.append("external-feedback")
    markdown_cleanup=contains_any(request,PHRASES["markdown_cleanup"])
    markdown_cleanup = markdown_cleanup or (
      contains_any(request,PHRASES["markdown_topic"])
      and contains_any(request,PHRASES["markdown_verbs"]))
    if markdown_cleanup:
        stages.append("markdown-cleanup")
    if package_release:
        # Integrity and privacy gates must survive the stage limit.
        stages.insert(0,"package-release")
    lifecycle_stages,stage_omitted=bounded(
      stages,REGISTRY["composition"]["stage_max"],"stage")
    omitted.extend(stage_omitted)
    prose_writing=contains_any(request,PHRASES["prose_writing"])
    gates=[]
    if deliverable in {"paper","book","document","course-material","policy"} and prose_writing:
        gates.append("prose-style")
    if package_release or contains_any(request,PHRASES["secret_check"]):
        gates.append("release-boundary")
    state_actions=[]
    if lifecycle=="resume": state_actions.append("resume")
    if project is not None:
        ai_dir=project/".ai"; project_file=ai_dir/"project.json"
        try: project_data=json.loads(project_file.read_text(encoding="utf-8"))
        except (OSError,json.JSONDecodeError): project_data=None
        visible_entries=any(item.name != ".ai" for item in project.iterdir()) if project.exists() else False
        if not project_data or project_data.get("status")=="placeholder":
            state_actions.append("existing-project-onboarding" if visible_entries else "new-project-bootstrap")
        machine_needed=contains_any(request,PHRASES["machine_needed"])
        if machine_needed and not (ai_dir/"MACHINE_PROFILE.md").exists():
            state_actions.append("machine-discovery")
        if publication_production and deliverable in {"paper","book","document","course-material","policy"} and not (ai_dir/"DOCUMENT_STYLE.md").exists():
            state_actions.append("document-style-bootstrap")
    elif lifecycle=="bootstrap": state_actions.append("new-project-bootstrap")
    state_actions=list(dict.fromkeys(state_actions))
    compatibility=list(dict.fromkeys(lifecycle_stages+method_modules+gates+state_actions))
    return {
      "schema_version":2,
      "request":request,
      "domain":domain,
      "deliverable":deliverable,
      "methods":methods,
      "lifecycle":lifecycle,
      "primary_pipeline":primary_pipeline,
      "workflow":{
        "primary":primary_pipeline,
        "methods":method_modules,
        "stages":lifecycle_stages,
        "gates":gates,
        "state_actions":state_actions},
      "secondary_workflows":compatibility,
      "omitted":omitted,
      "selection_trace":{"primary_candidates":primary_scores},
      "confidence":round(min(dc if domain!="general" else 0.7,oc,0.6 if len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] else 0.9),2),
      "needs_clarification":oc<0.5 or (len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] and primary_scores[0]["score"]>1) or (contains_any(request,PHRASES["alternative_markers"]) and sum(bool(matches(request,terms)) for terms in RULES["deliverable"].values())>1)}

def main() -> int:
    if sys.argv[1:] == ["--validate"]:
        errors = validate_rules()
        for error in errors: print(f"routing rules: {error}")
        print("routing rules: " + ("FAIL" if errors else "PASS")); return 1 if errors else 0
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--pretty",action="store_true"); p.add_argument("--project"); a=p.parse_args()
    project=Path(a.project).resolve() if a.project else None
    # Thai output must survive a redirected stdout on Windows (cp1252 default).
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(classify(" ".join(a.request),project),ensure_ascii=False,indent=2 if a.pretty else None)); return 0
if __name__=="__main__": raise SystemExit(main())
