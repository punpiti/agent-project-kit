# Markdown Over-Archive Recovery

Use this when a previous cleanup archived too many Markdown files.

## Principle

Do not assume archived Markdown is trash. Some archived `.md` files may be serious source documents that should be restored or registered in the document pipeline.

## Step 1 — Inspect archived files

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive
```

Read:

```text
.ai/MARKDOWN_INVENTORY.md
```

Look for rows with:

```text
Recommended action = restore-candidate
```

These are archived files whose original path/name looks like a serious document source or human-facing doc.

## Step 2 — Restore safely

Only after reviewing the inventory:

```bash
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive --restore-archived
```

The script restores only files marked as restore candidates and only when the destination path does not already exist.

## Step 3 — Register serious documents

If restored files are actual documents, register them in:

```text
.ai/DOCUMENT_PIPELINE.md
```

Prefer:

```text
documents/<document-id>/content.md
```

for new organized document sources, but do not move old serious Markdown blindly.

## Step 4 — Synthesize AI notes

For archived files that are truly AI working notes, synthesize useful information into canonical files:

```text
.ai/PROJECT_STATE.md
.ai/EVALS.md
.ai/REVIEW_GATE.md
.ai/SESSION_LOG.md
.ai/DECISION_LOG.md
```

Then leave the old note in archive. Do not delete unless explicitly requested.
