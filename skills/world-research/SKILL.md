---
name: world-research
description: Use when researching current events, historical events, geopolitics, policy, institutions, conflicts, social issues, economics, science-in-policy disputes, or other world affairs. For broad, controversial, policy, historical, scientific, economic, or current-events questions, automatically create an Evidence Audit Project and writer research packet in the workspace with claim map, source intake, evidence extraction, case/data audits, live viewpoint/lens analysis, angle readiness, reporting plan, quality gate, and only then synthesis unless the user explicitly asks for a quick chat-only answer.
---

# World Research

Use this skill to build high-trust evidence audits about current events, past events, policy, economics, science-in-policy disputes, and history. The default aim is to educate ourselves about the issue and find the best-supported truth, not merely to answer the narrow wording of the prompt.

## Non-negotiables

- A polished but shallow project or dossier is a failed draft. Do not deliver it as a completed answer.
- The project must answer the user's actual subquestions, not merely the topic. Use `writer-research-packet.md` as the coherent reader-facing packet and completion contract. Every central subquestion must be answered in the packet with claim/source anchors, evidence limits, and what would change the answer.
- The default deliverable is not a clever article pitch. It is a Writer Research Packet that helps the user decide what, if anything, is worth writing. Do not invent angles before the evidence earns them.
- For broad, controversial, policy, historical, scientific, economic, or current-events questions, default to an **Evidence Audit Project**, not an essay dossier. Create a folder under `research/<topic-slug>/` with auditable artifacts before synthesis. Use `scripts/init_evidence_audit.py <project-dir> --question "<question>"` when starting a new project.
- No synthesis before extraction. Do not write a settled conclusion until load-bearing claims have rows in `extractions.csv` or have been explicitly marked unauditable/incomplete. Do not use search-result snippets, previews, abstracts, landing pages, or secondary summaries as central evidence when a primary document, filing, dataset, transcript, docket, or report is reasonably available.
- Use broad intake but narrow audited claims. First map the world of claims and viewpoints; then identify the load-bearing claims whose truth would change the answer; then audit representative data, studies, cases, and source claims.
- Apply the source-neutral rule: source status is not evidence. Reputation, institutional prestige, peer review, nonprofit status, outsider status, or "whack job" status affect scrutiny and priors, not the verdict. A dissident source with better data beats a prestigious source with weak, hidden, or non-reproducible data.
- Treat every source as a claim container, not an authority. Extract the actual claims, data, assumptions, and methods; then decide whether they survive.
- For policy and economic questions, include a real Economic Perspectives chapter inside `writer-research-packet.md`: Austrian, Chicago/neoclassical, Keynesian, MMT, public choice, Marxian/labor, institutionalist, environmental/localist, industrial-policy, and security/state-capacity perspectives as relevant. Do not summarize schools from model memory or from only canonical dead thinkers. For each substantive lens, find current, issue-specific economists or active institutions/commentators representing that perspective whenever available; cite them in `sources.csv` and `extractions.csv`; then state the core claim, evidence supporting it, evidence weakening it, what it explains better than other lenses, what it misses, and a verdict. If no current representative source is found for a relevant lens, write exactly `No current issue-specific representative found; lens incomplete.` and do not give that lens a strong/complete verdict.
- For every Evidence Audit Project, run an adversarial evaluator stage before delivery. The evaluator acts as a hostile PhD examiner and must produce `VERDICT: pass`, `VERDICT: revise`, or `VERDICT: fail` in `adversarial-evaluation.md`. Deliver a settled answer only on `VERDICT: pass`; otherwise revise or mark the project incomplete.
- Treat the user's question as the starting doorway into the issue, not the full boundary of the research. Answer it directly, but also build the surrounding context needed to understand what the answer means.
- For substantial or controversial topics, produce a holistic issue model before conclusions: history, timeline, institutions, actors, incentives, definitions, mechanisms, data landscape, affected populations, policy choices, tradeoffs, and unknowns.
- Default to audit-project mode for broad, controversial, historical, scientific, economic, policy, or current-events questions whenever a writable workspace exists. Create or update a structured folder under `research/<topic-slug>/`, run the quality gate on the folder, then give the user a concise guided summary with links to the artifacts. Use chat-only full briefing only when no writable workspace exists or the user explicitly asks not to create files.
- When the user asks a follow-up question about an existing project, do not append another mini-essay. Add `updates/<YYYY-MM-DD>-<follow-up-slug>.md`, update `writer-research-packet.md`, `sources.csv`, `extractions.csv`, `source-cache/manifest.csv`, appendices, confidence levels, and verdicts if the follow-up changes the answer. Follow-ups must mutate the evidence model, not just add pages.
- Default to full briefing depth for broad public-interest questions unless the user explicitly asks for a quick answer. If the topic is too large for one pass, narrow the research boundary before concluding; do not present conclusions that depend on evidence not yet reviewed.
- For ordinary narrow questions, use standard briefing depth. For substantial public-interest topics, do not treat "I can answer in chat" as a reason to skip audit-project mode; the project artifacts are part of the quality workflow because they preserve claim maps, extraction rows, case audits, and the audit trail.
- Do not require the user to ask for audit-project mode, source intake, evidence extraction, named viewpoints, funder disclosure, contradiction search, self-review, or the quality gate. These are automatic obligations for broad, controversial, historical, scientific, economic, policy, or current-events research. The user should only need to name the topic.
- Do not deliver "first-pass" projects for the user's substantive research questions. Either complete the central audit inside a narrowed boundary or mark the project incomplete/failed and keep revising. Phrases like "first-pass national briefing," "not a full audit," or "does not estimate" are red flags when they refer to central evidence.
- For broad comparison questions, decompose large aggregates before judging. Do not compare "America" with "Europe," "the media," "the West," or similar huge categories until the analysis separates meaningful subcases, populations, regions, institutions, and person-types.
- Do not use "needs deeper review" for evidence that is central to the conclusion. If a source, PDF, filing, dataset, legal argument, local record, or case comparison is integral, inspect it in the first pass before reaching a conclusion. If that cannot be done, lower the conclusion and explicitly state that the answer is not yet complete.
- Aim for research completeness inside the agreed boundary. "Open questions" are for genuinely unavailable evidence, future developments, or peripheral leads, not for core work that should have been done.
- Make every major section self-contained. A reader should not encounter a list of claims without examples, citations, mechanism, and explanation on the assumption that another section does the real work.
- Narrative source summaries are not evidence audits. For every source that materially affects the answer, extract the source into `sources.csv` for identity/incentives/claims/access and `extractions.csv` for actual evidence, methods, critique, and confidence. For economic perspectives, the source rows must identify `economic_lens`, `representative_status`, and `issue_specificity` so the reader can see whether a claim comes from a current issue-specific economist, an active institution, adjacent current commentary, canonical background, or non-economist commentary. Narrative summaries in `writer-research-packet.md` may explain this work, but they cannot substitute for extraction rows.
- `sources.csv` must label each source's access depth: `full_document`, `partial_document`, `dataset_inspected`, `filing_inspected`, `docket_inspected`, `transcript_inspected`, `secondary_summary`, or `snippet_only`. `snippet_only` may orient the search but may not support central claims. `secondary_summary` may not support central claims when a primary source is reasonably available.
- Maintain `source-cache/manifest.csv` for every load-bearing source. Cache public filings, court opinions, datasets, agency pages, and other public documents when practical. For copyrighted articles or pages that should not be copied, preserve URL, metadata, short compliant excerpts or extraction notes, access date, and an explicit cache reason.
- Do not let audit artifacts become a costume for shallow work. Broad page ranges, headline paraphrases, and "methodology is thin" conclusions are not extraction. Use pinpoint propositions and show the mechanism by which the evidence supports, weakens, or fails the claim.
- Separate legal or institutional conclusions into layers: holding/rule, test, application, dicta, inference, prediction, and counterargument. Do not collapse them into a headline like "the law was narrowed."
- For court-case questions, use primary legal materials when available: opinions, orders, complaints, briefs, transcripts, dockets, trial findings, exhibits, and dissents. If the user asks about standing, arguments, trial, majority, dissent, or procedural history, create specific audit rows/artifacts for each.
- For methodology or quantitative-impact questions, reconstruct the unit of analysis. A criticism that a method is "not reproducible" is incomplete unless you identify the missing units, baseline, denominator, classification rule, constraints, sensitivity tests, and what result can still be inferred.
- For causal questions, do not write a narrative "causal synthesis" until completing a causal claim matrix. Each proposed cause needs mechanism, direct evidence, source quality, alternative explanations, counterevidence, confidence, and what would falsify or weaken it. Politically charged causal claims without this evidence chain are workflow failures.
- Explain the machinery of the issue. Do not merely list technical terms, institutions, actors, or incentives; explain what they are, how they work, why they matter, who controls them, and how they connect to the user's question.
- Treat historical context and historical analogies with the same rigor as current fact-checking. Do not compress major historical periods into decorative summaries. Explain the relevant chronology, mechanisms, social effects, economic data where available, major scholarly debates, and limits of the analogy.
- When naming a historical event, movement, document, doctrine, party, law, or institution that is important to the argument, explain it. Do not assume the user already knows what it was, who participated, what happened, why it mattered, or how historians interpret it.
- When naming a place, sacred site, border, institution, armed group, political party, legal body, or treaty that matters to the argument, explain what it is and why it matters. Do not let proper nouns substitute for education.
- When using a primary ideological text, speech, manifesto, doctrine, or party program, summarize the argument from the text itself: premises, enemies named, theory of power, moral claims, proposed state/society, and relevant short quotations within copyright limits.
- Prefer primary sources over media summaries whenever they are available and relevant.
- For current events or anything likely to have changed, browse and verify dates before answering.
- Separate facts, inferences, interpretations, and opinions.
- Cite sources for material claims, especially dates, numbers, quotes, allegations, legal claims, and causal claims.
- Evidence Audit Projects must contain retraceable source links. Source intake, evidence extraction, study/data readouts, case audits, viewpoint maps, claim ledgers, and audit trails should link to the actual documents, datasets, filings, reports, or pages used. A project with no URLs, source links, or extraction rows is a failed draft.
- Look for disconfirming evidence, missing context, and plausible alternative explanations.
- Label uncertainty plainly. Do not fill gaps with confident narrative.
- Make the work reproducible: preserve enough search terms, source links, dates accessed, and reasoning that the user can retrace the path.
- Use quotes carefully. When a quote matters, find the original transcript/audio/video/document where possible and inspect surrounding context before relying on it.
- Treat peer review as a starting filter, not proof of quality. When using scientific studies, read past the abstract and inspect what the study actually did: question, design, sample, exposure/intervention, comparator, outcomes, time period, model/specification, effect sizes, uncertainty intervals, confounder handling, missing data, conflicts, limitations, journal quality, replication status, and fit between evidence and claims. Put this into extraction rows, not just prose.
- Treat NGO, nonprofit, think-tank, and advocacy claims as claims, not authority. Verify their evidence, methods, data, sourcing, conflicts, and fit between evidence and conclusions, then identify their major funders when available, with special attention to government, corporate, foundation, and donor-advised funding. A generic funding summary is not enough: list named disclosed funders above the relevant reporting threshold. If a full donor list is not public, say that plainly, list whatever named funders/categories/amounts are disclosed, and treat donor opacity as a source limitation.
- Treat democracy indices, freedom ratings, human-rights scorecards, corruption indices, country rankings, and similar institutional ratings as analytical products, not facts. Before relying on them, inspect their methodology, indicators, coding process, funders, governance, ideological/institutional incentives, critiques, and whether the rating matches primary evidence.
- Do not use third-party data aggregators for central quantitative claims when official datasets or original publications are reasonably available. Aggregators can orient the search, but final evidence should come from primary/official datasets, original reports, or a clearly justified specialist source.
- Never treat "nonbiased" as a permanent property of a source. Label source type, incentives, viewpoint, method, and limits instead.
- Audit ideological bias explicitly. Check left/liberal/institutional bias, right/business/libertarian bias, establishment/deference bias, anti-establishment bias, and asymmetrical motive language. Pay special attention to whether left, liberal, NGO, academic, regulatory, state, or institutional claims are treated as neutral defaults while Austrian, libertarian, conservative, populist, business, or dissident claims are held to a higher evidence standard.
- Distinguish corporate media reporting from primary documents and from commentary. Corporate media may be useful for narrative mapping, chronology, and interviews, but should not be the endpoint when primary material exists.
- After establishing the fact base, include a debate and commentary section for contested topics. Identify mainstream, institutional, ideological, local, international, and dissident voices; steelman their arguments; identify what evidence each relies on; then fact-check their strongest factual claims.
- Debate and commentary sections must represent real debates, not generic "views." Name representative people, institutions, movements, or texts; explain their actual argument, evidence, moral frame, and strongest rebuttal. If there is not enough time or evidence to do this well, omit the section or mark it as incomplete rather than producing a shallow placeholder.
- Do not assert policy recommendations without arguing them. Present the policy problem, proposed rule, mechanism of action, expected benefit, likely tradeoffs, implementation problems, and serious counterarguments, including libertarian, Austrian, public-choice, localist, labor, environmental, industrial-policy, and other relevant schools of thought.
- For complex policy conflicts, do not imply that brief proposals solve the issue. Present policy paths as contested frameworks with prerequisites, implementation steps, tradeoffs, enforcement problems, failure modes, historical attempts, and serious objections. If a policy section cannot meet that bar, cut it or label it as a map of options only.
- Do not use scoring tables, rankings, grades, or typologies unless each score is backed by explicit evidence and a stated rubric. Apply the rubric symmetrically to favored and disfavored actors; include a consistency check for cases that appear to challenge the conclusion.
- For any comparative judgment, include hard counterexamples that might break the thesis. If the answer is "U.S. upside, Europe floor," test it against rich European cases, poor European cases, high-performing U.S. states, weak U.S. states, and different life circumstances before concluding.
- Apply equal evidentiary grace across comparisons. If one actor receives a distinction between "authoritarian," "illiberal," "racist," "imperial," and "fascist," apply the same distinctions to all actors being compared. Do not call similar behavior fascistic in one case and merely abusive in another without explaining the difference in ideology, movement form, institutional context, intent, scale, or trajectory.
- When the question alleges hidden purposes, covert action, propaganda, laundering, institutional misconduct, or euphemistic program language, do the deeper audit in the first pass: inspect primary records, award/grant data, implementers, funding chains, country examples, strategic interests, local consent, and concealment indicators before drawing conclusions.
- When the question depends on concrete projects, facilities, local conflicts, contracts, permits, subsidies, or regulatory decisions, include an initial case audit. Sample enough real cases to test the national narrative against ground-level records; do not defer this if the truth depends on implementation.
- For project-, facility-, or implementation-dependent topics, the case audit must inspect concrete named cases with direct records. Each case should include location, actor/developer/operator or agency, status/decision, power/water/money/permit/tariff facts where relevant, direct source links, and what the case proves or does not prove. Broad region summaries like "Virginia," "PJM," or "Ohio" are not enough unless tied to specific orders, dockets, projects, tariffs, or local records.
- For advocacy, industry, think-tank, NGO, nonprofit, and coalition sources, include funding, ownership, membership, donor disclosure, institutional incentives, or donor opacity notes in the source card and viewpoint map. Do not treat their reports as neutral evidence without this.
- Policy sections must be evidence-anchored. Each option needs a mechanism, implementation steps, enforcement problem, tradeoffs, serious objections, and at least one source link or case anchor.
- Evidence Audit Projects must include **Quality Gate Result** and **Expert Evaluator Result** sections in `writer-research-packet.md` reporting the gate command/result, evaluator verdict, deliverability status (`deliverable` or `excellent`), and how blocking issues were resolved. A missing evaluator result, unresolved blocking issue, or non-pass verdict is a delivery blocker.
- Evidence Audit Projects must include independent readiness verdicts: `Research readiness: incomplete|usable|strong` and `Writing readiness: weak|explanatory-only|promising|ready`. A project can be research-usable while not yet article-ready.

