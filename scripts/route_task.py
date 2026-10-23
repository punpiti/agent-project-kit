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
    "reviewer_response", "paper_review_role", "paper_documents", "thesis_documents", "thesis_review_verbs",
    "publication_production", "publication_verbs",
    "publication_formats", "presentation_production", "external_feedback",
    "markdown_cleanup", "markdown_topic", "markdown_verbs", "prose_writing",
    "secret_check", "checkpoint", "machine_needed", "alternative_markers",
    "genre_social", "genre_exam", "genre_web", "book_nouns", "book_parts", "book_chapter", "output_verbs",
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
    signals = routing.get("document_signals", {})
    sections = signals.get("research_report", {})
    if not isinstance(sections, dict) or not sections:
        errors.append("document_signals.research_report: must be a non-empty object")
    for name, headings in sections.items() if isinstance(sections, dict) else []:
        check_terms(f"document_signals.research_report.{name}", headings)
    for key in ("reference_paths", "published_markers"):
        check_terms(f"document_signals.{key}", signals.get(key))
    minimum = signals.get("minimum_sections")
    if not isinstance(minimum, int) or not 1 <= minimum <= max(1, len(sections)):
        errors.append("document_signals.minimum_sections: must be between 1 and the section count")
    limit = signals.get("published_marker_limit")
    if not isinstance(limit, int) or limit < 1:
        errors.append("document_signals.published_marker_limit: must be a positive integer")
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
    deliverable_owner: dict[str, str] = {}
    for genre, item in registry.get("prose_genres", {}).items():
        overlay = item.get("overlay")
        if overlay and not (ROOT / overlay).is_file():
            errors.append(f"prose_genres.{genre}: overlay {overlay!r} does not exist")
        key = item.get("phrases")
        if key and key not in REQUIRED_PHRASES:
            errors.append(f"prose_genres.{genre}: phrases {key!r} is not a router phrase list")
        routes_to = item.get("routes_to")
        if routes_to and not key:
            errors.append(f"prose_genres.{genre}: routes_to needs a phrase list that names the genre")
        for deliverable in item.get("deliverables", []):
            # A genre may own a deliverable that only its phrases produce.
            if deliverable not in axes.get("deliverable", {}) and deliverable != routes_to:
                errors.append(f"prose_genres.{genre}: unknown deliverable {deliverable!r}")
            other = deliverable_owner.setdefault(deliverable, genre)
            if other != genre:
                errors.append(f"prose_genres: deliverable {deliverable!r} in both {other} and {genre}")
    try:
        re.compile(routing.get("source_file_pattern", ""))
    except re.error as error:
        errors.append(f"source_file_pattern: {error}")
    return errors


# Same markers as apk_doctor.py: both present means the template was never filled in.
STATE_PLACEHOLDER_MARKERS = ("- Project name:\n", "สรุปเป้าหมายปัจจุบัน 3–7 บรรทัด")


KIT_NAMES = {"agent-project-kit", "computing-environment"}


