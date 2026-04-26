---
name: fact-check-ledger
description: Use when the user asks to verify claims, fact-check an article, test a speech or social media post, validate a statistic, inspect a disputed historical or current-event claim, or build a claim-by-claim evidence ledger with confidence ratings, source quality notes, method appraisal, and surrounding context.
---

# Fact Check Ledger

Use this skill for claim-level verification. The output should let the user retrace the work.

## Core Rules

- Do not fact-check in a vacuum. For consequential claims, explain the surrounding issue context needed to understand why the claim matters and what it would imply if true.
- Do not defer central verification. If a report, filing, PDF, dataset, case record, or rebuttal is integral to the claim, inspect it before assigning a status. If that cannot be done, lower confidence and say the check is incomplete.
- Each evidence row must be self-contained enough to understand the ruling. Avoid bare bullets like "scale of harm" or "intent statements" without concrete examples, citations, and explanation.
- Extract atomic claims before judging them.
- Verify with the best available primary source where possible.
- Do not use third-party aggregators for central quantitative claims when official datasets, original publications, filings, or primary records are reasonably available.
- Use more than one named source for key claims unless one source is the only relevant authority.
- Record contradictory evidence and explain whether it refutes, narrows, or contextualizes the claim.
- Do not rate an opinion as true or false; identify the factual premises inside it.
- For current events, browse and use exact dates.
- Preserve an audit trail: source URLs, publication dates, access dates when useful, and search terms or source paths for hard-to-find evidence.
- For quotes, use the original transcript/audio/video/document where possible and inspect surrounding context.
- Do not accept "peer reviewed" as enough. For scientific claims, read past the abstract and assess the research question, design, sample, intervention/exposure, comparator, outcomes, time period, model, effect sizes, uncertainty, confounder handling, missing data, conflicts, limitations, journal quality, replication, and whether the conclusion actually follows.
- Do not accept NGO, nonprofit, think-tank, or advocacy claims as self-validating. Verify their methods, data, sourcing, conflicts, and whether their conclusions follow from the evidence; list named disclosed funders above the relevant reporting threshold when available, especially government and corporate funders. A vague statement that a group is funded by "individuals, foundations, and companies" is not a funder audit; if donor names are not public, say so and treat opacity as a limitation.
- For historical claims or analogies, verify the historical facts and explain the relevant context before ruling. Check chronology, geography, definitions, mechanisms, source base, major scholarly disputes, and whether the analogy compares the right things.
- For technical or institutional claims, explain the underlying machinery enough that the ruling is meaningful. Do not only decide whether a label or number is correct.
- For claims involving named places, sacred sites, borders, legal bodies, armed groups, treaties, parties, or institutions, explain what they are and why they matter before relying on them.
- For claims based on ratings, rankings, scorecards, or indices, verify the product before using it: methodology, indicators, coders, funding, governance, ideological/institutional incentives, critiques, and whether primary evidence supports the score.
- For classification claims such as "fascist," "genocide," "coup," "authoritarian," "terrorist," or "corrupt," define the standard and apply it symmetrically. Similar conduct should not receive different labels unless the difference is explained with evidence.
- When claims involve hidden motives, covert activity, laundering, propaganda, euphemistic labels, or institutional misconduct, inspect primary records and representative cases before assigning a status. Do not defer the deeper audit if it is necessary to answer the claim.

## Verification Status

- **Supported:** strong evidence supports the claim as stated.
- **Mostly supported:** the core is supported, but wording, scope, or context needs qualification.
- **Mixed:** significant evidence supports and contradicts the claim, or different parts vary in accuracy.
- **Unsupported:** evidence is insufficient or the claim depends on unverified assertions.
- **Contradicted:** reliable evidence shows the claim is false or materially misleading.
- **Opinion/value judgment:** not directly fact-checkable, though supporting factual premises may be checked.

Confidence levels:

- **High:** primary evidence or multiple independent high-quality sources; few unresolved caveats.
- **Medium:** credible evidence but some limits, indirectness, or unresolved disagreement.
- **Low:** sparse, weak, stale, anonymous, or circular evidence.

## Workflow

1. Quote or paraphrase the claim being checked, preserving its original scope.
2. Break compound statements into atomic claims.
3. Add context: define key terms, relevant time/place, mechanism alleged, why the claim matters, and what adjacent claims must be checked to avoid a misleading narrow ruling.
4. Identify what evidence would prove or disprove each claim.
5. Search in this order:
   - Original documents, data, transcripts, filings, records, photos/video with provenance.
   - Official statistics or institutional records.
   - Peer-reviewed or specialist research, after method and quality appraisal.
   - NGO, nonprofit, think-tank, or advocacy reports, after method, data, sourcing, funding, and conflict appraisal.
   - Direct reporting from outlets with visible sourcing.
   - Fact-checkers and secondary summaries.
   - Commentary or ideological sources only for viewpoint, not final verification.
