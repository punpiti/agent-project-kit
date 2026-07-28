# 13 — Research Project Prompts

ใช้เมื่อโปรเจคที่กำลังทำอยู่เป็นงานวิจัย, manuscript, proposal, literature
synthesis, policy research, product/market research, หรือ decision brief ที่ต้อง
แยก evidence, source credibility, competing interpretations, และ limitation
ให้ชัด

ให้ใช้ร่วมกับ Spec-Eval-Loop:

- L1 = ค้น/สรุป/จัด matrix/วิเคราะห์ข้อมูล
- L2 = framing, thesis, audience, academic judgment, decision context
- L3 = reviewer feedback, expert consensus, updated evidence, external data

ห้าม claim เกินหลักฐาน และต้องแยก `established`, `debated`, `uncertain`,
`outdated`, และ `needs verification` ให้ชัด

## 1. Deep Dive

```text
Research [topic] in depth.

Find the most credible sources, competing perspectives, and the current
consensus among experts. Separate what is established from what is still
debated or uncertain. Cite every factual claim with source, date, and source
type. Flag where the evidence is weak, outdated, or discipline-specific.

Output:
1. Executive summary
2. Established findings
3. Active debates
4. Competing perspectives
5. Evidence quality and source credibility
6. What would change the conclusion
7. References / citations
```

## 2. Literature Review

```text
I'm writing about [topic].

Find the most important studies, papers, reviews, datasets, and expert opinions
from the last 5 years. Summarize each one in 2-3 sentences. Explain the method,
sample/data, key finding, limitation, and relevance to my project.

Flag anything that contradicts the mainstream view and explain why it matters.
Separate foundational older works from recent evidence.

Output as a table:
- citation
- year
- evidence type
- method/data
- finding
- limitation
- relevance
- supports / challenges / complicates the mainstream view
```

## 3. Counter-Argument Finder

```text
Here is my thesis: [paste your argument].

Attack it as a skeptical reviewer. Find the strongest counter-arguments, the
evidence that weakens or disproves it, the causal assumptions I am making, and
the blind spots I am ignoring.

Be direct and rigorous. I need to know where this falls apart before a reviewer,
committee, editor, or stakeholder finds it.

Output:
1. Strongest counter-arguments
2. Evidence against the thesis
3. Hidden assumptions
4. Missing controls / alternative explanations
5. Claims that overreach the evidence
6. Minimum revision needed to make the argument defensible
```

## 4. Source Credibility Check

```text
I found these claims about [topic]: [paste claims].

Verify each claim. For each one, tell me if it is true, partially true, false,
unverifiable, outdated, or taken out of context. Name the original source if
possible, the publication/update date, the data source, and whether newer data
or corrections exist.

Flag claims that are commonly misquoted, overgeneralized, cherry-picked, or
valid only under specific conditions.

Output as a table:
- claim
- verdict
- best original source
- date / latest update
- evidence
- caveat
- corrected wording
```

## 5. Competitive Intel

```text
Research [company, product, tool, platform, policy option, or method] and its
top 5 alternatives or competitors.

For each one, find pricing/cost, strongest feature, biggest weakness, evidence
of adoption or performance, customer/user complaints, switching cost, and fit
for my decision context: [describe context].

Use credible sources. Separate vendor claims from independent evidence.

Output as a comparison table I can use to make a decision, followed by:
1. Best option if cost matters most
2. Best option if quality/performance matters most
3. Best option if risk/lock-in matters most
4. Decision risks and missing information
```

## 6. Trend Spotter

```text
What are the most significant developments in [industry or topic] from the last
90 days?

Focus on developments that are likely to still matter in 12 months, not short
hype cycles. For each development, explain who it affects, what changes, why it
matters, what evidence supports it, and what to do about it.

Separate:
- confirmed developments
- early signals
- speculation
- hype/noise

Output as a ranked brief with citations and dates.
```

## 7. Data Interpreter

```text
Here is a dataset/report: [paste or upload].

Analyze it like a research analyst. Find the 3 most important patterns, the 1
thing that does not fit, and the conclusion the data supports that is not
obvious at first glance.

Show your reasoning. Distinguish descriptive patterns from causal claims. Flag
missing data, measurement problems, confounders, and any conclusion the data
does not support.

Output:
1. Data/source summary
2. Three strongest patterns
3. Anomaly or inconsistency
4. Non-obvious conclusion
5. What cannot be concluded
6. Follow-up analysis needed
```

## 8. Expert Breakdown

```text
Explain [complex topic] the way a PhD advisor would explain it to a first-year
student.

Start with why it matters. Then walk through the core concepts in order. Use
real examples from the field, not analogies. Define technical terms only when
needed. End with the one thing most beginners misunderstand and how to avoid
that mistake.

Output:
1. Why this matters
2. Core concepts in order
3. Real examples
4. Common misunderstanding
5. What to read or test next
```

## 9. Research Brief

```text
I need to decide about [describe the decision].

Build me a research brief. Cover the key facts, risks, alternatives, evidence,
and the best path given the decision context. Keep it under 500 words.

Write it so I can read it once and decide. Include confidence level, main
uncertainties, and what evidence would change the recommendation.

Output:
- Decision
- Recommendation
- Key evidence
- Risks
- Alternatives
- Confidence
- What would change the recommendation
```

## Research Project Startup Prompt

```text
This is a research project.

Read AGENTS.md and .ai/agent-project-kit first. Then read project-local
.ai/ state files. Identify the research object, thesis/question, audience,
evidence base, active manuscript/proposal files, and current uncertainty.

Before doing new research, classify the task:
- Deep dive
- Literature review
- Counter-argument check
- Source credibility check
- Competitive/alternative analysis
- Trend scan
- Data interpretation
- Expert explanation
- Decision brief

Then choose the matching prompt from
.ai/agent-project-kit/prompts/13_RESEARCH_PROJECT_PROMPTS.md and adapt it to
the current project. Do not browse or scan broadly unless the task requires
current evidence or source verification. If current evidence matters, cite
sources and dates.
```
