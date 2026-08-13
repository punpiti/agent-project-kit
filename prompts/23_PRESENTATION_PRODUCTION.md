# 23 — Presentation Production Workflow

Use this secondary workflow when the task must create, edit, render, export, or
final-QA a real slide/deck artifact. `05_SLIDES_TEACHING.md` remains the primary
route for audience, objective, core message, storyline, slide jobs, and delivery
logic. This workflow turns that approved presentation design into a trustworthy
PPTX, Google Slides, Keynote, PDF deck, HTML deck, or project-defined output.

## 0. Authority and production contract

Before changing slide files, resolve the project-local presentation contract:

- source of truth and editable source format;
- required deliverables and whether each is editable, review, or final output;
- toolchain and build/export commands actually available;
- canvas/aspect ratio, slide size, master/theme, grid, safe area, and margins;
- fonts, language/script metadata, fallback fonts, colors, logos, and brand rules;
- accessibility target, delivery setting, display distance, and recording/streaming constraints;
- speaker notes, handout, animation, transition, audio/video, and interaction requirements;
- asset sources, licenses, attribution, privacy, and production exclusions;
- output paths, naming/versioning policy, and approval state.

Project requirements override every 16:9, template, font, application, or export
example in this workflow. If the contract is missing and the choice changes the
real artifact, ask the user before building. Do not silently reuse a master,
theme, logo, dimensions, or export settings from another presentation.

## 1. Handoff from presentation design

Production starts only after the primary Presentation route has established:

1. audience, occasion, duration, delivery mode, and intended action;
2. one core message and a defensible storyline;
3. slide-by-slide jobs, evidence/examples, transitions, and takeaway;
4. the distinction between slide content, speaker narration, appendix, and handout.

Do not repair a weak story through decoration. If the deck structure still has
contradictory messages, missing evidence, or excessive scope, return that issue
to the primary route before polishing layouts.

## 2. Source, master, and layout system

- Preserve the project-approved editable source; generated PDF/images are not a
  substitute unless the contract declares them canonical.
- Use the approved slide master/theme and reusable layouts. Do not hand-format
  every slide independently or create hidden one-off variants without reason.
- Define a consistent grid, alignment, margins, title/body zones, figure/table
  treatment, page number/footer rules, and section-divider behavior.
- One slide has one job. Visual hierarchy must reveal that job within a few
  seconds without requiring the audience to read the entire slide.
- Keep text density, line length, type size, contrast, and visual load suitable
  for the actual room, device, stream, or recording—not merely the editor view.
- Never shrink text or charts until they technically fit. Split, simplify,
  reveal progressively, move detail to notes/appendix, or redesign the slide.
- Check all master/layout variants actually used; an unused clean master does
  not prove that individual slides are consistent.

## 3. Typography, language, and accessibility

- Verify that required fonts and weights exist on the build/render machine and
  that embedding/substitution behavior is known for every target format.
- Apply the language and script metadata required by the selected application,
  especially for Thai/Latin mixed text and spell checking.
- Maintain readable contrast, non-color cues, meaningful reading order, and alt
  text or equivalent descriptions where the target format supports them.
- Do not encode meaning only through color, position, animation, or an image of
  text. Explain essential visuals in narration/notes when needed.
- Check titles, labels, equations, legends, citations, and footnotes at delivery
  scale. A slide that looks readable at 100% editor zoom may fail in a room.
- Respect reduced-motion and accessibility constraints when animation is used.

## 4. Figures, tables, charts, equations, and media

- Every visual must serve the slide's job and be introduced by the surrounding
  slide/narration logic; decorative media must not compete with the message.
- Preserve traceability from chart/table/claim to the approved data or source.
  Record transformations, filters, units, dates, and uncertainty when relevant.
- Prefer editable/vector assets when the contract requires future revision;
  verify raster resolution at final display/export size.
- Keep captions, legends, axes, units, annotations, and source attribution
  readable. Do not crop labels, panels, or contextual information silently.
- Treat extracted figures as compositional references unless rights permit
  direct reuse. Record license/permission and create original visuals when required.
- Equations and symbols must use a consistent notation source and render without
  substitution, clipping, baseline errors, or image blur.
