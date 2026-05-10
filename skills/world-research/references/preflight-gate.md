# Research Preflight Gate

Use this gate before delivering any full briefing, dossier, or Evidence Audit Project. Its purpose is to prevent polished summaries from masquerading as research.

This gate is automatic. For broad, controversial, historical, scientific, economic, policy, or current-events research, the user should only need to name the topic; the agent is responsible for creating an Evidence Audit Project when a writable workspace exists and running this gate before delivery.

## Hard Stop Conditions

Stop and revise before final output if any answer is "yes":

- Does the project lack `research-brief.md`, `sources.csv`, `extractions.csv`, `source-cache/manifest.csv`, or `adversarial-evaluation.md`?
- Does `research-brief.md` fail to read as one coherent investigation with question/boundary, bottom line, timeline, claim map, causal model, source/evidence audit, economic perspectives when relevant, bias/symmetry check, unknowns, quality gate result, and expert evaluator result?
- Does the user need to open random side files to understand the answer, evidence, uncertainty, and strongest objections?
- Are there markdown artifacts outside `research-brief.md`, `adversarial-evaluation.md`, `appendices/`, or `updates/` that are not referenced from the main brief?
- Does a central conclusion depend on a report, dataset, filing, study, local record, or rebuttal that has not been inspected?
- Does `research-brief.md` cite claims that do not appear as audited rows in `extractions.csv`?
- Does `research-brief.md` cite source IDs that do not appear in extraction rows supporting audited claims?
- Are load-bearing claims missing extraction rows or explicit unauditable/incomplete rows?
- Does any central source or extraction row rely on a search-result snippet, preview, abstract, landing page, press release, or secondary summary where a primary document, filing, dataset, docket, transcript, report, or source page was reasonably available?
- Does `sources.csv` omit source-access depth, primary-source availability/use, centrality, or evidence limits?
- Is any central source marked `snippet_only`, or marked `secondary_summary` while a primary source was available and not used?
- Does any load-bearing source lack a `source-cache/manifest.csv` row with cached status, access date, cache reason, centrality, and copyright limitations?
- Does the audit judge source credibility by prestige, peer review, institutional status, or outsider status before inspecting data and methods?
- Does the audit ignore a dissident, conspiratorial, local, or ideological source that makes a concrete factual claim relevant to a load-bearing issue?
- Does the project lack retraceable URLs or citations for the actual documents, datasets, filings, reports, and pages used?
- Do source or extraction rows name documents without linking to them or stating what parts were read?
- Does any major section consist mostly of conclusion bullets without mechanisms, examples, citations, and counterarguments?
- For a causal question, does the answer lack a causal model or matrix with mechanism, evidence quality, alternative explanations, counterevidence, confidence, and falsifiers?
- For economic or policy questions, does the Economic Perspectives chapter lack current issue-specific economists or active institutions/commentators for the relevant schools?
- Does the Economic Perspectives chapter avoid real per-lens headings, making individual lens checks hard to audit?
- Are economic perspectives summarized from canonical theory, famous dead thinkers, or model memory instead of actual current representatives speaking about the issue or a close policy analogue?
- Does any substantive economic lens lack a cited current issue-specific representative source and also fail to say exactly `No current issue-specific representative found; lens incomplete.`?
- Does any lens marked incomplete still give itself a strong or complete verdict?
- Does `sources.csv` omit `economic_lens`, `representative_status`, or `issue_specificity` for economic-perspective sources?
- Does any economic lens lack extraction rows for the representative's actual argument?
- For economic or policy questions, does the Economic Perspectives chapter lack named representatives/texts, core claim, supporting evidence, weakening evidence, comparative strength, omissions, and verdict for relevant schools?
- Does the viewpoint or economic review grant easier evidentiary treatment to any ideological camp?
- Does the audit show left/liberal/institutional bias by treating regulators, NGOs, academia, foundations, unions, state actors, or liberal-left claims as neutral defaults while market, Austrian, libertarian, conservative, populist, business, or dissident claims require more evidence?
- Does the audit show reverse bias by overcorrecting into pro-business, anti-state, anti-left, anti-institutional, or anti-expert assumptions?
- Does the audit describe one side's motives as public-spirited while describing another side's motives as self-interested without symmetrical incentive analysis?
- Does a central study or dataset rely on an abstract, landing page, press release, media summary, or "key findings" page instead of the full paper/report/codebook/data documentation?
- Does the answer use third-party aggregators where an official dataset or primary source is reasonably available?
- Does a rubric, ranking, or category judgment appear without thresholds, evidence notes, hard counterexamples, and a symmetry check?
- Does the conclusion sound useful but leave the user unable to explain how the system works?
- Does `adversarial-evaluation.md` lack `VERDICT: pass`, or list unresolved blocking issues or unsupported load-bearing claims?
- Does the evaluator fail to grade evidence integrity, causal inference, source preservation, counterargument handling, economic-perspective depth, ideological symmetry, reader coherence, and final-answer usefulness?
- Does `research-brief.md` lack a `Quality Gate Result` section or `Expert Evaluator Result` section?
- Does the final deliverability status remain anything other than `deliverable` or `excellent`?