## Evidence Audit Workflow

1. Clarify the research question, time period, geography, actors, and desired output.
2. Set the depth contract:
   - **Quick answer:** chat only; use only when the user asks for speed or a narrow lookup.
   - **Standard audit:** use for ordinary research questions; create a claim map and limited extraction table if files are useful.
   - **Full Evidence Audit Project:** default for broad, consequential, controversial, scientific, economic, historical, policy, or current-events questions. Create a folder centered on `writer-research-packet.md`, supported by `sources.csv`, `extractions.csv`, `source-cache/manifest.csv`, appendices only when needed, updates, and adversarial evaluation.
3. Initialize the project:
   - New project: run `scripts/init_evidence_audit.py research/<topic-slug> --question "<question>"`.
   - Existing project follow-up: add an update file under `updates/`, update the packet/source/extraction/cache artifacts, then revise the verdict only if evidence changed.
4. Build an issue and claim universe before narrowing:
   - Direct user questions to answer.
   - Definitions and category boundaries that could change the answer.
   - Historical background and timeline.
   - Main institutions, actors, incentives, and affected populations.
   - Mechanisms or causal pathways proposed by each side.
   - Mainstream, academic, industry, state, local, dissident, conspiratorial, and ideological claims.
   - Data needed, data quality problems, and likely blind spots.
   - Policy tradeoffs, harms, benefits, and distributional effects.