def kit_source(project: Path | None) -> bool:
    """True inside Agent Project Kit's own source tree (START_HERE.md
    "Self-Hosting / Recursion Guard"), where requests about policies, prompts,
    or documents are edits to the kit itself."""
    if project is None or not (project / "START_HERE.md").is_file():
        return False
    try:
        manifest = json.loads((project / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(manifest, dict) and manifest.get("name") in KIT_NAMES


def markdown_state_initialized(ai_dir: Path) -> bool:
    path = ai_dir / "PROJECT_STATE.md"
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return bool(text.strip()) and not all(marker in text for marker in STATE_PLACEHOLDER_MARKERS)


def contains_any(text: str, phrases: list[str]) -> bool:
    return any(matches(text,[phrase]) for phrase in phrases)


def read_project_data(project: Path | None) -> dict | None:
    if project is None:
        return None
    try:
        data = json.loads((project / ".ai" / "project.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def declared_project_domains(project_data: dict | None) -> list[str]:
    if not project_data or project_data.get("status") == "placeholder":
        return []
    domains = project_data.get("domain", [])
    if isinstance(domains, str):
        domains = [domains]
    if not isinstance(domains, list):
        return []
    known = RULES["domain"]
    return list(dict.fromkeys(item for item in domains if isinstance(item, str) and item in known))


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
            # Breaks ties between pipelines sharing a deliverable: Administrative
            # Operations owns documents; for Software they are secondary output.
            if deliverable == selectors["deliverables"][0]:
                score += 10
                reasons.append("owns-deliverable")
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


def first_position(text: str, terms: list[str]) -> int:
    """Index of the earliest phrase match, with the same boundaries as matches()."""
    folded=text.casefold(); best=len(text)+1
    for term in terms:
        needle=term.casefold()
        if needle.isascii():
            found=re.search(rf"(?<![a-z0-9_.]){re.escape(needle)}(?![a-z0-9_]|\.[a-z0-9])", folded)
            index=found.start() if found else -1
        else:
            index=folded.find(needle)
        if index>=0: best=min(best,index)
    return best


def output_terms(deliverable: str) -> list[str]:
    terms=list(RULES["deliverable"].get(deliverable,[]))
    for item in ROUTING["strong_outputs"]:
        if item["id"]==deliverable: terms+=item["phrases"]
    if deliverable=="book": terms+=PHRASES["book_chapter"]
    return terms


FILLER_END = re.compile(r"(?:(?<=\s)|^)(?:a|an|the|some|new|short|few|several|\d+)$|(?:ให้|\d+)$")


def verb_led(request: str, position: int) -> bool:
    """True when the words just before `position` end in a production verb
    ("write a ...", "create 5 ...", "ออก...", "เขียน..."), skipping articles and
    numbers. The object of such a verb is the output; other mentions are its
    topic or source."""
    if position > len(request):
        return False
    before = request[:position].casefold().rstrip()
    while True:
        stripped = FILLER_END.sub("", before).rstrip()
        if stripped == before:
            break
        before = stripped
    for verb in PHRASES["output_verbs"]:
        needle = verb.casefold()
        if before.endswith(needle) and (not needle.isascii() or len(before) == len(needle)
                                        or not before[-len(needle) - 1].isalnum()):
            return True
    return False


def named_genre(request: str) -> tuple[str | None, int, bool]:
    """The genre the request asks to produce: a verb-led mention first, then the
    earliest one. Returns (genre, position, verb_led)."""
    found = []
    for genre, item in REGISTRY.get("prose_genres", {}).items():
        if item.get("phrases"):
            at = first_position(request, PHRASES[item["phrases"]])
            if at <= len(request):
                found.append((not verb_led(request, at), at, genre))
    if not found:
        return None, len(request) + 1, False
    unled, at, genre = min(found)
    return genre, at, not unled


def select_prose_genre(deliverable: str, named: str | None) -> str:
    """A genre named in the request wins; otherwise the deliverable's genre."""
    if named:
        return named
    for genre, item in REGISTRY.get("prose_genres", {}).items():
        if deliverable in item.get("deliverables", []):
            return genre
    return "general"


def bounded(items: list[str], limit: int, category: str) -> tuple[list[str], list[dict]]:
    unique = list(dict.fromkeys(items))
    selected = unique[:limit]
    omitted = [
        {"id": item, "category": category, "reason": f"{category} limit {limit} reached"}
        for item in unique[limit:]
    ]
    return selected, omitted

SIGNALS = ROUTING["document_signals"]
# A heading may carry Markdown marks, a chapter word, or section numbering.
HEADING_PREFIX = re.compile(r"^[\s#*>|=\-]*(?:บทที่\s*\d+\s*)?(?:chapter\s*\d+\s*)?(?:\d+(?:\.\d+)*[.)]?\s*)?", re.IGNORECASE)
HEADING_MAX = 80


ORDERING_PREFIX = re.compile(r"^\d+[\s._-]*|[\s._-]*\d+$")


def strip_ordering(part: str) -> str:
    """"02_references" and "references" name the same folder."""
    return ORDERING_PREFIX.sub("", part.casefold()).strip("._- ")


def document_sections(text: str) -> list[str]:
    """Names of the research-report sections that appear as headings."""
    found = set()
    for raw in text.splitlines():
        line = raw.strip()
        # A heading is short. Body prose starting with "Results show that..."
        # is not a section, and treating it as one would flag reading notes.
        if not line or len(line) > HEADING_MAX:
            continue
        rest = HEADING_PREFIX.sub("", line).strip().casefold()
        for name, headings in SIGNALS["research_report"].items():
            if name not in found and any(rest.startswith(h.casefold()) for h in headings):
                found.add(name)
    return sorted(found)


def inspect_document(path: Path) -> dict:
    """Structure and ownership signals for one document the caller named."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {"path": str(path), "readable": False, "research_document": False,
                "finished_or_external": False}
    folded = text.casefold()
    sections = document_sections(text)
    markers = sorted({marker for marker in SIGNALS["published_markers"]
                      if marker.casefold() in folded})
    reference_dirs = {name.casefold() for name in SIGNALS["reference_paths"]}
    in_reference_dir = any(strip_ordering(part) in reference_dirs for part in path.parts[:-1])
    # Structure cannot tell a draft from a reference paper or from the reader's
    # own published work: all three have abstract, method, results, references.
    # Location and publication marks are what separate them.
    finished_or_external = in_reference_dir or len(markers) >= SIGNALS["published_marker_limit"]
    return {
        "path": str(path),
        "readable": True,
        "sections": sections,
        "research_document": len(sections) >= SIGNALS["minimum_sections"],
        "finished_or_external": finished_or_external,
        "in_reference_dir": in_reference_dir,
        "published_markers": markers,
    }


def classify(request: str, project: Path | None = None, files: list[Path] | None = None) -> dict:
    documents=[inspect_document(path) for path in files or []]
    supplied_document=any(d["research_document"] for d in documents)
    project_data=read_project_data(project)
    project_domains=declared_project_domains(project_data)
    project_domain_ambiguity=False
    domain,dc=best(request,"domain",DEFAULTS["domain"]); deliverable,oc=best(request,"deliverable",DEFAULTS["deliverable"])
    for candidate,hints in ((item["id"],item["phrases"]) for item in ROUTING["strong_domains"]):
        if contains_any(request,hints): domain,dc=candidate,0.95; break
    package_release=contains_any(request,PHRASES["package_release"])
    checkpoint=contains_any(request,PHRASES["checkpoint"])
    if checkpoint:
        domain,dc="general",0.9
        deliverable,oc="analysis",0.9
    if domain=="general" and (package_release or SOURCE_FILE.search(request)):
        domain,dc="software",0.8
    if not checkpoint and domain=="general" and dc<0.5 and len(project_domains)==1:
        domain,dc=project_domains[0],0.55
    elif not checkpoint and domain=="general" and dc<0.5 and len(project_domains)>1:
        project_domain_ambiguity=True
    # Strong output phrases outrank subject-matter mentions. Merely mentioning a
    # thesis, policy, test, or document does not select that output by itself.
    strong_output=False
    for candidate,hints in ((item["id"],item["phrases"]) for item in ROUTING["strong_outputs"]):
        if contains_any(request,hints): deliverable,oc,strong_output=candidate,0.95,True; break
    # Owner rules: "หนังสือเรียน"/"ตำรา" is a textbook (book); "หนังสือ" alone is
    # a document, often an official letter; "บทที่" (chapter N) always means the
    # textbook unless the request already names a paper, thesis, slides, or
    # course material. Another book part (preface, contents, volume) next to a
    # bare "หนังสือ" leaves it unclear, so ask instead of guessing.
    if deliverable not in {"paper","presentation","course-material","book"} \
       and contains_any(request,PHRASES["book_chapter"]):
        domain,dc,deliverable,oc="book-writing",0.9,"book",0.9
    # "เขียนบทที่ 3 เรื่องข้อสอบ" writes a chapter about exams; "ออกข้อสอบบทที่ 3"
    # writes an exam on a chapter: the verb-led mention is the output.
    if deliverable=="course-material" and contains_any(request,PHRASES["book_chapter"]) \
       and verb_led(request,first_position(request,PHRASES["book_chapter"])) \
       and not verb_led(request,first_position(request,output_terms("course-material"))):
        domain,dc,deliverable,oc="book-writing",0.9,"book",0.9
    thai_book_unclear = (not strong_output and deliverable != "book"
      and contains_any(request,PHRASES["book_nouns"]) and contains_any(request,PHRASES["book_parts"]))
    if not strong_output:
        preferred=ROUTING["preferred_deliverable"].get(domain)
        if preferred and matches(request,RULES["deliverable"][preferred]): deliverable,oc=preferred,0.8
        # Engineering work in a software domain produces code unless the
        # request names some other output.
        elif domain=="software" and oc<0.5: deliverable,oc="code",0.8
    # A supplied research document names the deliverable that the request left out.
    if supplied_document and not strong_output: deliverable,oc="paper",0.9
    # In the kit's own source, "policy", "prompt", or "document" names a kit
    # file to change, so the work is software development of the kit.
    self_hosted=kit_source(project)
    if self_hosted:
        domain,dc,deliverable,oc="software",0.9,"code",0.9
        thai_book_unclear=False
    # A named post, exam, or web copy is the output, so it also decides the
    # pipeline. When another output is named too, the one a production verb
    # takes as its object is what to produce and the other is its topic or
    # source: "using this paper, create exam questions" -> exam, "เกลาตำราที่มี
    # ข้อสอบ" -> book, "implement a quiz API" -> code. If neither is verb-led an
    # explicit output phrase wins, then the earlier mention; if both are, ask.
    # A kit prompt about posts or exams is kit code, not a post or an exam.
    genre_match,genre_at,genre_verb=(None,0,False) if self_hosted else named_genre(request)
    genre_conflict=None
    if genre_match:
        target=REGISTRY["prose_genres"][genre_match]["routes_to"]
        if deliverable!=target:
            other_at=first_position(request,output_terms(deliverable))
            # Code is named by its verbs ("implement", "fix the", "debug").
            other_verb=verb_led(request,other_at) or (strong_output and deliverable=="code")
            if genre_verb and other_verb:
                genre_conflict=(genre_match,deliverable); genre_match=None
            elif other_verb or (not genre_verb and (strong_output or other_at<genre_at)):
                genre_match=None
        if genre_match:
            deliverable,oc=target,0.9
    methods=[key for key,terms in RULES["method"].items() if matches(request,terms)]
    # In software work "data" usually means configuration or fixtures.
    bare_data=[] if domain=="software" else PHRASES["data_analytics_bare_terms"]
    if "data-analytics" in methods and not contains_any(request,bare_data+PHRASES["data_analytics_confirm"]):
        methods.remove("data-analytics")
    lifecycle,lc=best(request,"lifecycle",DEFAULTS["lifecycle"])
    if checkpoint: lifecycle,lc=DEFAULTS["lifecycle"],0.9
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
    # Examining a thesis, reviewing a paper before submission, and answering
    # journal reviewers are distinct stages. Explicit thesis scope wins first;
    # a real response/rebuttal action wins over a general paper-review request.
    review_verb = contains_any(request,PHRASES["thesis_review_verbs"])
    explicit_thesis = contains_any(request,PHRASES["thesis_documents"])
    thesis_review = review_verb and explicit_thesis
    paper_review = contains_any(request,PHRASES["paper_review_role"]) or (
      review_verb and (contains_any(request,PHRASES["paper_documents"])
                       or supplied_document)
    )
    reviewer_response = contains_any(request,PHRASES["reviewer_response"])
    if deliverable=="paper" and thesis_review: stages.append("thesis-review")
    elif deliverable=="paper" and reviewer_response: stages.append("reviewer-response")
    elif deliverable=="paper" and paper_review: stages.append("paper-review")
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
    prose_genre=select_prose_genre(deliverable,genre_match)
    genre_named=genre_match is not None
    gates=[]
    # Naming a post, exam, or web copy is already a writing request. Books are
    # left out: the book-writing pipeline has its own prose method for
    # textbooks, while this gate targets articles and other reader-facing prose.
    if (deliverable in {"paper","document","course-material","policy"} and prose_writing) \
       or "paper-review" in lifecycle_stages or genre_named:
        gates.append("prose-style")
    if package_release or contains_any(request,PHRASES["secret_check"]):
        gates.append("release-boundary")
    state_actions=[]
    if checkpoint: state_actions.append("checkpoint")
    elif lifecycle=="resume": state_actions.append("resume")
    if project is not None:
        ai_dir=project/".ai"
        visible_entries=any(item.name != ".ai" for item in project.iterdir()) if project.exists() else False
        # PROJECT_STATE.md is authoritative (config/STATE_MIGRATION.md): an
        # initialized Markdown state means the project is already onboarded
        # even when project.json is still the placeholder template.
        if (not project_data or project_data.get("status")=="placeholder") and not markdown_state_initialized(ai_dir):
            state_actions.append("existing-project-onboarding" if visible_entries else "new-project-bootstrap")
        machine_needed=contains_any(request,PHRASES["machine_needed"])
        if machine_needed and not (ai_dir/"MACHINE_PROFILE.md").exists():
            state_actions.append("machine-discovery")
        if publication_production and deliverable in {"paper","book","document","course-material","policy"} and not (ai_dir/"DOCUMENT_STYLE.md").exists():
            state_actions.append("document-style-bootstrap")
    elif lifecycle=="bootstrap": state_actions.append("new-project-bootstrap")
    state_actions=list(dict.fromkeys(state_actions))
    compatibility=list(dict.fromkeys(lifecycle_stages+method_modules+gates+state_actions))
    # A research document was handed over without a stated intent. It may be
    # finished, already published, or someone else's, so ask before acting.
    clarification_reasons=[]
    if project_domain_ambiguity and domain=="general" and primary_pipeline=="general":
        clarification_reasons.append(
          "project metadata declares multiple domains; ask which domain owns this task "
          "when the request itself provides no domain signal")
    if supplied_document and not (thesis_review or paper_review or reviewer_response):
        clarification_reasons.append(
          "a supplied file looks like a research document; ask what to do with it "
          "before reviewing, because it may be finished, already published, or someone else's")
    if genre_conflict:
        clarification_reasons.append(
          f"the request asks to produce both a {genre_conflict[0]} output and a "
          f"{genre_conflict[1]}; ask which one comes first or whether both are wanted")
    if thai_book_unclear:
        clarification_reasons.append(
          "\"หนังสือ\" with a chapter, preface, or volume may be a textbook (หนังสือเรียน) "
          "or a document; ask which before choosing Book Writing or a document route")
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
      "prose_genre":prose_genre if "prose-style" in gates else None,
      "documents":documents,
      "clarification_reasons":clarification_reasons,
      "omitted":omitted,
      "selection_trace":{"primary_candidates":primary_scores,"self_hosted_kit":self_hosted},
      "confidence":round(min(dc if domain!="general" else 0.7,oc,0.6 if len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] else 0.9),2),
      "needs_clarification":bool(clarification_reasons) or oc<0.5 or (len(primary_scores)>1 and primary_scores[0]["score"]==primary_scores[1]["score"] and primary_scores[0]["score"]>1) or (contains_any(request,PHRASES["alternative_markers"]) and sum(bool(matches(request,terms)) for terms in RULES["deliverable"].values())>1)}

def main() -> int:
    if sys.argv[1:] == ["--validate"]:
        errors = validate_rules()
        for error in errors: print(f"routing rules: {error}")
        print("routing rules: " + ("FAIL" if errors else "PASS")); return 1 if errors else 0
    p=argparse.ArgumentParser(description=__doc__); p.add_argument("request",nargs="+"); p.add_argument("--pretty",action="store_true"); p.add_argument("--project"); p.add_argument("--file",action="append",default=[],help="a document to inspect; repeatable"); a=p.parse_args()
    project=Path(a.project).resolve() if a.project else None
    files=[Path(name).resolve() for name in a.file]
    # Thai output must survive a redirected stdout on Windows (cp1252 default).
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(classify(" ".join(a.request),project,files),ensure_ascii=False,indent=2 if a.pretty else None)); return 0
if __name__=="__main__": raise SystemExit(main())
