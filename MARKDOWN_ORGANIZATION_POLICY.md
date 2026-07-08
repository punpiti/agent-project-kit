# Markdown Classification and Pipeline Policy

This policy prevents projects from accumulating scattered Markdown files while protecting serious Markdown documents.

## Core rule

Markdown is not disposable by default.

Markdown may be the preferred source format for serious work. The goal is not to "clean up all Markdown". The goal is to classify every Markdown file by role and keep AI working memory separate from real project documents.

## Roles

Classify Markdown files into one of these roles:

- `human-facing-doc` — `README.md`, `docs/**/*.md`, user/developer documentation.
- `document-source` — serious document source such as reports, papers, reviewer responses, proposals, syllabi, lecture notes, policy briefs, letters, manuscripts, or content intended to become PDF/DOCX/slides/web.
- `ai-pipeline` — canonical AI memory under `.ai/`, such as spec, evals, review gate, session log, project state, local resources, document QA.
- `ai-working-note-candidate` — likely temporary AI scratch such as one-off prompts, notes, plans, todos, or analysis files, but only after checking that it is not a serious source document.
- `generated-output` — generated reports or exports that can be rebuilt from source.
- `unknown-review-required` — ambiguous files that must not be moved without human review.
- `archived-legacy` — files already under `.ai/archive/legacy-md/`.

## Canonical locations

```text
project/
  README.md                         # project overview for humans
  docs/                             # human-facing documentation
  documents/<document-id>/content.md # serious document source
  .ai/                              # AI working memory and pipeline metadata
  .ai/archive/legacy-md/<date>/      # old AI notes or ambiguous files, never deleted
```

## Important distinction

These are serious Markdown sources and must not be archived automatically:

```text
proposal.md
report.md
manuscript.md
paper.md
reviewer-response.md
response-to-reviewer.md
syllabus.md
lecture-notes.md
policy-brief.md
agenda.md
minutes.md
letter.md
content.md
```

These may be AI working notes, but still require classification before moving:

```text
plan.md
notes.md
todo.md
scratch.md
prompt.md
analysis.md
review.md
ideas.md
chatgpt-output.md
```

## Migration policy for existing projects

1. Inventory all Markdown files first.
2. Classify each file. Do not move files during initial inventory.
3. Treat ambiguous files as `unknown-review-required`, not as garbage.
4. Move only confirmed AI working notes into `.ai/archive/legacy-md/<date>/`.
5. Register serious document sources in `.ai/DOCUMENT_PIPELINE.md` when they are part of a document workflow.
6. Summarize useful content from old AI notes into canonical `.ai/PROJECT_STATE.md`, `.ai/EVALS.md`, `.ai/REVIEW_GATE.md`, or `.ai/SESSION_LOG.md`.
7. Delete nothing unless explicitly requested. Archive first.
8. If files were archived too aggressively, use the restore plan before continuing.

## Safer default for agents

Agents must not equate "loose Markdown" with "safe to archive".

Before moving any `.md` file, answer:

1. Is this readable by a human as part of the actual project output?
2. Is this a source document that may be exported later?
3. Is this referenced by README, docs, build scripts, Pandoc, MkDocs, Quarto, LaTeX, or website generators?
4. Does the filename contain serious terms such as report, proposal, manuscript, syllabus, lecture, response, agenda, letter, policy, paper?
5. Is it only temporary AI state that belongs in `.ai/`?

If uncertain, mark `unknown-review-required` and leave it in place.

## Bad behavior

Do not do this:

```text
find . -name '*.md' -move-to .ai/archive
```

Do not create a new `notes.md`, `plan.md`, `review.md`, or `prompt.md` at the root. Use canonical `.ai/` files instead.

## Token discipline link

The inventory is a token-saving mechanism. Future sessions should read canonical `.ai/` files first, then serious document sources, and only open archived legacy notes when needed.