5. Fill the opening sections of `writer-research-packet.md` before source extraction:
   - Split the user's prompt into concrete subquestions inside Question And Boundary.
   - Add Orientation, Timeline, System Explainer, Evidence Backbone, Live Viewpoints, Economic Perspectives when relevant, Causal Models, Emerging Tensions, Angle Readiness, Claims To Avoid, So What?, Reporting Plan, Writer's Current Position, Bias And Symmetry Check, Hostile Editor Review, Quality Gate Result, and Expert Evaluator Result.
   - A central subquestion is complete only when the packet cites claim/source anchors and the supporting rows exist in `extractions.csv`.
   - Do not mark any angle as promising or ready until the evidence, counterevidence, and missing-reporting sections make that status defensible.
6. Fill the Claim Map section:
   - Give each claim a stable `claim_id`.
   - Mark whether it is load-bearing.
   - Classify the evidence needed: dataset, official records, local case, study/model, primary text, historical source, expert argument, or viewpoint claim.
   - State what would confirm, weaken, or falsify the claim.
7. Build an explanatory map:
   - Define key technical terms, institutions, job categories, financial mechanisms, legal tools, and physical systems.
   - For each important noun, explain what it is, how it works, why it matters, who benefits, who pays, and what can go wrong.
   - Explain the causal chain step by step. Example: not just "transmission upgrades," but what transmission is, why large loads require it, who builds it, how costs are recovered, and why ratepayers may care.
