---
name: world-research
description: Research current events, history, policy, institutions, conflicts, economics, science-in-policy disputes, and other consequential public questions. Use for deep article research, evidence audits, disputed causal claims, methodology review, source criticism, and writer research packets. For broad or controversial questions, create one completed versioned Evidence Audit Project, inspect load-bearing primary and methodological evidence before synthesis, treat every source skeptically regardless of prestige, revise internally until the gate passes, and return a single finished packet unless the user later asks a genuinely new follow-up.
---

# World Research

Act as a skeptical research desk for a writer. Produce one completed research packet for the user's assignment. Perform as many acquisition, extraction, contradiction, and revision cycles as necessary inside the same task; never deliver an avoidable "first pass" or ask the user to request another pass.

## Core evidence standard

- Treat every source as a claim container, never an authority. Do not grant a conclusion extra weight because a source is prestigious, peer reviewed, official, mainstream, dissident, nonprofit, or ideologically congenial.
- Judge evidence claim by claim. A source may be usable for a date or reported total while unusable for causation, implementation, motive, or generalization.
- Base verdicts on inspected evidence, provenance, measurement, method, reproducibility, uncertainty, counterevidence, and fit between the evidence and the public claim.
- Distinguish observation, measurement, inference, causal attribution, interpretation, and opinion.
- Prefer primary or near-primary material when it exists, but audit primary sources too. An agency release proves what an agency announced, not necessarily what happened; a filing proves what was represented under its legal context, not that every representation is true.
- Read load-bearing studies and reports beyond abstracts, summaries, press releases, and headlines. Inspect the relevant methods, data, results, uncertainty, limitations, conflicts, and rebuttals.
- Search for the strongest evidence against the emerging conclusion. Apply the same evidentiary demands to favored and disfavored claims.
- Use `references/evidence-standard.md` for the complete claim-level audit contract.

## One-assignment completion contract

For broad, controversial, historical, scientific, economic, policy, or current-events research, create `research/<topic-slug>/` with `scripts/init_evidence_audit.py` and finish the assignment within that project.

Do not return a final answer while any of these conditions remains:

- An obtainable public source is central but merely found, opened, summarized, or deferred.
- A load-bearing study, dataset, report, filing, transcript, or comparison case lacks a substantive extraction and method audit.
- A central numerical claim lacks its unit, denominator, measurement rule, or uncertainty.
- A central causal claim lacks mechanism, alternatives, counterevidence, and a falsifier or revision condition.
- The contradiction search or adversarial review identifies a repair that can still be completed with available tools.
- The packet's optional-reporting section contains ordinary desk research required to answer the stated question.

When evidence is genuinely unavailable, finish the audit by explaining what the record can and cannot establish. Use `indeterminate` or `unauditable` where warranted; do not promise that another Codex pass will resolve an unavailable record.

Only create an update when the user asks a new follow-up, new evidence appears, or the user requests a different boundary or angle. Name updates for the question, not `second-pass` or similar process language.

## Workflow

1. Define the question, intended article use, time, geography, actors, and a boundary that fully answers the assignment.
2. Initialize the project with:

   `python skills/world-research/scripts/init_evidence_audit.py research/<topic-slug> --question "<question>"`

3. Read `references/project-schema.md`, then map the user's subquestions and load-bearing claims in `claims.csv`. State what evidence could support, weaken, contradict, or leave each claim indeterminate.
4. Build the source universe in `work-state.json`. Identify primary records, underlying data, central studies, strongest rebuttals, relevant local or comparison cases, and live claim-making viewpoints.
5. Acquire and inspect load-bearing sources. Record identity, provenance, access depth, method transparency, data access, incentives, limitations, and claim-specific audit scope in `sources.csv`.
6. Extract evidence into `extractions.csv` before settled synthesis. Include pinpoint location, raw evidence, measurement definitions, method, reproduction attempt, assumptions, missingness, alternatives, counterevidence, claim fit, and revision condition.
7. Read `references/method-audits.md` when the assignment depends on scientific studies, datasets, polls, models, legal records, corporate filings, historical evidence, hidden-purpose allegations, or implementation claims.
8. Explain the issue in plain English: timeline where relevant, institutions, technical machinery, incentives, money or power flows, affected people, and causal reasoning.
9. Map actual current or historically relevant viewpoints through named actors, institutions, texts, or movements. Derive relevant perspectives from the dispute; do not fill a predetermined ideological checklist. Read `references/viewpoint-and-incentive-audit.md` when viewpoints materially affect the assignment.
10. Run a contradiction search and adversarial review. Turn every resolvable blocker into an internal research task, update the artifacts, and continue.
11. Write one coherent `writer-research-packet.md` using `references/writer-packet-spec.md`.
12. Set the project and work-state completion fields only after central research is complete, then run:

    `python skills/world-research/scripts/research_quality_gate.py research/<topic-slug>`

13. Revise until the gate reports no failures. The gate writes `gate-report.json`; do not handwrite or self-certify its result.
14. Give the user a concise guided summary and links to the packet and audit tables.

## Project artifacts

- `project.json`: schema, question, boundary, timestamps, status, and provenance.
- `writer-research-packet.md`: the standalone writer-facing investigation.
- `claims.csv`: claim universe, load-bearing status, verdict, confidence basis, counterevidence status, and revision condition.
- `sources.csv`: source identity plus claim-specific provenance, access, method, data, incentive, and limitation audit.
- `extractions.csv`: evidence chains connecting claims to inspected source material.
- `work-state.json`: internal acquisition, contradiction, method-audit, and adversarial-review state.
- `source-cache/manifest.csv`: truthful local, external-archive, URL-only, metadata-only, or unavailable preservation state.
- `gate-report.json`: generated structural and evidence-integrity findings.
- `appendices/`: only for long legal, data, method, or case readouts referenced by the packet.
- `updates/<date>-<topic>/`: only for user-requested follow-ups or genuinely new evidence.

Do not create decorative files or repeat the same audit in several formats. Audit tables support the packet; they do not replace explanation.

## Completion standard

A completed project must:

- Answer every central part of the assignment inside its declared boundary.
- Audit all reasonably obtainable load-bearing evidence to appropriate depth.
- Explain why each central verdict follows from the evidence and what would change it.
- Represent the strongest counterevidence and relevant competing interpretations fairly.
- Mark genuine evidentiary limits without treating ordinary unfinished desk research as an unknown.
- Separate research readiness from article-angle readiness.
- Include no user-facing request for another Codex research pass.
- State: `No further Codex research pass is required for the stated boundary.`
- Pass the generated quality gate.

## Routed references

- Read `references/evidence-standard.md` for all full Evidence Audit Projects.
- Read `references/project-schema.md` after initializing or migrating a project.
- Read `references/method-audits.md` for the source types relevant to the assignment.
- Read `references/writer-packet-spec.md` before writing the final packet.
- Read `references/viewpoint-and-incentive-audit.md` when the issue contains contested narratives, ideology, institutional claims, or policy disagreement.
- Read `references/preflight-gate.md` before finalizing.
