# Workflow Architecture v2

Agent Project Kit uses one orchestrator and five separate workflow dimensions.
Adding a prompt does not automatically create another peer workflow.

1. **Primary pipeline** owns the requested outcome. Exactly one is selected.
2. **Method modules** supply bounded specialist methods such as data analytics,
   content analysis, web development, research synthesis, or strategy.
3. **Lifecycle stages** describe what happens now: implementation, review,
   production, feedback, cleanup, or release.
4. **Quality gates** must pass but do not compete for method/stage slots.
5. **State actions** run only when project or machine state requires them.

`config/workflow-registry.json` is the canonical module, prompt, policy, and
composition registry. The deterministic bilingual classifier vocabulary lives
in `config/routing-rules.json`, so adding or moving a phrase needs no code edit.
Priority order, word boundaries, and combination and ambiguity logic stay in
`scripts/route_task.py`. Keeping that logic in Python keeps it testable, so the
rules file does not try to be a complete rule engine.
`python3 scripts/route_task.py --validate` rejects malformed lists, duplicate
phrases, a phrase owned by two keys of one axis, ids missing from the axes or
registry, methods without a module, and phrase lists the router does not use.
`config/routes.json`, `config/workflows.json`, `config/policies.json`, and
`prompts/catalog.json` are generated compatibility projections. Update them with:

```bash
python3 scripts/sync_workflow_registry.py --write
```

## Composition contract

- Choose the primary pipeline from the requested deliverable first, then from a
  specialist method, and finally from the surrounding domain.
- A method remains subordinate when another pipeline owns the deliverable. For
  example, survey analysis informs a policy pipeline; it does not replace it.
- Stages and gates are orthogonal. Exporting a revised book can activate Book
  Writing, Publication Production, and Prose Style without one hiding another.
- A module may reuse the primary prompt, but the compiled bundle includes each
  prompt once.
- If a category reaches its configured limit, return the omitted candidate and
  reason. Never truncate silently.
- Keep one orchestrator responsible for the final result. Split ownership only
  when instructions, tools, evidence, or approval boundaries materially differ.

## Change rule

Before adding a workflow, demonstrate all four:

1. No existing pipeline/module owns the contract.
2. The new contract changes instructions, tools, evidence, or approvals.
3. At least one routing fixture fails without it and passes with it.
4. The registry, compatibility projections, security boundary, and package
   inventory remain valid.

Prefer a gate, checklist, or tool when the behavior validates another workflow
rather than owning an outcome.