8. Build a source plan using this priority order, while preserving source neutrality:
   - Primary documents: laws, court filings, official records, transcripts, budgets, datasets, speeches, archived pages, original video/audio, photos with provenance, direct statements.
   - High-quality specialist sources: peer-reviewed work, books from reputable presses, subject-matter experts, professional data shops, local reporters with direct access.
   - Independent corroboration: multiple outlets, local media, wire services, NGO reports, think tanks, watchdog groups, academic commentary.
   - Narrative sources: corporate media, partisan media, ideological journals, influencer commentary, official propaganda, campaign messaging.
   - Dissident or conspiratorial sources: include when they make factual claims that are influential, evidence-bearing, or challenge institutional consensus. Audit the claim and data; do not dismiss by label.
9. Fill `sources.csv` and `source-cache/manifest.csv`:
   - Record source id, title, URL/citation, source type, viewpoint, incentives/funding/ownership, claims made, data access, and whether it is eligible for central evidence.
   - Record access depth and source-cache status for load-bearing sources.
10. Fill `extractions.csv` before synthesis:
   - Each load-bearing claim needs extraction rows or an explicit "not auditable with available evidence" row.
   - Record claim id, source id, exact claim, evidence location (page/table/row/case), extracted data or quote, method notes, assumptions, exclusions, uncertainty, our critique, status, and confidence.
   - For datasets, inspect codebooks, rows/cases, ambiguous coding, missing data, and sensitivity to definitions when accessible.
   - For studies, inspect instruments, measures, model specifications, effect sizes, uncertainty, robustness, and whether conclusions follow.
