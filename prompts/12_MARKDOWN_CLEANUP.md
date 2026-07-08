# Prompt 12 — Markdown Classification and Pipeline Migration

Use this when an old project has many Markdown files.

```text
Read AGENTS.md and .ai/computing-environment first.
This project may contain serious Markdown sources and AI scratch Markdown mixed together.
Do NOT assume all .md files are temporary.

First run inventory only:
python3 .ai/computing-environment/scripts/organize-project-markdown.py .

Then read .ai/MARKDOWN_INVENTORY.md and classify files as:
- human-facing-doc
- document-source
- ai-pipeline
- ai-working-note-candidate
- generated-output
- unknown-review-required
- archived-legacy

Do not move anything automatically unless it is clearly confirmed as AI working scratch.
If unsure, leave it in place and ask for human decision.

For serious document sources, register them in .ai/DOCUMENT_PIPELINE.md instead of archiving them.
For AI working notes, synthesize useful content into canonical .ai files before archiving.
If previous cleanup archived too much, generate a restore plan first.

Never delete Markdown files.
```

## Archive recovery prompt

```text
Some Markdown may have been over-archived into .ai/archive/legacy-md/.
Run:
python3 .ai/computing-environment/scripts/organize-project-markdown.py . --include-archive

Then inspect files classified as archived-legacy and propose which should be restored as document-source or human-facing-doc.
Do not restore blindly if destination files already exist.
```