6. For scientific or quantitative claims, create a study/data readout before assigning a status:
   - What question was tested.
   - What data, sample, comparison, and time period were used.
   - What model or statistical method was used.
   - What effect size and uncertainty were reported.
   - What limitations, confounders, and alternative explanations remain.
   - Whether the public claim matches the actual result.
7. For reports, PDFs, filings, datasets, or institutional claims central to the ruling, create a document/product readout before assigning a status:
   - Who produced it and why.
   - What parts were read.
   - Methodology, evidence base, and limitations.
   - Funding, governance, and incentives where relevant.
   - Strongest rebuttal or critique.
   - Whether the document's evidence supports its headline conclusion.
8. For historical-comparison claims, make a context row before judging:
   - What historical period/event is being invoked.
   - Which mechanism is being compared.
   - What primary or specialist historical evidence supports the comparison.
   - What important differences weaken the analogy.
   - What named events, movements, doctrines, parties, documents, or institutions must be explained for the claim to be meaningful.
9. For rating, scorecard, or index claims, make a product readout before judging:
   - Who produces it and why.
   - Who funds or governs it.
   - What indicators and coding process it uses.
   - How uncertainty, expert judgment, and disagreement are handled.
   - What serious critiques exist.
   - Whether primary evidence supports the rating being cited.
10. For classification or typology claims, make a rubric row before judging:
   - Definition and threshold.
   - Evidence for each criterion.
   - Best counterexample.
   - Similar cases and whether the standard is applied consistently.
11. For hidden-purpose or institutional-misconduct claims, sample and inspect the relevant underlying cases:
   - Award/grant/contract records, program descriptions, implementers, subimplementers, budgets, inspector-general reports, congressional records, local reporting, declassified records, court filings, or leaked documents when provenance is adequate.
   - Classify evidence by stated purpose, observed activity, funding chain, strategic interest, local consent, transparency, concealment, outcomes, and harms.
12. Search for the strongest contradiction or narrowing context before assigning a status.
13. Make an evidence row for each claim.
14. Explain the ruling in plain language, including caveats and missing evidence.
15. For consequential checks, add a short adversarial review: what could make this assessment wrong or incomplete. Do not use this review to excuse skipping central evidence.
16. For broad research dossiers using this skill inside `world-research`, run that skill's preflight gate before delivery. Treat failures about deferred central evidence, weak aggregators, unsupported rubrics, or missing method readouts as blocking.

## Evidence Row Format

For each claim:

- **Claim:** exact claim or precise paraphrase.
- **Context:** relevant definitions, time/place, mechanism, and why a narrow ruling could mislead.
- **Checkable parts:** atomic factual pieces.
- **Best evidence:** source list with dates and links.
- **Source quality:** primary/specialist/reporting/commentary, proximity, method, incentives, limitations.
- **Concrete examples:** specific events, quotes, figures, cases, or documents that support or weaken the claim.
- **Study/data readout:** for key research or statistics, summarize what was actually measured, how, over what period, effect size, uncertainty, and limits.
- **Document/product readout:** for central reports, PDFs, filings, datasets, or institutional claims, summarize what was read, methodology, evidence base, limits, incentives, and rebuttals.
- **Historical context:** for historical claims or analogies, summarize period, mechanism, specialist evidence, and limits of comparison.
- **Rating/index readout:** for institutional ratings, summarize producer, funding/governance, methodology, critiques, and primary-evidence checks.
- **Rubric consistency:** for classification claims, define the standard, evidence, counterexamples, and whether similar cases are treated similarly.
- **Funding/conflicts:** named disclosed funders, undisclosed-donor limits, and conflicts, especially for NGOs, nonprofits, think tanks, advocacy groups, and scientific studies.
- **Case/audit evidence:** for hidden-purpose claims, sampled records and what they show about stated purpose versus actual function.
- **Contradictory evidence:** source list and explanation.
- **Assessment:** status plus confidence.
- **Reasoning:** why the evidence supports, narrows, or contradicts the claim.
- **Needed next:** what would improve confidence.
- **Audit trail:** key searches, source paths, dates checked, and inaccessible sources when relevant.

## Red Flags

- Circular sourcing where multiple articles repeat one unverified origin.
- Misleading denominator, time window, map scale, or jurisdiction.
- Quote fragments without full transcript or surrounding context.
- Anonymous sourcing used for factual claims that could be documented.
- Screenshots without original URL, metadata, archive, or independent capture.
- Official statements that describe policy intent but not actual implementation.
- Think-tank or advocacy claims without funding, method, or data transparency.
- NGO/nonprofit reports that summarize conclusions without transparent data, methodology, source documents, or conflict disclosures.
- Peer-reviewed papers with weak design, small or biased samples, p-hacking signs, poor measurement, undisclosed conflicts, predatory journals, retraction flags, or conclusions stronger than the data supports.
- Fact checks that skip the best argument or evidence against the emerging conclusion.
- Fact checks that rely on public category labels when the claim being tested is that those labels hide a different function.