11. For historical claims, comparisons, or analogies, build a historical context module before answering:
   - Establish dates, geography, sequence, and definitions.
   - Identify the relevant mechanisms, not just surface similarities.
   - Use historians, economic historians, primary historical documents, historical datasets, and reputable books or papers where possible.
   - Include social conditions, labor effects, winners and losers, political conflicts, environmental consequences, and distribution of gains.
   - Explain any named events, movements, doctrines, parties, leaders, laws, and institutions that are necessary to the comparison.
   - For movements or doctrines, explain the argument from primary sources where possible: what they claimed was wrong, who they blamed, what they wanted, how they justified power, and what they did in practice.
   - Compare similarities and differences explicitly; do not imply that a past analogy proves the present case.
12. For hidden-purpose or institutional-misconduct questions, build an audit sample before answering:
   - Choose relevant countries, programs, or cases based on the user's claim, money involved, historical controversy, and availability of primary records.
   - Inspect award/grant records, congressional or inspector-general reports, court records, declassified files, budgets, program descriptions, implementer pages, and local reporting.
   - Classify each sampled item by stated purpose, actual activities, implementer, subimplementers if available, funding chain, U.S. strategic interest, local consent, transparency, concealment, and documented outcomes or harms.
   - Do not use ordinary sector labels as proof of benign purpose when the allegation is that labels may obscure political or covert functions.
13. For project-, place-, or implementation-dependent questions, build a case audit before answering:
   - Choose representative cases across geography, project size, political context, and outcome.
   - Inspect primary local records when available: permits, zoning minutes, interconnection requests, utility filings, water agreements, tax-incentive agreements, environmental permits, litigation, community-benefit agreements, and local budgets.
   - For each case, identify the developer/operator, facility type, promised investment/jobs, permanent jobs, power demand, water demand, public subsidies, ratepayer exposure, local tax effects, land-use impacts, public process, and current status.
   - Use the case audit to test whether national claims survive contact with local implementation.
   - Do not count broad regional summaries as cases unless they are tied to specific records such as a docket, tariff order, permit, local vote, project filing, or named project.
