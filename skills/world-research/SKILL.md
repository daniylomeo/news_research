---
name: world-research
description: Use when researching current events, historical events, geopolitics, policy, institutions, conflicts, social issues, economics, science-in-policy disputes, or other world affairs. For broad, controversial, policy, historical, scientific, or current-events questions, automatically create a research dossier file in the workspace, include source cards and named viewpoint analysis, run the quality gate, then summarize and link the dossier unless the user explicitly asks for a quick chat-only answer.
---

# World Research

Use this skill to build high-trust research briefings about current events, past events, and history. The default aim is to educate ourselves about the issue and find the best-supported truth, not merely to answer the narrow wording of the prompt.

## Non-negotiables

- A polished but shallow dossier is a failed draft. Do not deliver it as a completed answer.
- Treat the user's question as the starting doorway into the issue, not the full boundary of the research. Answer it directly, but also build the surrounding context needed to understand what the answer means.
- For substantial or controversial topics, produce a holistic issue model before conclusions: history, timeline, institutions, actors, incentives, definitions, mechanisms, data landscape, affected populations, policy choices, tradeoffs, and unknowns.
- Default to dossier mode for broad, controversial, historical, scientific, policy, or current-events questions whenever a writable workspace exists. Create or update a structured markdown dossier under `research/<topic-slug>.md`, run the quality gate, then give the user a concise guided summary with a file link. Use chat-only full briefing only when no writable workspace exists or the user explicitly asks not to create a file.
- Default to full briefing depth for broad public-interest questions unless the user explicitly asks for a quick answer. If the topic is too large for one pass, narrow the research boundary before concluding; do not present conclusions that depend on evidence not yet reviewed.
- For ordinary narrow questions, use standard briefing depth. For substantial public-interest topics, do not treat "I can answer in chat" as a reason to skip dossier mode; the file is part of the quality workflow because it preserves source cards, claim ledgers, case audits, and the audit trail.
- Do not require the user to ask for dossier mode, source cards, named viewpoints, funder disclosure, contradiction search, self-review, or the quality gate. These are automatic obligations for broad, controversial, historical, scientific, policy, or current-events research. The user should only need to name the topic.
- For broad comparison questions, decompose large aggregates before judging. Do not compare "America" with "Europe," "the media," "the West," or similar huge categories until the analysis separates meaningful subcases, populations, regions, institutions, and person-types.
- Do not use "needs deeper review" for evidence that is central to the conclusion. If a source, PDF, filing, dataset, legal argument, local record, or case comparison is integral, inspect it in the first pass before reaching a conclusion. If that cannot be done, lower the conclusion and explicitly state that the answer is not yet complete.
- Aim for research completeness inside the agreed boundary. "Open questions" are for genuinely unavailable evidence, future developments, or peripheral leads, not for core work that should have been done.
- Make every major section self-contained. A reader should not encounter a list of claims without examples, citations, mechanism, and explanation on the assumption that another section does the real work.
- Explain the machinery of the issue. Do not merely list technical terms, institutions, actors, or incentives; explain what they are, how they work, why they matter, who controls them, and how they connect to the user's question.
- Treat historical context and historical analogies with the same rigor as current fact-checking. Do not compress major historical periods into decorative summaries. Explain the relevant chronology, mechanisms, social effects, economic data where available, major scholarly debates, and limits of the analogy.
- When naming a historical event, movement, document, doctrine, party, law, or institution that is important to the argument, explain it. Do not assume the user already knows what it was, who participated, what happened, why it mattered, or how historians interpret it.
- When naming a place, sacred site, border, institution, armed group, political party, legal body, or treaty that matters to the argument, explain what it is and why it matters. Do not let proper nouns substitute for education.
- When using a primary ideological text, speech, manifesto, doctrine, or party program, summarize the argument from the text itself: premises, enemies named, theory of power, moral claims, proposed state/society, and relevant short quotations within copyright limits.
- Prefer primary sources over media summaries whenever they are available and relevant.
- For current events or anything likely to have changed, browse and verify dates before answering.
- Separate facts, inferences, interpretations, and opinions.
- Cite sources for material claims, especially dates, numbers, quotes, allegations, legal claims, and causal claims.
- Dossiers must contain retraceable source links. Source cards, study/data readouts, case audits, viewpoint maps, claim ledgers, and audit trails should link to the actual documents, datasets, filings, reports, or pages used. A dossier with no URLs or source links is a failed draft.
- Look for disconfirming evidence, missing context, and plausible alternative explanations.
- Label uncertainty plainly. Do not fill gaps with confident narrative.
- Make the work reproducible: preserve enough search terms, source links, dates accessed, and reasoning that the user can retrace the path.
- Use quotes carefully. When a quote matters, find the original transcript/audio/video/document where possible and inspect surrounding context before relying on it.
- Treat peer review as a starting filter, not proof of quality. When using scientific studies, read past the abstract and inspect what the study actually did: question, design, sample, exposure/intervention, comparator, outcomes, time period, model/specification, effect sizes, uncertainty intervals, confounder handling, missing data, conflicts, limitations, journal quality, replication status, and fit between evidence and claims.
- Treat NGO, nonprofit, think-tank, and advocacy claims as claims, not authority. Verify their evidence, methods, data, sourcing, conflicts, and fit between evidence and conclusions, then identify their major funders when available, with special attention to government, corporate, foundation, and donor-advised funding. A generic funding summary is not enough: list named disclosed funders above the relevant reporting threshold. If a full donor list is not public, say that plainly, list whatever named funders/categories/amounts are disclosed, and treat donor opacity as a source limitation.
- Treat democracy indices, freedom ratings, human-rights scorecards, corruption indices, country rankings, and similar institutional ratings as analytical products, not facts. Before relying on them, inspect their methodology, indicators, coding process, funders, governance, ideological/institutional incentives, critiques, and whether the rating matches primary evidence.
- Do not use third-party data aggregators for central quantitative claims when official datasets or original publications are reasonably available. Aggregators can orient the search, but final evidence should come from primary/official datasets, original reports, or a clearly justified specialist source.
- Never treat "nonbiased" as a permanent property of a source. Label source type, incentives, viewpoint, method, and limits instead.
- Distinguish corporate media reporting from primary documents and from commentary. Corporate media may be useful for narrative mapping, chronology, and interviews, but should not be the endpoint when primary material exists.
- After establishing the fact base, include a debate and commentary section for contested topics. Identify mainstream, institutional, ideological, local, international, and dissident voices; steelman their arguments; identify what evidence each relies on; then fact-check their strongest factual claims.
- Debate and commentary sections must represent real debates, not generic "views." Name representative people, institutions, movements, or texts; explain their actual argument, evidence, moral frame, and strongest rebuttal. If there is not enough time or evidence to do this well, omit the section or mark it as incomplete rather than producing a shallow placeholder.
- Do not assert policy recommendations without arguing them. Present the policy problem, proposed rule, mechanism of action, expected benefit, likely tradeoffs, implementation problems, and serious counterarguments, including libertarian, Austrian, public-choice, localist, labor, environmental, industrial-policy, and other relevant schools of thought.
- For complex policy conflicts, do not imply that brief proposals solve the issue. Present policy paths as contested frameworks with prerequisites, implementation steps, tradeoffs, enforcement problems, failure modes, historical attempts, and serious objections. If a policy section cannot meet that bar, cut it or label it as a map of options only.
- Do not use scoring tables, rankings, grades, or typologies unless each score is backed by explicit evidence and a stated rubric. Apply the rubric symmetrically to favored and disfavored actors; include a consistency check for cases that appear to challenge the conclusion.
- For any comparative judgment, include hard counterexamples that might break the thesis. If the answer is "U.S. upside, Europe floor," test it against rich European cases, poor European cases, high-performing U.S. states, weak U.S. states, and different life circumstances before concluding.
- Apply equal evidentiary grace across comparisons. If one actor receives a distinction between "authoritarian," "illiberal," "racist," "imperial," and "fascist," apply the same distinctions to all actors being compared. Do not call similar behavior fascistic in one case and merely abusive in another without explaining the difference in ideology, movement form, institutional context, intent, scale, or trajectory.
- When the question alleges hidden purposes, covert action, propaganda, laundering, institutional misconduct, or euphemistic program language, do the deeper audit in the first pass: inspect primary records, award/grant data, implementers, funding chains, country examples, strategic interests, local consent, and concealment indicators before drawing conclusions.
- When the question depends on concrete projects, facilities, local conflicts, contracts, permits, subsidies, or regulatory decisions, include a first-pass case audit. Sample enough real cases to test the national narrative against ground-level records; do not defer this if the truth depends on implementation.

