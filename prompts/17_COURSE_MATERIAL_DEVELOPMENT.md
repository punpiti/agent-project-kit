# 17 — Course Material Development

Use for syllabi, lesson plans, modules, exercises, assessments, rubrics,
examples, instructor notes, and learner-facing materials.

## Route

1. Identify learners, prerequisites, delivery setting, duration, and constraints.
2. Define observable learning outcomes before producing content.
3. Align explanation, example, practice, feedback, and assessment to each outcome.
4. Control cognitive and visual load; distinguish must-know from enrichment.
5. Check accuracy, inclusivity, accessibility, workload, and feasibility.
6. Reuse course-level context and approved outcomes; do not redo curriculum
   discovery for every lesson.
7. Treat learner/instructor feedback and learning results as L3 evidence, not as
   something content generation alone can settle.

Use the presentation prompt for slides, document production for handouts, and
data analytics only when learner/course evidence is being analyzed.

## Prose Content Development (Concept Outline → Master Outline → Prose)

Use this when a lesson, module, or chapter must be written as connected
explanatory prose (not just a slide deck or bullet list) and needs to stay
traceable to sources rather than invented from general knowledge. It lets a
short presentation concept grow into fully structured, cited exposition
without fabricating content along the way. Three stages, run in order —
do not skip to prose before the master outline is checked:

1. **Concept outline** — capture the minimum content that must be covered
   (from an existing slide deck, syllabus line item, or the instructor's
   stated scope). Treat this as a floor, not a draft to prune: everything in
   it must survive into the master outline, verified and expanded rather
   than cut for being inconvenient.
2. **Master outline** — for each concept-outline point, open and actually
   read the reference sources (see "Large Reference Source Ingestion" in
   `AGENTS.md` for format-native extraction and caching; do not duplicate that guidance here) to
   find the definitions, reasoning, mechanisms, numbers, scope, and
   exceptions behind it. Build nested bullets:
   - **Main bullet** = one self-contained claim, ordered the way the source
     reasons about it (e.g., scope → classification → role → application →
     limitation), not the order it occurs to the writer.
   - **Nested bullets, up to 3 levels**: level 1 expands a main component,
     level 2 gives the reasoning/relationship/mechanism behind it, level 3
     gives evidence-sourced numbers, examples, or exceptions. Only go to
     level 3 when it adds real information from a source — not to hit a
     target depth. Drop to 2 levels when the source genuinely lacks that
     much detail.
   - **Fake-hierarchy trap**: indentation must mean "inherits from / is more
     specific than" its parent, never "comes after" or "is like." Equal-rank
     steps of one process, parallel special cases of the same rule, and
     comparisons/contrasts (watch for "in contrast," "similarly," "also")
     stay as sibling bullets at the same level, even if that leaves the
     branch short of 3 levels.
   - Every bullet must trace back to a source actually opened and read for
     this task. If it can't be traced: delete it, leave it open for more
     research, or mark it explicitly as the author's own editorial judgment
     — never attribute an unverified claim to a source.
   - Check this against every bullet, section by section, and fix what
     fails before moving on — this is a gate, run once per section, not a
     style preference. Writing prose on top of an outline with shallow
     nesting or unresolved fake hierarchy forces a rewrite of the prose
     later; catching it in the outline is far cheaper.
3. **Prose** — only after a section's master outline passes the check above:
   - One main bullet becomes one paragraph, in bullet order; nested bullets
     become the reasoning, examples, and detail woven into that paragraph,
     not restated as a list.
   - Paragraph shape: main claim → reasoning/mechanism → example or evidence
     → comparison or implication.
   - Cite every sourced claim where it's used. Do not narrate the writing
     process in reader-facing text ("the slides say...", "the source
     explains...") — state the knowledge directly and cite it.
   - Where a point should be expanded but evidence is genuinely missing,
     insert an explicit placeholder naming what's missing and where to look
     — never invent content to fill the gap.
   - Keep the outline/evidence file (bullets, citations, source notes)
     separate from the reader-facing prose file, so the outline remains the
     audit trail and the prose stays clean, continuous reading.