14. For any source that materially affects the answer, write the necessary readout before using its conclusion:
   - For PDFs, reports, filings, or long documents: read the executive summary, methodology, key evidence sections, limitations, and rebuttal-relevant sections; do not rely only on a press release or headline.
   - What question the authors tested.
   - What data and method they used.
   - What result they actually found, including magnitude and uncertainty.
   - What the result does and does not prove.
   - The strongest methodological critique and whether it changes confidence.
15. For causal questions, build a causal claim matrix before the narrative:
   - Proposed cause or mechanism.
   - Evidence that supports it, with direct source links.
   - Evidence quality and whether the evidence is descriptive, correlational, quasi-experimental, experimental, causal, or only interpretive.
   - Alternative explanations and confounders.
   - Counterevidence and hard cases.
   - Confidence level and what would change it.
   - Do not use phrases like "X made Y feel," "X caused Y," "this explains," "the common pathway is," or "the feedback loop is" unless the matrix supports the claim and the prose cites the relevant evidence.
16. Triangulate facts across independent evidence. Prefer independent confirmation over repetition of the same wire story, press release, or anonymous source.
17. Map perspectives beyond U.S. party categories when relevant: liberal, conservative, socialist, libertarian, Austrian/free-market, nationalist, realist, internationalist, religious, labor, business, technocratic, populist, local/community, state/security, anti-colonial, environmental, feminist, institutionalist, dissident, conspiratorial, and other topic-specific traditions.
18. For policy/economic questions, build an evidence-tested Economic Perspectives chapter in `writer-research-packet.md`:
   - Austrian/free-market: dispersed knowledge, price signals, malinvestment, intervention effects.
   - Chicago/neoclassical: incentives, externalities, elasticities, opportunity cost, welfare tradeoffs.
   - Keynesian: demand, employment, infrastructure, public investment, coordination failures.
   - MMT: real resource constraints versus financial constraints, inflation, public capacity.
   - Public choice: rent seeking, capture, concentrated benefits, diffuse costs.
   - Marxian/labor: ownership of gains, class power, worker displacement, bargaining power.
   - Institutionalist/localist/environmental: rules, agencies, contracts, local consent, ecological limits.
   - For each relevant lens: current issue-specific representative source(s), named representatives/texts, core claim, evidence supporting, evidence weakening, comparative advantage, omissions, verdict.
   - Canonical texts such as Hayek, Keynes, Mises, Bork, Buchanan, or Marx may provide background, but they cannot substitute for current economists or active institutions speaking about the issue or a close policy analogue.
19. Build the debate/commentary map:
   - Identify major voices and dissident voices, including serious critics outside mainstream institutions.
   - Name actual representatives where possible, not generic camps.
   - Steelman each argument before critique.
   - Explain each side's moral frame, causal theory, evidence base, institutional or material incentives, and best evidence.
   - Separate what the side gets right, what it overstates, what it ignores, and what remains unknowable.
20. Analyze policy options when recommendations are relevant:
   - State the problem each option tries to solve.
   - Explain the mechanism by which it is supposed to work.
   - Identify prerequisites and implementation steps.
   - Present the best argument for it and the best argument against it.
   - Explain historical attempts or analogues where relevant.
   - Include serious ideological and economic counterarguments, especially public-choice concerns about regulatory capture, Austrian concerns about planning and dispersed knowledge, libertarian concerns about property rights and state coercion, and left/labor/environmental concerns about externalities and corporate power.
   - Identify failure modes and who bears the cost if the policy fails.
   - Distinguish "my assessment" from settled fact.
21. Fact-check the viewpoint map:
   - Identify each major voice's strongest factual claims.
   - Check those claims against the source base with the same rigor as standalone claims.
   - Separate accurate criticism, exaggerated rhetoric, unsupported claims, and value judgments.
22. If using a rubric, typology, or scorecard:
    - Define the scoring scale and threshold.
    - Provide evidence notes for each score or collapse the table into prose if evidence cannot fit.
    - Test the strongest counterexample against the rubric.
    - Explain why similar-looking cases are classified differently.
23. Run a contradiction search before finalizing: search for the strongest evidence against the emerging conclusion, including critiques from serious opposing viewpoints.
24. Convert `writer-research-packet.md` from provisional to deliverable only after extraction and source-cache work:
   - Cite audited claim ids and source ids.
   - Separate what survived, what failed, what is unknown, and what would change the answer.
   - State which load-bearing claims remain unaudited or inaccessible.
   - Ensure the packet reads as one guided investigation, not disconnected artifact summaries.
   - Add a `Claims To Avoid` section for tempting but unsupported statements the user should not publish yet.
   - Add a `Reporting Plan` with concrete documents, datasets, interviews, or records to obtain; why each matters; what claim it would test; where to find it; and how it could change the article.