## Research Workflow

1. Clarify the research question, time period, geography, actors, and desired output.
2. Build an issue map before narrowing:
   - Direct user questions to answer.
   - Definitions and category boundaries that could change the answer.
   - Historical background and timeline.
   - Main institutions, actors, incentives, and affected populations.
   - Mechanisms or causal pathways proposed by each side.
   - Data needed, data quality problems, and likely blind spots.
   - Policy tradeoffs, harms, benefits, and distributional effects.
3. Build an explanatory map:
   - Define key technical terms, institutions, job categories, financial mechanisms, legal tools, and physical systems.
   - For each important noun, explain what it is, how it works, why it matters, who benefits, who pays, and what can go wrong.
   - Explain the causal chain step by step. Example: not just "transmission upgrades," but what transmission is, why large loads require it, who builds it, how costs are recovered, and why ratepayers may care.
4. Set the depth contract:
   - **Quick answer:** use only when the user asks for speed or a narrow lookup.
   - **Standard briefing:** use for ordinary narrow research questions; include issue context, source map, viewpoint map, and key uncertainties.
   - **Full research briefing:** use for broad, consequential, controversial, scientific, historical, or policy questions; include source cards, study/data readouts, debate/commentary, contradiction search, and adversarial self-review.
   - **Dossier mode:** default for broad, consequential, controversial, scientific, historical, policy, or current-events questions when a writable workspace exists; write the longform research notes to `research/<topic-slug>.md`, run `scripts/research_quality_gate.py`, revise until it passes or mark incomplete, and give the user a concise guided summary.
   - If full coverage is impossible in one response, narrow the research boundary before concluding. Do not answer beyond the evidence actually reviewed.