If a hard stop cannot be fixed in the current pass, state that the research is incomplete inside the chosen boundary and do not present a settled conclusion.

## Required Passes

Before finalizing, run these passes in order:

1. **Brief-structure pass:** build `research-brief.md` around question/boundary, bottom line, timeline, claim map, causal model, evidence audit, economic perspectives if relevant, bias/symmetry check, unknowns, evaluator result, and quality gate.
2. **Claim-universe pass:** map mainstream, academic, industry/state, local, dissident, conspiratorial, and ideological claims before judging them.
3. **Load-bearing pass:** mark the claims whose truth would change the conclusion.
4. **Extraction pass:** fill `sources.csv`, `extractions.csv`, and `source-cache/manifest.csv`; do not synthesize claims that lack extraction rows.
5. **Mechanism pass:** for every major claim, explain how the system works in practice: money, law, institutions, incentives, tradeoffs, and affected people.
6. **Source-integrity pass:** replace convenient secondary/aggregator sources with official datasets, primary records, specialist literature, or clearly justified secondary sources.
7. **Source-preservation pass:** cache public central sources where lawful/practical; otherwise record metadata, compliant excerpts/extraction notes, access date, and cache reason.
8. **Causal-matrix pass:** for why/cause/driver questions, build a matrix before prose.
9. **Quantitative-reconstruction pass:** for numerical impact claims, reconstruct row-level units and show baseline, denominator, classification rule, assumptions, constraints, confidence, and sensitivity.
10. **Economic/lens pass:** for policy and economic questions, find current issue-specific economists or active institutions/commentators for each relevant perspective, extract their actual argument into `extractions.csv`, and test each perspective against evidence instead of summarizing it from theory.
11. **Ideological-bias pass:** check left/liberal/institutional bias, right/business/libertarian bias, establishment/deference bias, anti-establishment bias, and motive-language symmetry.
12. **Counterexample pass:** test the conclusion against cases that should break it if it is too simple.
13. **Reader-coherence pass:** verify the main brief can stand alone. Move only long support into referenced appendices.
14. **Adversarial-evaluator pass:** fill `adversarial-evaluation.md` as a hostile PhD examiner. Do not deliver a settled answer unless the final verdict is pass.

## Adversarial Evaluator Template

Use this structure in `adversarial-evaluation.md`:

```text
VERDICT: pass | revise | fail

BLOCKING ISSUES:
- claim_id:
  artifact:
  problem:
  required_fix:

UNSUPPORTED LOAD-BEARING CLAIMS:
- claim_id:
  source_ids:
  problem:
  required_evidence:

RUBRIC:
- evidence integrity:
- causal inference:
- source preservation:
- counterargument handling:
- economic-perspective depth:
- ideological symmetry:
- reader coherence:
- final-answer usefulness:

BIAS VERDICT:
- left/institutional bias detected: yes/no
- right/business/libertarian bias detected: yes/no
- establishment/deference bias detected: yes/no
- anti-establishment bias detected: yes/no
- examples:
- required revisions:

FINAL EVALUATOR DECISION:
```
