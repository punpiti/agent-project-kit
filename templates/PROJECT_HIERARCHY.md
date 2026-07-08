# PROJECT_HIERARCHY

ไฟล์นี้ประกาศว่า directory นี้เป็น project เองหรือเป็นแค่ subdirectory ธรรมดา
และถ้าเป็น project/subproject ให้สัมพันธ์กับ parent/child อย่างไร

## Project Marker

- This directory is a project: yes/no
- Project name:
- Project type: root-project / subproject / component / document-package / data-area / plain-subdir
- Parent project path:
- Parent project role:
- Child projects:
- Plain subdirectories that should not be treated as projects:

## Context Boundary

- Core concern of this project:
- What belongs here:
- What should stay in parent:
- What should stay in child:
- What should not be pulled automatically:

## Parent / Child Reading Rule

- Parent may read child summaries to understand what active child work exists.
- Parent should not load full child context unless the task requires that child.
- Child should read parent summary only for broad framing, constraints, naming,
  resource policy, or shared data assumptions.
- Child should not pull parent-wide context automatically when doing a sharp local
  task such as paper revision, figure update, or reviewer response.
- Child may read parent project files as a read-only interface/contract.
- Child must not edit parent project files, parent `.ai/` state, parent logs, or
  parent resource manifests unless the user explicitly asks for a parent-level
  change or the task is declared as a cross-project migration/update.
- If child work discovers parent information is stale, write a note in the child
  project or propose a parent update; do not silently patch the parent.
- A plain subdirectory is not a subproject unless this file, `.ai/PROJECT_STATE.md`,
  `AGENTS.md`, or another explicit marker says it is.

## Parent Encapsulation Policy

Think of the parent project as exposing a small public interface to the child:

- allowed to read: parent summary, hierarchy file, shared resource policy,
  naming conventions, high-level constraints, and explicitly referenced data
  contracts
- not allowed by default: editing parent documents, parent `.ai/` state, parent
  session logs, parent resource manifests, parent deliverables, or sibling
  projects
- escalation path: if a child needs a parent change, report the proposed change
  and wait for explicit parent-scope instruction

This keeps sharp child work local while still letting the child respect the
parent's broader constraints.

## Context Sharpness

Lower-level projects should carry sharper, task-specific state. Higher-level
projects should carry broader framing and an index of child work.

Examples:

- Root topic/workspace: broad research program, shared data/resource policy.
- Funded project: goals, deliverables, timeline, datasets, reports.
- Paper package: journal target, manuscript state, reviewer concerns, figures,
  evidence, response strategy.

## Child Project Index

| Child path | Project? | Scope / concern | Status | Read when | Last checked |
|---|---:|---|---|---|---|
| | yes/no | | active/stale/archived | | |

## Parent Summary For Child

สรุปจาก parent ที่ child ต้องรู้ โดยไม่ต้องอ่าน parent ทั้งหมด:

- 

## Child Summary For Parent

สรุปที่ parent ควรเห็นจาก child โดยไม่ต้องอ่าน child ทั้งหมด:

- 

## Example Mapping

```text
nowcast/
  root research theme: long-running nowcasting research program

nowcast/ting67/
  subproject: one funded 2567 research grant under nowcast

nowcast/ting67/amt/
  subproject/document-package: AMT journal paper/revision package within ting67
```

In this example, `ting67/amt` should keep the sharp paper/reviewer state. `ting67`
should keep grant-level framing and read the AMT child summary when needed.
`nowcast` should keep the broader research-program map and should not load full
AMT paper context unless the task explicitly concerns that paper.