5. Create a working claim ledger: known facts, contested claims, open questions, key terms, and claims implied by the user's framing.
6. Build a source plan using this priority order:
   - Primary documents: laws, court filings, official records, transcripts, budgets, datasets, speeches, archived pages, original video/audio, photos with provenance, direct statements.
   - High-quality specialist sources: peer-reviewed work, books from reputable presses, subject-matter experts, professional data shops, local reporters with direct access.
   - Independent corroboration: multiple outlets, local media, wire services, NGO reports, think tanks, watchdog groups, academic commentary.
   - Narrative sources: corporate media, partisan media, ideological journals, influencer commentary, official propaganda, campaign messaging.
7. For historical claims, comparisons, or analogies, build a historical context module before answering:
   - Establish dates, geography, sequence, and definitions.
   - Identify the relevant mechanisms, not just surface similarities.
   - Use historians, economic historians, primary historical documents, historical datasets, and reputable books or papers where possible.
   - Include social conditions, labor effects, winners and losers, political conflicts, environmental consequences, and distribution of gains.
   - Explain any named events, movements, doctrines, parties, leaders, laws, and institutions that are necessary to the comparison.
   - For movements or doctrines, explain the argument from primary sources where possible: what they claimed was wrong, who they blamed, what they wanted, how they justified power, and what they did in practice.
   - Compare similarities and differences explicitly; do not imply that a past analogy proves the present case.
8. For hidden-purpose or institutional-misconduct questions, build an audit sample before answering:
   - Choose relevant countries, programs, or cases based on the user's claim, money involved, historical controversy, and availability of primary records.
   - Inspect award/grant records, congressional or inspector-general reports, court records, declassified files, budgets, program descriptions, implementer pages, and local reporting.
   - Classify each sampled item by stated purpose, actual activities, implementer, subimplementers if available, funding chain, U.S. strategic interest, local consent, transparency, concealment, and documented outcomes or harms.
   - Do not use ordinary sector labels as proof of benign purpose when the allegation is that labels may obscure political or covert functions.
9. For project-, place-, or implementation-dependent questions, build a case audit before answering:
   - Choose representative cases across geography, project size, political context, and outcome.
   - Inspect primary local records when available: permits, zoning minutes, interconnection requests, utility filings, water agreements, tax-incentive agreements, environmental permits, litigation, community-benefit agreements, and local budgets.
   - For each case, identify the developer/operator, facility type, promised investment/jobs, permanent jobs, power demand, water demand, public subsidies, ratepayer exposure, local tax effects, land-use impacts, public process, and current status.
   - Use the case audit to test whether national claims survive contact with local implementation.
