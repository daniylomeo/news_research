# Research Preflight Gate

Use this gate before delivering any full briefing or dossier. Its purpose is to prevent polished summaries from masquerading as research.

This gate is automatic. Do not wait for the user to request it. For broad, controversial, historical, scientific, policy, or current-events research, the user should only need to name the topic; the agent is responsible for choosing dossier mode when needed and running this gate before delivery.

## Hard Stop Conditions

Stop and revise before final output if any answer is "yes":

- Does a central conclusion depend on a report, dataset, filing, study, local record, or rebuttal that has not been inspected?
- Does any major section consist mostly of conclusion bullets without mechanisms, examples, citations, and counterarguments?
- Does the viewpoint section use generic camps instead of named people, institutions, texts, movements, parties, or schools with actual arguments?
- Does a source card accept an NGO, think tank, rating product, index, or advocacy source without method, funding/governance, incentives, and primary-evidence checks?
- Does a nonprofit/think-tank/advocacy source card summarize funding categories without listing named disclosed funders, or without explicitly flagging that donor names are unavailable?
- Does a rubric, ranking, or category judgment appear without thresholds, evidence notes, hard counterexamples, and a symmetry check?
- Does the answer use third-party aggregators where an official dataset or primary source is reasonably available?
- Does the answer compare large units such as "America," "Europe," "the West," "the Global South," "the media," or "the left/right" without decomposing them into meaningful subcases?
- Does the conclusion sound useful but leave the user unable to explain how the system works?

If a hard stop cannot be fixed in the current pass, state that the research is incomplete inside the chosen boundary and do not present a settled conclusion.

## Required Passes

Before finalizing, run these passes in order:

1. **Boundary pass:** define the exact geography, time period, population types, and comparison units. Break large aggregates into subcases.
2. **Mechanism pass:** for every major claim, explain how the system works in practice: money, law, institutions, incentives, tradeoffs, and affected people.
3. **Source-integrity pass:** replace convenient secondary/aggregator sources with official datasets, primary records, specialist literature, or clearly justified secondary sources.
4. **Named-debate pass:** replace generic camps with named voices and actual arguments; fact-check the strongest factual claim from each.
5. **Counterexample pass:** test the conclusion against cases that should break it if it is too simple.
6. **Section-quality pass:** every major section must stand alone. Rewrite or cut any paragraph that is only a compressed assertion.
7. **Adversarial-review pass:** identify what could make the conclusion wrong, without using this as an excuse for skipped central work.

## Chat Summary Rule

The final chat response must not merely summarize a weak dossier. If the dossier fails this gate, say so plainly and either continue revising or mark it as a failed draft.