25. Run the adversarial evaluator stage:
   - If subagents are explicitly authorized and available, use a separate evaluator agent with only the project artifacts and the hostile PhD evaluator rubric; do not leak the intended answer.
   - Otherwise, fill `adversarial-evaluation.md` yourself using the same hostile rubric.
   - The evaluator must identify unsupported load-bearing claims, source-integrity failures, causal gaps, quantitative/method gaps, missing counterevidence, weak article angles, missing reporting targets, and ideological bias including left/institutional bias and reverse bias.
   - Fix every blocking issue in the artifacts, not just in prose. Do not mark `VERDICT: pass` until no blocking issue remains. The evaluator must grade evidence integrity, causal inference, source preservation, counterargument handling, economic-perspective depth, ideological symmetry, live-viewpoint grounding, angle readiness, So What strength, reporting plan, reader coherence, and final-answer usefulness.
26. Run the preflight gate before finalizing, even if the user did not ask for it. For audit projects, run `scripts/research_quality_gate.py <project-dir>` and revise until it reports no failures, or mark the project as incomplete/failed. For legacy dossier files, run it on the markdown file. For chat-only full briefings, apply `references/preflight-gate.md` manually before answering and explain why no project folder was created.
27. Produce the answer with uncertainty labels, source notes, and a "what would change this assessment" section when appropriate.

## Output Standard

Default chat summary format after an audit project:

- **Research Readiness:** incomplete, usable, or strong.
- **Writing Readiness:** weak, explanatory-only, promising, or ready.
- **Research Boundary:** what this pass covers, what it does not cover, and whether this is quick, standard, or full briefing depth.
- **What The Evidence Earns:** the strongest supported interpretation, with claim/source anchors.
- **What It Does Not Earn:** claims and article angles to avoid.
- **Best Article Direction, If Any:** only if the Angle Readiness section supports it.
- **Live Viewpoints:** named current voices and what evidence their claims survive.
- **Economic/Ideological Lenses:** evidence-tested lens results when relevant.
- **System Explainer:** the machinery the user must understand to write with authority.
- **Reporting Plan:** documents, datasets, interviews, or records that would improve or change the article.
- **Artifacts:** links to the packet, source table, extraction table, source-cache manifest, appendices, updates, and evaluator result.

For audit-project mode, create a folder under `research/<topic-slug>/` with these artifacts:

- `writer-research-packet.md`: the coherent working packet and final output. It contains question/boundary, orientation, timeline, system explainer, evidence backbone, live viewpoints, economic perspectives when relevant, causal models, emerging tensions, angle readiness, claims to avoid, So What stress test, reporting plan, writer's current position, bias/symmetry check, hostile editor review, unknowns, quality gate result, and expert evaluator result.
- `sources.csv`: source inventory from all viewpoints, with incentives, access depth, primary-source availability/use, centrality, evidence limits, `economic_lens`, `representative_status`, and `issue_specificity`.
- `extractions.csv`: exact extracted evidence, method notes, assumptions, critique, status, and confidence for load-bearing claims.
- `source-cache/manifest.csv`: source preservation record for every load-bearing source, including cached path or URL, cached status, cache reason, access date, centrality, and copyright limitations.
- `appendices/`: only for genuinely long legal, data, source, or case readouts that would make the main packet unreadable. Every appendix must be referenced from `writer-research-packet.md`.
- `adversarial-evaluation.md`: hostile evaluator verdict, blocking issues, unsupported load-bearing claims, source-preservation check, economic-depth review, ideological-symmetry audit, live-viewpoint grounding, angle readiness, reporting-plan review, reader-coherence review, required revisions, and final decision.
- `updates/`: follow-up questions as evidence-model updates, not mini-essays.

Do not create a separate markdown file for every concept. Separate files are allowed only when they support the main packet and are referenced from it. Artifact sprawl is a workflow failure because it makes the research feel aimless and hides whether the final answer is actually coherent.

For follow-up questions on the same topic, keep the original project folder. Add a dated update file and change the packet/source/extraction/cache/appendix artifacts as needed. Do not overwrite earlier analysis; add revision notes when the new evidence changes a prior conclusion, confidence level, source assessment, or claim status.

Before finalizing a project or legacy dossier, scan each major section and remove or rewrite any paragraph that is only a compressed assertion. Replace it with evidence, explanation, examples, citations, and counterargument, or omit it.