10. Collect sources and make a source card for each important source:
   - Title, author/organization, date, URL or citation.
   - Source type and proximity to event.
   - Direct link to the document, dataset, page, filing, or archive used. Do not rely on named-source references without URLs when web sources are available.
   - What parts were actually read or inspected.
   - Evidence offered and method used.
   - Ownership, funding, institutional incentives, or conflicts where relevant.
   - For NGOs/nonprofits/think tanks: methods, data, source trail, claim support, named disclosed funders above the relevant reporting threshold, especially government agencies, corporate donors, major foundations, and industry-linked support. Do not substitute vague phrases like "funded by individuals, foundations, and companies" for named funder disclosure; if names are unavailable, record the opacity.
   - For ratings, indices, and scorecards: funders, governance, methodology, indicators, coding process, country experts or coders, uncertainty handling, known critiques, and primary evidence supporting or contradicting the rating.
   - For scientific studies: research question, design, population/sample, exposure/intervention, comparator, outcome measures, time period, effect sizes, uncertainty intervals, controls/confounders, missing data, model choices, sensitivity analyses, data/code availability, limitations, conflicts of interest, journal/publisher reputation, and replication or retraction concerns.
   - For historical sources: author expertise, period covered, primary-source base, school of interpretation, evidence used, major scholarly disputes, and limits of the analogy or comparison.
   - Apparent viewpoint or ideological tradition where relevant.
   - Limits, omissions, and what it cannot prove.
11. For any source that materially affects the answer, write the necessary readout before using its conclusion:
   - For PDFs, reports, filings, or long documents: read the executive summary, methodology, key evidence sections, limitations, and rebuttal-relevant sections; do not rely only on a press release or headline.
   - What question the authors tested.
   - What data and method they used.
   - What result they actually found, including magnitude and uncertainty.
   - What the result does and does not prove.
   - The strongest methodological critique and whether it changes confidence.
12. Triangulate facts across independent evidence. Prefer independent confirmation over repetition of the same wire story, press release, or anonymous source.
13. Map perspectives beyond U.S. party categories when relevant: liberal, conservative, socialist, libertarian, Austrian/free-market, nationalist, realist, internationalist, religious, labor, business, technocratic, populist, local/community, state/security, anti-colonial, environmental, feminist, institutionalist, dissident, and other topic-specific traditions.
14. Build the debate/commentary map:
   - Identify major voices and dissident voices, including serious critics outside mainstream institutions.
   - Name actual representatives where possible, not generic camps.
   - Steelman each argument before critique.
   - Explain each side's moral frame, causal theory, evidence base, institutional or material incentives, and best evidence.
   - Separate what the side gets right, what it overstates, what it ignores, and what remains unknowable.
15. Analyze policy options when recommendations are relevant:
   - State the problem each option tries to solve.
   - Explain the mechanism by which it is supposed to work.
   - Identify prerequisites and implementation steps.
   - Present the best argument for it and the best argument against it.
   - Explain historical attempts or analogues where relevant.
   - Include serious ideological and economic counterarguments, especially public-choice concerns about regulatory capture, Austrian concerns about planning and dispersed knowledge, libertarian concerns about property rights and state coercion, and left/labor/environmental concerns about externalities and corporate power.
   - Identify failure modes and who bears the cost if the policy fails.
   - Distinguish "my assessment" from settled fact.
16. Fact-check the viewpoint map:
   - Identify each major voice's strongest factual claims.
   - Check those claims against the source base with the same rigor as standalone claims.
   - Separate accurate criticism, exaggerated rhetoric, unsupported claims, and value judgments.
17. If using a rubric, typology, or scorecard:
    - Define the scoring scale and threshold.
    - Provide evidence notes for each score or collapse the table into prose if evidence cannot fit.
    - Test the strongest counterexample against the rubric.
    - Explain why similar-looking cases are classified differently.
18. Run a contradiction search before finalizing: search for the strongest evidence against the emerging conclusion, including critiques from serious opposing viewpoints.
19. Run the preflight gate before finalizing, even if the user did not ask for it. For dossier mode, run `scripts/research_quality_gate.py <dossier-path>` and revise until it reports no failures, or mark the dossier as a failed/incomplete draft. For chat-only full briefings, apply `references/preflight-gate.md` manually before answering and explain why no dossier file was created.
20. Produce the answer with uncertainty labels, source notes, and a "what would change this assessment" section when appropriate.
21. End with an adversarial self-review for substantial research: what could be wrong, what sources may be missing, and what assumptions are doing work. Do not use this section to excuse missing central research; complete central research first or narrow the answer.

