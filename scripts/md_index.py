#!/usr/bin/env python3
"""Index a project's Markdown and point a request at the few files worth reading.

The context bundle only carries PROJECT_STATE.md. Evidence notes, reading
caches, extraction INDEX.md files, and pipeline records written in earlier
sessions are otherwise invisible, so an agent either misses them and redoes the
work, or browses and reads too much. This module returns pointers (path, title,
matched headings, size, reason), never file content.

The index is regenerable (rebuild class R0 in DATA_FLOW_POLICY.md), so it lives
under $APK_CACHE_ROOT on local storage, not in the project. Listing files is
metadata only. Reading content is bounded per call: up to
$APK_MD_INDEX_READ_BUDGET (default 40) new or changed files whose path matches
the request or that are evidence, cache, or .ai notes, plus at most
$APK_MD_INDEX_DISCOVERY (default 5) other files. Every file read from a
cloud-only placeholder is still downloaded in full; the caps bound how many.
`--build-all` reads everything once, for use after the user agrees. Private
areas from config/release-boundary.json are never indexed, including through
symlinks.

  python3 scripts/md_index.py "อ่านบทที่ 3 กลศาสตร์ของไหล" --project .
  python3 scripts/md_index.py "check figures" --project . --file refs/book.pdf
"""
from __future__ import annotations
import argparse, difflib, hashlib, json, math, os, re, sys
from pathlib import Path

INDEX_VERSION = 1
MAX_FILES = 3000
MAX_HEADINGS = 60
FULL_READ_BYTES = 2_000_000
PARTIAL_READ_BYTES = 256_000
DEFAULT_LIMIT = 5
MIN_SCORE = 3.0
DEFAULT_READ_BUDGET = 40
DEFAULT_DISCOVERY = 5
KIT_ROOT = Path(__file__).resolve().parent.parent

IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", ".conda",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".ipynb_checkpoints", "build", "dist", "_site", "_freeze", "tmp", "temp",
}
# Installed kit snapshots are instructions, not project knowledge.
SKIP_PREFIXES = (".ai/agent-project-kit/", ".ai/computing-environment/")
# Already carried by the context bundle.
SKIP_FILES = {".ai/PROJECT_STATE.md"}
ARCHIVE_PREFIX = ".ai/archive/"


