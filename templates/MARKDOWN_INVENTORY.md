# MARKDOWN_INVENTORY

Purpose: classify Markdown files so serious document sources, human-facing documentation, and AI working notes do not get mixed together.

Last updated: YYYY-MM-DDTHH:MM:SS
Machine: <machine>

## Inventory

| File | Role | Status | Confidence | Recommended action | Notes |
|---|---|---|---:|---|---|
| `README.md` | human-facing-doc | active | high | keep | Project overview |
| `documents/example/content.md` | document-source | active | high | register | Add to `.ai/DOCUMENT_PIPELINE.md` |
| `.ai/PROJECT_STATE.md` | ai-pipeline | active | high | keep | Canonical project state |
| `notes.md` | ai-working-note-candidate | active | medium | review-before-archive | May contain useful context |
| `.ai/archive/legacy-md/2026-07-07/old-plan.md` | archived-legacy | archived | medium | review-for-restore | Check if over-archived |

## Latest classification summary

- Markdown files inventoried: 0
- Human-facing docs: 0
- Document sources: 0
- AI pipeline files: 0
- AI working note candidates: 0
- Unknown / review required: 0
- Archived legacy files included: 0

## Restore candidates

Files listed here may have been archived too aggressively and should be restored manually or via restore mode after review.

| Archived file | Suggested original path | Reason | Action |
|---|---|---|---|

## Notes

- Do not delete Markdown files.
- Do not archive serious document sources.
- Register serious document sources in `.ai/DOCUMENT_PIPELINE.md`.
