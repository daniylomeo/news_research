# Research Preflight Gate

Use this gate before delivering any full briefing, dossier, or Evidence Audit Project. Its purpose is to prevent polished summaries from masquerading as research.

This gate is automatic. Do not wait for the user to request it. For broad, controversial, historical, scientific, economic, policy, or current-events research, the user should only need to name the topic; the agent is responsible for creating an Evidence Audit Project when a writable workspace exists and running this gate before delivery. If no project folder is created, the final answer must explain why.

## Hard Stop Conditions

Stop and revise before final output if any answer is "yes":

- Does a central conclusion depend on a report, dataset, filing, study, local record, or rebuttal that has not been inspected?
- For a broad or controversial question, did the agent write a synthesis before creating claim/source/extraction artifacts?
- Does the project lack `protocol.md`, `claim-map.md`, `source-intake.csv`, `evidence-extraction.csv`, `audit-trail.md`, or `final-synthesis.md`?
- Does `final-synthesis.md` cite claims that do not appear as audited rows in `evidence-extraction.csv`?
- Are load-bearing claims missing extraction rows or explicit unauditable/incomplete rows?
- Does the audit judge source credibility by prestige, peer review, institutional status, or outsider status before inspecting data and methods?
- Does the audit ignore a dissident, conspiratorial, local, or ideological source that makes a concrete factual claim relevant to a load-bearing issue?
- Does the project or legacy dossier lack retraceable URLs or citations for the actual documents, datasets, filings, reports, and pages used?
- Do source-intake or evidence-extraction rows name documents without linking to them or stating what parts were read?
- Do study/data readouts, case audits, viewpoint maps, claim ledgers, or extraction rows make material claims without direct source links?
- Does any major section consist mostly of conclusion bullets without mechanisms, examples, citations, and counterarguments?
- Does the viewpoint section use generic camps instead of named people, institutions, texts, movements, parties, or schools with actual arguments?
- Does a source card accept an NGO, think tank, rating product, index, or advocacy source without method, funding/governance, incentives, and primary-evidence checks?
- Does any source card merely summarize what a source is instead of interrogating what it proves? A passing source interrogation card must include full-source status, exact claim used, evidence extracted, method/data, findings, validity appraisal, source weight, and limits.
- Does a central study or dataset rely on an abstract, landing page, press release, media summary, or "key findings" page instead of the full paper/report/codebook/data documentation?
- Does a nonprofit/think-tank/advocacy source card summarize funding categories without listing named disclosed funders, or without explicitly flagging that donor names are unavailable?
- For a causal question, does the answer lack a causal claim matrix with mechanism, evidence quality, alternative explanations, counterevidence, confidence, and falsifiers?
- Does any politically charged causal claim appear as narrative assertion without an evidence chain, for example by saying one actor "made" another side violent, that one side's action "caused" the other side's violence, or that a "feedback loop" exists without case-level or statistical support?
- Does a rubric, ranking, or category judgment appear without thresholds, evidence notes, hard counterexamples, and a symmetry check?
- Does the answer use third-party aggregators where an official dataset or primary source is reasonably available?
- Does the answer compare large units such as "America," "Europe," "the West," "the Global South," "the media," or "the left/right" without decomposing them into meaningful subcases?
- Does the conclusion sound useful but leave the user unable to explain how the system works?
- For policy/economic questions, does the project omit relevant economic/institutional lenses such as Austrian, Chicago/neoclassical, Keynesian, MMT, public choice, Marxian/labor, institutionalist, environmental/localist, or industrial-policy/state-capacity arguments?
- For follow-ups, did the response append a prose chapter without updating the evidence model, extraction rows, confidence levels, or synthesis revision notes?

If a hard stop cannot be fixed in the current pass, state that the research is incomplete inside the chosen boundary and do not present a settled conclusion.

## Required Passes

Before finalizing, run these passes in order:

1. **Protocol pass:** define the exact question, geography, time period, comparison units, definitions, inclusion/exclusion rules, and done criteria.
2. **Claim-universe pass:** map mainstream, academic, industry/state, local, dissident, conspiratorial, and ideological claims before judging them.
3. **Load-bearing pass:** mark the claims whose truth would change the conclusion.
4. **Evidence-type pass:** match each load-bearing claim to the evidence needed: dataset, codebook, table, model, primary record, local case, historical source, or primary text.
5. **Extraction pass:** fill `source-intake.csv` and `evidence-extraction.csv`; do not synthesize claims that lack extraction rows.
6. **Mechanism pass:** for every major claim, explain how the system works in practice: money, law, institutions, incentives, tradeoffs, and affected people.
7. **Source-integrity pass:** replace convenient secondary/aggregator sources with official datasets, primary records, specialist literature, or clearly justified secondary sources.
8. **Source-neutrality pass:** judge sources by data, methods, and reproducibility before prestige or stigma.
9. **Causal-matrix pass:** for why/cause/driver questions, build a matrix before prose: proposed cause, mechanism, evidence, evidence quality, alternatives, counterevidence, confidence, and falsifiers.
10. **Named-debate pass:** replace generic camps with named voices and actual arguments; fact-check the strongest factual claim from each.
11. **Economic/lens pass:** for policy and economic questions, run the relevant Austrian, Chicago/neoclassical, Keynesian, MMT, public-choice, Marxian/labor, institutionalist/localist/environmental, and industrial-policy/state-capacity checks.
12. **Counterexample pass:** test the conclusion against cases that should break it if it is too simple.
13. **Section-quality pass:** every major section must stand alone. Rewrite or cut any paragraph that is only a compressed assertion.
14. **Adversarial-review pass:** identify what could make the conclusion wrong, without using this as an excuse for skipped central work.

## Chat Summary Rule

The final chat response must not merely summarize a weak project or dossier. If the gate fails, say so plainly and either continue revising or mark it as a failed draft.