- Tables should support comparison at a glance. If a table requires prolonged
  reading, simplify it, stage it, move detail to a handout, or use another visual.
- Embedded audio/video must be tested on the delivery machine or exported mode;
  links, codecs, autoplay, captions, volume, and offline behavior are part of QA.

## 5. Speaker notes, timing, interaction, and motion

- Put spoken explanation in speaker notes rather than shrinking it onto slides.
  Notes should add delivery guidance, evidence, pronunciation, transitions, and
  interaction cues—not contradict the visible slide.
- Rehearse or estimate timing by section and whole deck, including questions,
  demonstrations, activities, media, and transitions. Slide count alone is not timing evidence.
- Record where audience interaction, exercise, poll, pause, or decision occurs
  and what the presenter does if time or technology fails.
- Animation and transitions need an explanatory purpose: sequence, causality,
  comparison, focus, or controlled reveal. Avoid motion that merely decorates.
- Verify animation order, triggers, duration, easing, object states, and fallback
  behavior in exported/static formats. Never assume the editor preview equals delivery.

## 6. Build, render, and export loop

1. Save/version the editable source according to project policy.
2. Run the project-approved build/export command; do not invent a parallel toolchain.
3. Capture tool/application version, fonts, plugins, linked assets, and warnings.
4. Render every slide to images or another inspectable form at target dimensions.
5. Inspect the montage/contact sheet for flow and consistency, then inspect full
   slides for overflow, clipping, substitution, chart labels, citations, and media.
6. Extract/search text when possible to detect missing content, placeholders,
   duplicated titles, unresolved tokens, and accidental author-only notes.
7. Open every required deliverable in its target viewer/application. Test links,
   notes, animation, media, and editability where those features are promised.
8. Fix the cause in the source/master and rebuild. Do not patch only a derived
   export while leaving the canonical source broken.
9. Record commands, outputs, inspections, unresolved issues, and approval in the
   project presentation pipeline/QA state.

## 7. Format-specific gates

### PPTX / editable office deck

- File opens without repair warnings in the target application.
- Master/layout references, theme colors, fonts, notes, links, media, charts,
  equations, and object editability are preserved as promised.
- No unintended font substitution, overflow, off-canvas objects, hidden review
  content, broken relationships, or missing linked assets remain.
- Test presenter view and delivery-machine behavior when available.

### Google Slides / cloud-native deck

- Confirm import/export did not alter fonts, crop, spacing, animation, notes,
  charts, or object stacking.
- Verify sharing/permission state without exposing private sources or edit access.
- Test the actual presentation link and offline/export fallback if required.

### Keynote or other native deck format

- Test in the declared native application and version.
- Verify cross-platform/export substitutions explicitly; do not claim PPTX/PDF
  compatibility from a successful native preview alone.

### PDF/static deck

- Every page has the required dimensions and orientation.
- Fonts, transparency, gradients, equations, images, links, and page ordering render correctly.
- Animation-dependent meaning has a static alternative or is declared absent.
- Inspect the actual PDF, not only the editable source.

### HTML/web presentation

- Test viewport sizes, keyboard navigation, focus order, contrast, reduced motion,
  asset loading, offline/network assumptions, printing/export, and browser support.

## 8. Final acceptance criteria

- [ ] Audience, occasion, duration, delivery mode, action, and core message remain aligned.
- [ ] Each slide has one clear job and the storyline survives montage review.
- [ ] Project master/theme, dimensions, fonts, language, brand, and accessibility rules are satisfied.
- [ ] No clipped, overflowing, substituted, low-resolution, unreadable, or unresolved content remains.
- [ ] Claims, charts, tables, figures, media, and citations are traceable and rights-safe.
- [ ] Speaker notes, timing, interactions, motion, and media behave as promised.
- [ ] Every required editable/static/web output opens and was inspected in its target environment.
- [ ] Author-only notes, placeholders, private data, and production exclusions are absent from final outputs.
- [ ] Source, build/export command, tool versions, outputs, and QA evidence are recorded.
- [ ] L2 choices needing presenter/owner judgment and L3 items needing audience rehearsal remain explicit.

Do not call a deck final because the source file saved successfully. Final means
the required outputs were rendered/opened, visually inspected, behavior-tested
in proportion to their promises, and accepted against the project contract.