Then run `scripts/research_quality_gate.py <project-dir-or-dossier-path>`. Treat any failure as a block on delivery unless the final response clearly says the project is incomplete or failed.

If the gate passes but the project has no retraceable links, thin extraction rows, or source names without document URLs, treat that as a judgment failure and revise anyway.

For the complete manual gate, read `references/preflight-gate.md`.

## Source Labels

Use labels like these, in combinations:

- **Primary/official:** original record, direct statement, law, filing, dataset, transcript.
- **Primary/nonofficial:** eyewitness media, leaked document, direct interview, archive, firsthand account.
- **Specialist:** academic, technical expert, historian, field researcher, local expert.
- **Peer-reviewed study:** evaluate methods directly before relying on it; do not treat publication status alone as decisive.
- **Corporate media/reporting:** professional newsroom report, wire report, interview, investigation.
- **Corporate media/commentary:** editorial, op-ed, pundit segment, analysis column.
- **State-affiliated:** government-funded or government-controlled outlet or institution.
- **Advocacy/ideological:** think tank, party, campaign, union, NGO, activist group, movement publication.
- **NGO/nonprofit report:** evaluate methods, data, sourcing, funding, conflicts, and whether claims follow from the evidence.
- **Commercial/industry:** trade group, company statement, investor research, lobby group.
- **Unknown/weak provenance:** anonymous post, unverifiable account, unattributed image/video, copied claim.

## Quality Checks

Before finalizing, ask:

- Are the most important claims backed by primary or near-primary evidence?
- Did I distinguish evidence from interpretation?
- Did I educate the user about the issue as a whole, not merely answer the narrowest version of the prompt?
- If the topic is too large for chat, did I use audit-project mode instead of compressing away the most important context?
- Did I complete the central research inside the stated boundary, instead of listing core missing work at the end?
- Does every major section stand on its own with evidence, examples, citations, and reasoning?
- Did I define the issue's key terms, mechanisms, actors, timeline, data limits, and tradeoffs?
- Did I explain how the technical, institutional, and financial machinery works in plain but serious detail?
- If I used history or analogy, did I research the historical period seriously rather than compressing it into a shallow comparison?
- Did I explain every important historical event, movement, doctrine, document, party, and institution I named?
- Did I explain every important place, sacred site, border, legal body, armed group, treaty, and political institution I named?
- If I used an ideological text or doctrine, did I explain its actual argument rather than summarizing its headline reputation?
- If I relied on a democracy index, NGO scorecard, nonprofit report, or institutional rating, did I inspect methodology, funding, governance, incentives, critiques, and primary evidence?
- Did I explain relevant job categories, incentives, and benefit/cost flows instead of only naming who benefits?
- Did I include a serious opposing or alternative view?
- Did I identify the major public voices and fact-check their strongest claims, not just summarize them?
- Did I include serious dissident and non-mainstream arguments when they are relevant, and steelman them before critique?
- Did I represent real debates with named actors and actual arguments, or did I invent generic "views"?
- Did I argue policy recommendations against serious alternatives and counterarguments, including libertarian/Austrian/public-choice critiques where relevant?
- If I included policy paths for a complex conflict, did I explain prerequisites, implementation, tradeoffs, enforcement problems, historical attempts, and failure modes rather than offering middle-school summaries?
- If I used a scoring table or typology, did I justify each score with evidence and apply the standard symmetrically?
- Did I give equal evidentiary grace to all compared actors, or did I use stricter language for one side and softer language for another without explaining why?
- Did I identify source incentives without using labels as a substitute for evidence?
- Did I read and assess the methods and actual results of any scientific study I rely on, rather than relying on the abstract, press release, or "peer reviewed" as a shortcut?
- Did I verify the methods, data, sourcing, and major claims in NGO/nonprofit/think-tank material instead of accepting institutional authority?
- Did I identify named major funders for NGOs, nonprofits, think tanks, and advocacy groups when they materially affect source incentives, or explicitly flag donor opacity when names are not public?
- Did I date the evidence and flag stale information?
- Did I avoid laundering corporate or partisan narratives into fact?
- Did I run the strongest available contradiction search?
- Did I preserve enough of an audit trail for the user to retrace the research?
- Did I include an adversarial self-review for major conclusions?
- If the topic involved hidden purposes or euphemistic labels, did I inspect primary award/program/case records in the first pass rather than deferring that work?
- If the topic depended on concrete projects, local implementation, permits, subsidies, or contracts, did I include an initial case audit rather than naming it as a limitation?

## Reference Standards

For methodology background and links to journalism/fact-checking standards, read `references/standards.md` when auditing or revising this skill.
