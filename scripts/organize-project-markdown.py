#!/usr/bin/env python3
"""Classify Markdown files and optionally migrate only confirmed AI scratch.

This is intentionally conservative. Markdown may be a serious source document.
Default mode: inventory only; no moves.

Useful commands:
  python3 .ai/computing-environment/scripts/organize-project-markdown.py .
  python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive
  python3 .ai/computing-environment/scripts/organize-project-markdown.py . --apply
  python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive --restore-archived
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import shutil
import socket
from dataclasses import dataclass
from pathlib import Path

IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "env", ".conda",
    "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".ipynb_checkpoints",
    "build", "dist", "cache", ".cache", "tmp", "temp",
}

PROTECTED_NAMES = {
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md",
    "CODE_OF_CONDUCT.md", "AGENTS.md",
}

# Serious source/document hints. These should NOT be archived automatically.
DOC_HINTS = {
    "content", "draft", "report", "paper", "manuscript", "proposal", "letter",
    "document", "slides", "article", "agenda", "minutes", "syllabus", "lecture",
    "lesson", "course", "policy", "brief", "response", "reviewer", "revision",
    "cover", "memo", "statement", "abstract", "chapter", "thesis", "dissertation",
    "worksheet", "assignment", "rubric", "manual", "guide", "handbook", "specification",
}

# Exact names that are usually AI scratch. Even these are only candidates.
AI_SCRATCH_EXACT = {
    "notes", "note", "plan", "todo", "todos", "scratch", "prompt", "prompts",
    "ideas", "idea", "chatgpt", "chatgpt-output", "codex", "agent-notes",
    "worklog", "session", "session-log", "brainstorm",
}

AI_SCRATCH_SUBSTR = {
    "ai-note", "ai_notes", "scratch", "chatgpt", "codex", "tmp-note", "temp-note",
}

GENERATED_HINTS = {"generated", "output", "export", "build", "compiled"}

ARCHIVE_PREFIX = ".ai/archive/legacy-md/"

@dataclass
class Row:
    path: Path
    role: str
    status: str
    confidence: str
    action: str
    notes: str = ""
    original_path: str = ""


def rel(path: Path, project: Path) -> str:
    return str(path.relative_to(project)).replace("\\", "/")


def iter_markdown(project: Path, include_archive: bool = False):
    for root, dirs, files in os.walk(project):
        root_path = Path(root)
        rel_root = root_path.relative_to(project) if root_path != project else Path(".")
        rel_root_str = str(rel_root).replace("\\", "/")

        if rel_root_str.startswith(".ai/computing-environment"):
            dirs[:] = []
            continue
        if rel_root_str.startswith(ARCHIVE_PREFIX.rstrip("/")) and not include_archive:
            dirs[:] = []
            continue

        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            if name.lower().endswith(".md"):
                yield root_path / name


def archived_original_rel(r: str) -> str:
    # .ai/archive/legacy-md/YYYY-MM-DD/original/path.md -> original/path.md
    prefix = ARCHIVE_PREFIX
    if not r.startswith(prefix):
        return ""
    rest = r[len(prefix):]
    parts = rest.split("/", 1)
    if len(parts) == 2 and len(parts[0]) >= 8:
        return parts[1]
    return ""


def classify(path: Path, project: Path) -> Row:
    r = rel(path, project)
    lower = r.lower()
    name = path.name
    stem = path.stem.lower()
    parent = str(path.parent.relative_to(project)).replace("\\", "/") if path.parent != project else "."

    if lower.startswith(ARCHIVE_PREFIX):
        orig = archived_original_rel(r)
        if orig:
            pseudo = Path(orig)
            # classify original path, but keep archived status
            tmp_row = classify_by_rel(orig, pseudo.name, pseudo.stem.lower(), is_archived=True)
            tmp_row.path = path
            tmp_row.status = "archived"
            tmp_row.original_path = orig
            if tmp_row.role in {"document-source", "human-facing-doc"}:
                tmp_row.action = "restore-candidate"
                tmp_row.notes = "May have been archived too aggressively; review for restore"
            else:
                tmp_row.action = "keep-archived-or-synthesize"
            return tmp_row
        return Row(path, "archived-legacy", "archived", "medium", "review", "Archived legacy Markdown")

    return classify_by_rel(r, name, stem, is_archived=False, path=path)


def classify_by_rel(r: str, name: str, stem: str, is_archived: bool = False, path: Path | None = None) -> Row:
    lower = r.lower()
    p = path or Path(r)

    if lower.startswith(".ai/"):
        return Row(p, "ai-pipeline", "active", "high", "keep", "Canonical AI pipeline file")
    if name in PROTECTED_NAMES:
        return Row(p, "human-facing-doc", "active", "high", "keep", "Protected human-facing project file")
    if lower.startswith(("docs/", "doc/", "documentation/", "site/", "website/")):
        return Row(p, "human-facing-doc", "active", "high", "keep", "Human-facing documentation")
    if lower.startswith("documents/"):
        return Row(p, "document-source", "active", "high", "register", "Document pipeline source")

    tokens = set(stem.replace("_", "-").split("-")) | {stem}
    if any(h in tokens or h in lower for h in DOC_HINTS):
        return Row(p, "document-source", "active", "medium", "review-register", "Likely serious Markdown source; do not archive automatically")
    if any(h in lower for h in GENERATED_HINTS):
        return Row(p, "generated-output", "active", "medium", "review", "May be generated output; verify source exists before archiving")
    if stem in AI_SCRATCH_EXACT or any(h in lower for h in AI_SCRATCH_SUBSTR):
        confidence = "high" if stem in {"scratch", "chatgpt", "chatgpt-output", "prompt", "prompts", "todo", "todos"} else "medium"
        return Row(p, "ai-working-note-candidate", "active", confidence, "review-before-archive", "Possible AI scratch; synthesize useful content before archiving")

    return Row(p, "unknown-review-required", "active", "low", "leave-in-place", "Ambiguous Markdown; human review required")


def safe_archive_path(project: Path, src: Path, date: str) -> Path:
    r = rel(src, project)
    return project / ".ai" / "archive" / "legacy-md" / date / r


def disambiguate(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    i = 2
    dst = path
    while dst.exists():
        dst = path.with_name(f"{stem}-{i}{suffix}")
        i += 1
    return dst


def write_inventory(project: Path, rows: list[Row], moved: list[tuple[Path, Path]], restored: list[tuple[Path, Path]]) -> None:
    ai_dir = project / ".ai"
    ai_dir.mkdir(parents=True, exist_ok=True)
    inventory = ai_dir / "MARKDOWN_INVENTORY.md"
    now = dt.datetime.now().isoformat(timespec="seconds")
    machine = socket.gethostname().lower()

    counts = {}
    for row in rows:
        counts[row.role] = counts.get(row.role, 0) + 1

    lines = [
        "# MARKDOWN_INVENTORY",
        "",
        "Purpose: classify Markdown files so serious document sources, human-facing documentation, and AI working notes do not get mixed together.",
        "",
        f"Last updated: {now}",
        f"Machine: {machine}",
        "",
        "## Inventory",
        "",
        "| File | Role | Status | Confidence | Recommended action | Notes |",
        "|---|---|---|---:|---|---|",
    ]
    for row in sorted(rows, key=lambda x: rel(x.path, project)):
        note = row.notes.replace("|", "\\|")
        file_label = rel(row.path, project)
        if row.original_path:
            note = (note + f"; original path: `{row.original_path}`").strip()
        lines.append(f"| `{file_label}` | {row.role} | {row.status} | {row.confidence} | {row.action} | {note} |")

    lines += [
        "",
        "## Latest classification summary",
        "",
        f"- Markdown files inventoried: {len(rows)}",
        f"- Human-facing docs: {counts.get('human-facing-doc', 0)}",
        f"- Document sources: {counts.get('document-source', 0)}",
        f"- AI pipeline files: {counts.get('ai-pipeline', 0)}",
        f"- AI working note candidates: {counts.get('ai-working-note-candidate', 0)}",
        f"- Unknown / review required: {counts.get('unknown-review-required', 0)}",
        f"- Archived legacy files included: {counts.get('archived-legacy', 0)}",
        f"- Files moved to archive in this run: {len(moved)}",
        f"- Files restored from archive in this run: {len(restored)}",
    ]

    restore_candidates = [row for row in rows if row.action == "restore-candidate"]
    if restore_candidates:
        lines += ["", "## Restore candidates", "", "| Archived file | Suggested original path | Reason | Action |", "|---|---|---|---|"]
        for row in restore_candidates:
            lines.append(f"| `{rel(row.path, project)}` | `{row.original_path}` | {row.notes} | review/restore |")

    if moved:
        lines += ["", "## Moved to archive in this run", ""]
        for src, dst in moved:
            lines.append(f"- `{rel(src, project)}` -> `{rel(dst, project)}`")
    if restored:
        lines += ["", "## Restored from archive in this run", ""]
        for src, dst in restored:
            lines.append(f"- `{rel(src, project)}` -> `{rel(dst, project)}`")

    lines += [
        "",
        "## Safety rule",
        "",
        "Do not archive or delete serious Markdown sources. If uncertain, leave in place and mark for human review.",
    ]
    inventory.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_session_log(project: Path, mode: str, moved: list[tuple[Path, Path]], restored: list[tuple[Path, Path]]) -> None:
    log = project / ".ai" / "SESSION_LOG.md"
    if not log.exists():
        return
    today = dt.date.today().isoformat()
    machine = socket.gethostname().lower()
    with log.open("a", encoding="utf-8") as f:
        f.write(f"""

