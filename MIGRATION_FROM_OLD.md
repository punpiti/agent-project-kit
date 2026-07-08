# Migration from Old `computing-environment`

This version is intended to replace the old `computing-environment` folder completely.

## What to do

1. Back up or rename the old folder first:

```bash
mv /path/to/old/computing-environment /path/to/computing-environment-old-backup-$(date +%F)
```

2. Extract this package as:

```text
/path/to/agent-project-kit
```

3. For each active project, reinstall project-local AI files from WSL2:

```bash
bash "/path/to/agent-project-kit/scripts/install-to-project.sh" .
```

4. For old projects with scattered Markdown files, run inventory first:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py .
```

5. Review `.ai/MARKDOWN_INVENTORY.md`. If classification is safe, archive likely legacy AI notes:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --apply
```

The cleanup script does **not** delete files.

## What was merged from the old folder

- `ENVIRONMENT_POLICY.md` — kept as the cross-project environment policy.
- project run logs should be kept in project-local `.ai/SESSION_LOG.md` or another private run log.
- `tools/register_project_run.sh` — moved to `scripts/register_project_run.sh`.
- `tools/scan_machine_resources.sh` — moved to `scripts/scan_machine_resources.sh`.
- `templates/pandoc-thai-a4/` — kept and updated as a document production template.
- `EDGE_PDF_VIEWER_ANNOTATION.md` — moved to `legacy/EDGE_PDF_VIEWER_ANNOTATION.md`.
- old `README.md` and `three_loop_prompts.md` — archived under `legacy/` for reference.
- old cleanup logs — moved under `legacy/cleanup-logs/`.

## What was not merged

The `.p12` certificate file from the old package was intentionally excluded. See `SECURITY_EXCLUSIONS.md`.

## New conventions

- AI working Markdown belongs under `.ai/`.
- Real document sources belong under `documents/<document-id>/content.md` and must be registered in `.ai/DOCUMENT_PIPELINE.md`.
- Loose `plan.md`, `notes.md`, `draft.md`, `review.md`, etc. in project root should be inventoried and usually archived under `.ai/archive/legacy-md/<date>/`.
- Large local cache/intermediate/data outside the project/shared source tree must be recorded in `.ai/LOCAL_RESOURCES.md` and `.ai/MACHINE_COMPATIBILITY.md`.

## v6 Markdown safety note

Older cleanup guidance may have treated scattered `.md` files as likely AI scratch. v6 changes this behavior. Markdown is not disposable by default: reports, proposals, reviewer responses, lecture notes, policy briefs, syllabi, letters, and `content.md` files may be serious source documents.

Before archiving Markdown, run inventory only:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py .
```

To inspect files already archived too aggressively:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive
```

To restore archive candidates when the destination path is absent:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive --restore-archived
```