def private_rules() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Private areas follow the release boundary. Project-local .ai/ state is
    already part of the context bundle, so it stays indexable."""
    prefixes, suffixes = ["private/", "internal/", "local-profiles/"], [".private.md"]
    try:
        boundary = json.loads((KIT_ROOT / "config" / "release-boundary.json").read_text(encoding="utf-8"))
        prefixes += [p for p in boundary.get("private_prefixes", []) if p != ".ai/"]
        suffixes += [s for s in boundary.get("private_suffixes", []) if s.endswith(".md")]
    except (OSError, ValueError):
        pass
    return tuple(dict.fromkeys(prefixes)), tuple(dict.fromkeys(suffixes))


PRIVATE_PREFIXES, PRIVATE_SUFFIXES = private_rules()
EVIDENCE_HINT = re.compile(r"evidence|reading[-_ ]?cache|extract|figures?/index", re.I)
CACHE_DIR = re.compile(r"^(?P<stem>.+)-(?P<sha>[0-9a-f]{12})$")

LATIN = re.compile(r"[a-z0-9][a-z0-9_]*", re.I)
THAI = re.compile(r"[฀-๿]+")
EN_STOP = {
    "the", "and", "for", "with", "this", "that", "from", "into", "please", "help",
    "file", "files", "read", "check", "look", "make", "use", "using", "about",
    "what", "how", "why", "can", "you", "all", "any", "new", "add", "fix",
    "update", "project", "md", "markdown", "doc", "docs", "document", "page",
    "pages", "see", "show", "get", "need", "want", "should", "would", "then",
}
# Thai function words: a match made only of these says nothing about topic.
TH_STOP = (
    "ให้หน่อย", "หน่อย", "ช่วย", "ไฟล์", "เอกสาร", "เรื่อง", "อ่าน", "ดู", "ทำ",
    "ได้", "ไหม", "ครับ", "ค่ะ", "คะ", "นี้", "นั้น", "และ", "หรือ", "ของ",
    "ที่", "ใน", "ให้", "กับ", "จาก", "แล้ว", "อะไร", "ยังไง", "อย่างไร", "ด้วย",
)


def cache_root() -> Path:
    base = os.environ.get("APK_CACHE_ROOT")
    if base:
        return Path(base)
    xdg = os.environ.get("XDG_CACHE_HOME")
    # Not ".../agent-project-kit": README puts the kit's own Git clone there.
    return (Path(xdg) if xdg else Path.home() / ".cache") / "agent-project-kit-cache"


def index_path(project: Path) -> Path:
    key = hashlib.sha256(str(project.resolve()).encode("utf-8")).hexdigest()[:16]
    return cache_root() / "md-index" / f"{key}.json"


def latin_terms(text: str) -> set[str]:
    out = set()
    for word in LATIN.findall(text.casefold()):
        for part in word.split("_"):
            if len(part) >= 3 and part not in EN_STOP:
                out.add(part[:-1] if part.endswith("s") and len(part) > 4 else part)
    return out


def thai_runs(text: str) -> list[str]:
    return [run for run in THAI.findall(text) if len(run) >= 3]


def topical(fragment: str) -> bool:
    """Thai has no spaces, so stopwords are removed only from a matched
    fragment, never from the source text: "ของ" is part of "ของไหล"."""
    for stop in sorted(TH_STOP, key=len, reverse=True):
        fragment = fragment.replace(stop, "")
    return len(fragment) >= 3


def grams(text: str) -> set[str]:
    return {text[i:i + 3] for i in range(len(text) - 2)}


def front_matter(lines: list[str]) -> dict:
    if not lines or lines[0].strip() != "---":
        return {}
    meta = {}
    for line in lines[1:40]:
        if line.strip() == "---":
            break
        key, sep, value = line.partition(":")
        if sep and key.strip() in {"title", "summary", "keywords", "source_sha256", "sources"}:
            meta[key.strip()] = value.strip().strip("\"'")
    return meta


def role_of(rel: str, path: Path) -> str:
    if rel.startswith(ARCHIVE_PREFIX):
        return "archived"
    if path.name == "INDEX.md" and (path.parent / "manifest.json").exists():
        return "cache-index"
    if EVIDENCE_HINT.search(rel):
        return "evidence"
    if rel.startswith(".ai/"):
        return "ai-pipeline"
    return "document"


def parse(path: Path, rel: str, stat: os.stat_result) -> dict:
    limit = FULL_READ_BYTES if stat.st_size <= FULL_READ_BYTES else PARTIAL_READ_BYTES
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            text = handle.read(limit)
    except OSError as error:
        return {"error": str(error)}
    lines = text.splitlines()
    meta = front_matter(lines)
    headings, in_code = [], False
    for line in lines:
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
        elif not in_code and line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if level <= 3 and line[level:level + 1] == " ":
                headings.append(line[level:].strip()[:120])
                if len(headings) >= MAX_HEADINGS:
                    break
    title = meta.get("title") or (headings[0] if headings else path.stem)
    entry = {"title": title[:120], "headings": headings, "partial": limit < stat.st_size}
    for key in ("summary", "keywords", "source_sha256"):
        if meta.get(key):
            entry[key] = meta[key][:300]
    match = CACHE_DIR.match(path.parent.name)
    if match:
        entry["source_sha12"] = match["sha"]
    return entry


def private_path(path: Path) -> bool:
    """A resolved path inside any private area, wherever the root is."""
    parts = path.as_posix().split("/")
    folders = {prefix.rstrip("/") for prefix in PRIVATE_PREFIXES}
    return path.name.lower().endswith(PRIVATE_SUFFIXES) or any(part in folders for part in parts[:-1])


def private_target(path: Path, root: Path) -> bool:
    """A symlink is judged by where it points: outside the root, or into a
    private area, is never indexed."""
    if not path.is_symlink():
        return False
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return True
    return rel.startswith(PRIVATE_PREFIXES) or rel.lower().endswith(PRIVATE_SUFFIXES)


def walk(root: Path, prefix: str = ""):
    for current, dirs, files in os.walk(root):
        base = Path(current)
        here = "" if base == root else base.relative_to(root).as_posix() + "/"
        dirs[:] = sorted(d for d in dirs if d not in IGNORE_DIRS
                         and not (here + d + "/").startswith(PRIVATE_PREFIXES))
        for name in sorted(files):
            if name.lower().endswith(".md") and not name.lower().endswith(PRIVATE_SUFFIXES):
                path = base / name
                rel = prefix + path.relative_to(root).as_posix()
                if rel in SKIP_FILES or rel.startswith(SKIP_PREFIXES) or private_target(path, root):
                    continue
                yield path, rel


def extra_roots(project: Path) -> list[tuple[Path, str]]:
    """Caches kept off the synced project still belong to it."""
    roots = []
    figure = os.environ.get("APK_PDF_FIGURE_CACHE")
    if figure:
        path = Path(figure).expanduser()
        if not path.is_absolute():
            path = project / path
        try:
            path.resolve().relative_to(project.resolve())
        except ValueError:
            if path.is_dir():
                roots.append((path, str(path.resolve()) + "/"))
    return roots


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def read_budget() -> int:
    return env_int("APK_MD_INDEX_READ_BUDGET", DEFAULT_READ_BUDGET)


def build(project: Path, persist: bool = True, request: str = "",
          budget: int | None = None) -> dict:
    """Index Markdown, reading at most `budget` new or changed files (None: the
    configured budget; a negative value: no limit)."""
    project = project.resolve()
    budget = read_budget() if budget is None else budget
    wanted = latin_terms(request)
    wanted_runs = thai_runs(request)
    target = index_path(project)
    old = {}
    try:
        cached = json.loads(target.read_text(encoding="utf-8"))
        if cached.get("version") == INDEX_VERSION and cached.get("project") == str(project):
            old = cached.get("files", {})
    except (OSError, ValueError):
        pass
    files, pending, reparsed, truncated = {}, [], 0, False
    for root, prefix in [(project, "")] + extra_roots(project):
        for path, rel in walk(root, prefix):
            if len(files) >= MAX_FILES:
                truncated = True
                break
            try:
                stat = path.stat()
            except OSError:
                continue
            prior = old.get(rel)
            if (prior and not prior.get("unparsed") and prior.get("size") == stat.st_size
                    and prior.get("mtime_ns") == stat.st_mtime_ns):
                files[rel] = prior
                continue
            role = role_of(rel, path)
            # Until read, a file is known by its path; a cache folder name
            # (<stem>-<sha12>) already carries the source hash.
            files[rel] = {"title": Path(rel).stem, "headings": [], "unparsed": True,
                          "size": stat.st_size, "mtime_ns": stat.st_mtime_ns, "role": role}
            match = CACHE_DIR.match(path.parent.name)
            if match:
                files[rel]["source_sha12"] = match["sha"]
            path_hits = len(wanted & latin_terms(rel)) + sum(run in rel for run in wanted_runs)
            relevant = path_hits > 0 or role in {"evidence", "cache-index", "ai-pipeline"}
            pending.append((not relevant, -path_hits, -stat.st_mtime_ns, rel, path, stat, role))
    pending.sort(key=lambda item: item[:4])
    if budget < 0:
        chosen = pending
    else:
        relevant = [item for item in pending if not item[0]][:budget]
        other = [item for item in pending if item[0]][:env_int("APK_MD_INDEX_DISCOVERY", DEFAULT_DISCOVERY)]
        chosen = relevant + other
    for *_, rel, path, stat, role in chosen:
        entry = parse(path, rel, stat)
        entry.update(size=stat.st_size, mtime_ns=stat.st_mtime_ns, role=role)
        files[rel] = entry
        reparsed += 1
    unparsed = sum(1 for entry in files.values() if entry.get("unparsed"))
    index = {"version": INDEX_VERSION, "project": str(project), "files": files,
             "truncated": truncated, "unparsed": unparsed}
    if persist and (reparsed or len(files) != len(old)):
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            temp = target.with_suffix(".tmp")
            temp.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
            os.replace(temp, target)
        except OSError:
            pass  # read-only cache: the in-memory index still answers this call
    index["reparsed"] = reparsed
    return index


def cache_hits(digest: str, project: Path) -> list[Path]:
    """Extraction caches keyed by a source hash, looked up directly so a cache
    outside the project (DATA_FLOW_POLICY.md `hot` tier) is found without
    indexing every project's cache."""
    roots = [cache_root() / "extract"]
    figure = os.environ.get("APK_PDF_FIGURE_CACHE")
    if figure:
        path = Path(figure).expanduser()
        roots.append(path if path.is_absolute() else project / path)
    hits = []
    for root in roots:
        if root.is_dir():
            # The same private rules as the walk, judged by where a link points.
            hits.extend(hit for hit in sorted(root.glob(f"*-{digest[:12]}/INDEX.md"))
                        if not private_path(hit.resolve()))
    return hits