## {today} — {machine} — Markdown classification {mode}
- Objective: Classify Markdown files without treating serious Markdown sources as disposable.
- Mode: T0 Quick
- Files touched: .ai/MARKDOWN_INVENTORY.md{', .ai/archive/legacy-md/' if moved else ''}
- Result: moved {len(moved)} confirmed AI scratch candidates; restored {len(restored)} over-archived files
- Decisions made: conservative classification; no deletion
- Next action: review document-source and unknown-review-required rows before any migration
- Token note: read canonical .ai files first; open archived legacy notes only when needed.
""")


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Markdown files and optionally migrate confirmed AI scratch")
    parser.add_argument("project_path", nargs="?", default=".")
    parser.add_argument("--include-archive", action="store_true", help="Include .ai/archive/legacy-md files and flag restore candidates")
    parser.add_argument("--apply", action="store_true", help="Archive only high-confidence AI scratch candidates; serious docs are never moved")
    parser.add_argument("--include-medium", action="store_true", help="With --apply, also archive medium-confidence AI working note candidates; use cautiously")
    parser.add_argument("--restore-archived", action="store_true", help="Restore archived files classified as document-source or human-facing-doc when destination is absent")
    args = parser.parse_args()

    project = Path(args.project_path).expanduser().resolve()
    if not project.exists():
        raise FileNotFoundError(project)

    today = dt.date.today().isoformat()
    rows: list[Row] = []
    moved: list[tuple[Path, Path]] = []
    restored: list[tuple[Path, Path]] = []

    files = list(iter_markdown(project, include_archive=args.include_archive or args.restore_archived))
    for path in files:
        row = classify(path, project)

        # Restore over-archived serious Markdown if explicitly requested.
        if args.restore_archived and row.action == "restore-candidate" and row.original_path:
            dst = project / row.original_path
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(dst))
                restored.append((path, dst))
                row.status = "restored"
                row.path = dst
                row.action = "restored"
            else:
                row.notes += "; destination already exists, not restored"

        # Archive only confirmed AI scratch candidates. Never move document-source.
        if args.apply and row.role == "ai-working-note-candidate" and not rel(row.path, project).startswith(".ai/"):
            allowed = row.confidence == "high" or args.include_medium
            if allowed:
                dst = disambiguate(safe_archive_path(project, row.path, today))
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(row.path), str(dst))
                moved.append((row.path, dst))
                row.status = "moved-to-archive"
                row.path = dst
                row.action = "archived-confirmed-scratch"

        rows.append(row)

    write_inventory(project, rows, moved, restored)
    mode_parts = []
    if args.apply:
        mode_parts.append("apply")
    if args.restore_archived:
        mode_parts.append("restore")
    if args.include_archive:
        mode_parts.append("include-archive")
    mode = "+".join(mode_parts) or "dry-run"
    append_session_log(project, mode, moved, restored)

    print(f"Markdown files inventoried: {len(rows)}")
    print(f"Moved to archive: {len(moved)}")
    print(f"Restored from archive: {len(restored)}")
    print(f"Inventory: {project / '.ai' / 'MARKDOWN_INVENTORY.md'}")
    if not args.apply and not args.restore_archived:
        print("Dry run only. Use --apply for high-confidence AI scratch; use --include-archive to review archived files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