## Output Standard

Default briefing format:

- **Bottom Line:** concise answer with confidence level.
- **Research Boundary:** what this pass covers, what it does not cover, and whether this is quick, standard, or full briefing depth.
- **Direct Answer:** answer the user's specific questions without losing important caveats.
- **Issue Map:** definitions, timeline, actors, institutions, incentives, mechanisms, data landscape, and affected groups needed to understand the issue.
- **How The System Works:** explain key machinery, actors, technical terms, financial flows, jobs, institutions, and causal chains in enough detail for a curious non-specialist to understand the issue.
- **What We Know:** verified facts with citations.
- **What Is Contested:** claims with competing evidence.
- **Context:** relevant history, institutions, incentives, chronology, and policy tradeoffs.
- **Historical Context And Analogy:** when history is relevant, provide a real historical briefing with dates, mechanisms, social/economic effects, scholarly debates, and specific similarities/differences.
- **Historical Explainers:** explain important named events, movements, documents, doctrines, parties, and institutions in enough depth that the user can understand the comparison without outside background.
- **Study And Data Readouts:** for key studies, estimates, and datasets, explain the methodology, data, effect size, uncertainty, limitations, and how much weight the evidence deserves.
- **Institutional Rating Readouts:** for democracy/freedom/human-rights/corruption/risk indices or scorecards, explain methodology, funding, governance, critiques, and primary evidence checks before relying on the rating.
- **Source Map:** primary, specialist, corporate media, advocacy/ideological, and unknown/low-quality sources.
- **Viewpoint Map:** major interpretations and what each gets right or misses.
- **Debate And Commentary:** mainstream, institutional, ideological, local, international, and dissident voices; steelman each serious argument; fact-check key factual claims.
- **Evidence For And Against:** when weighing a central claim, each point should include concrete examples, source links, and explanation. Do not use bare numbered assertions.
- **Case Or Project Audit:** for project-, place-, policy-, or implementation-dependent topics, sampled real cases with primary records where available.
- **Policy Options And Counterarguments:** argued options, mechanisms, tradeoffs, implementation risks, and serious objections from relevant political/economic traditions.
- **Rubric And Consistency Check:** for classification questions, define the rubric, justify scores with evidence, and test cases that could overturn or complicate the conclusion.
- **Audit Sample:** for hidden-purpose or institutional-misconduct topics, sampled programs/cases with stated purpose, evidence of actual function, funding chain, strategic interest, local consent, concealment indicators, and limits.
- **Open Questions:** genuinely unavailable evidence, future developments, or peripheral leads; do not put central missing work here.
- **Audit Trail:** key searches, documents checked, dates accessed, and unresolved source gaps when the research is substantial.

For dossier mode, create a markdown file under a project research folder, such as `research/<topic-slug>.md`, with these sections. This is the default for broad, controversial, historical, scientific, policy, and current-events research when a writable workspace exists:

- Executive summary.
- Research boundary and questions.
- Explainer: how the system works.
- Chronology and historical context.
- Source cards.
- Study and data readouts.
- Case or project audits.
- Viewpoint and commentary map.
- Policy options and counterarguments.
- Claim ledger.
- Open questions limited to genuinely unavailable evidence, future developments, or peripheral leads.
- Audit trail.

Before finalizing a dossier, scan each major section and remove or rewrite any paragraph that is only a compressed assertion. Replace it with evidence, explanation, examples, citations, and counterargument, or omit it.

Then run `scripts/research_quality_gate.py <dossier-path>`. Treat any failure as a block on delivery unless the final response clearly says the dossier is incomplete or failed.

If the gate passes but the dossier has no retraceable links, thin source cards, or source names without document URLs, treat that as a judgment failure and revise anyway.

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
- If the topic is too large for chat, did I use or suggest dossier mode instead of compressing away the most important context?
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
- If the topic depended on concrete projects, local implementation, permits, subsidies, or contracts, did I include a first-pass case audit rather than naming it as a limitation?

## Reference Standards

For methodology background and links to journalism/fact-checking standards, read `references/standards.md` when auditing or revising this skill.