def sha256_file(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def thai_hit(request_runs: list[str], request_grams: set[str], text: str) -> str | None:
    for run in thai_runs(text):
        if len(grams(run) & request_grams) < 2 and run not in "".join(request_runs):
            continue
        for request_run in request_runs:
            m = difflib.SequenceMatcher(None, request_run, run, autojunk=False).find_longest_match(
                0, len(request_run), 0, len(run))
            fragment = run[m.b:m.b + m.size]
            if m.size >= min(len(run), 5) and m.size >= 4 and topical(fragment):
                return fragment
    return None


def score_entry(rel: str, entry: dict, latin: set[str], runs: list[str], run_grams: set[str]) -> tuple[float, list[str], list[str]]:
    score, reasons, matched = 0.0, [], []
    strong = latin_terms(rel + " " + entry.get("title", "") + " " + entry.get("keywords", ""))
    hits = sorted(latin & strong)
    if hits:
        score += 3 * len(hits); reasons.append("title/path: " + ", ".join(hits[:4]))
    seen, thai_seen = set(hits), set()
    for heading in entry.get("headings", [])[1:] + [entry.get("summary", "")]:
        found = (latin & latin_terms(heading)) - seen
        thai = thai_hit(runs, run_grams, heading) if runs else None
        thai = thai if thai not in thai_seen else None
        if found or thai:
            score += 2 * len(found) + (2 if thai else 0)
            seen |= found
            if thai:
                thai_seen.add(thai)
            if heading and len(matched) < 3 and heading != entry.get("summary"):
                matched.append(heading)
    if runs:
        thai = thai_hit(runs, run_grams, rel + " " + entry.get("title", "") + " " + entry.get("keywords", ""))
        if thai:
            score += 3; reasons.append("title/path: " + thai)
    heading_terms = sorted(seen - set(hits)) + sorted(thai_seen)
    if heading_terms:
        reasons.append("headings: " + ", ".join(heading_terms[:4]))
    return score, reasons, matched


def related(request: str, project: Path, files: list[Path] | None = None,
            limit: int = DEFAULT_LIMIT, index: dict | None = None) -> dict:
    index = index or build(project, request=request)
    latin = latin_terms(request)
    runs = thai_runs(request)
    run_grams = set().union(*(grams(r) for r in runs)) if runs else set()
    supplied = []
    for path in files or []:
        if path.suffix.lower() == ".md":
            continue
        supplied.append((path, sha256_file(path)))
    ranked = []
    for rel, entry in index["files"].items():
        if "error" in entry:
            continue
        score, reasons, matched = score_entry(rel, entry, latin, runs, run_grams)
        for path, digest in supplied:
            if digest and (entry.get("source_sha12") == digest[:12] or entry.get("source_sha256") == digest):
                score += 100; reasons.insert(0, f"cache of supplied file {path.name}")
            elif entry.get("role") == "cache-index" and Path(rel).parent.name.startswith(
                    re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-")[:20] or "\0"):
                score += 4; reasons.insert(0, f"cache for a file named like {path.name}; hash differs, may be stale")
        if score <= 0:
            continue
        role = entry.get("role")
        if role in {"evidence", "cache-index"}:
            score += 1
        elif role == "archived":
            score -= 2
        if score >= MIN_SCORE:
            ranked.append((score, entry.get("mtime_ns", 0), rel, entry, reasons, matched))
    project_root = project.resolve()
    seen_paths = {str(Path(rel).resolve()) if Path(rel).is_absolute() else str((project_root / rel).resolve())
                  for rel, entry in index["files"].items()
                  if any(digest and entry.get("source_sha12") == digest[:12] for _, digest in supplied)}
    for path, digest in supplied:
        for hit in cache_hits(digest, project_root) if digest else []:
            if str(hit.resolve()) in seen_paths:
                continue
            seen_paths.add(str(hit.resolve()))
            entry = {"title": hit.parent.name, "role": "cache-index", "size": hit.stat().st_size}
            ranked.append((100.0, 0, str(hit), entry, [f"cache of supplied file {path.name}"], []))
    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]))
    picks = [{"path": rel, "title": entry.get("title"), "role": entry.get("role"),
              "bytes": entry.get("size"), "score": round(score, 1),
              "reasons": reasons[:3], "matched_headings": matched,
              **({"partial_index": True} if entry.get("partial") else {}),
              **({"unread": True} if entry.get("unparsed") else {})}
             for score, _, rel, entry, reasons, matched in ranked[:limit]]
    return {"files": picks,
            "omitted_matches": max(0, len(ranked) - limit),
            "indexed_files": len(index["files"]),
            "reparsed": index.get("reparsed", 0),
            "truncated": index.get("truncated", False),
            "unread_files": index.get("unparsed", 0),
            "note": ("Read the listed files' matched sections first. An empty list means no "
                     "indexed Markdown matched; do not browse for more unless the task needs it. "
                     "Unread files are matched by path only until a later call reads them.")}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("request", nargs="+")
    p.add_argument("--project", default=".")
    p.add_argument("--file", action="append", default=[], help="a source file whose cache to look for; repeatable")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    p.add_argument("--build-all", action="store_true",
                   help="read every new or changed Markdown file now; in a cloud-synced project ask first")
    a = p.parse_args()
    request = " ".join(a.request)
    index = build(Path(a.project), request=request, budget=-1) if a.build_all else None
    result = related(request, Path(a.project), [Path(f).resolve() for f in a.file], a.limit, index)
    sys.stdout.buffer.write((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
