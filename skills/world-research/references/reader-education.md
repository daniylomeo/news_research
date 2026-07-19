# Reader Education Contract

Use this contract for every Writer Research Packet. The audit tables prove that research was performed; the packet must transfer the resulting knowledge to a reader who has not performed it.

## Reader Baseline

Assume an intelligent non-specialist with no prior topic knowledge. The reader must not need to open a source, CSV, appendix, or claim ledger to learn the background, event sequence, institutional machinery, evidence basis, uncertainty, or article relevance. Those artifacts exist for verification and deeper exploration.

Only the user may authorize a different baseline. Record both `Reader-baseline exception authorized by user: yes` and a concrete `Reader-baseline exception reason` in the Assignment Brief. Do not infer expertise from the prompt, the writer's confidence, or prior work in the project.

## Coverage Contract

Create `reader-education.csv` before drafting conclusions. Register a separate module for:

- every central reader question and every load-bearing claim that needs explanation;
- every historical or comparative case used materially;
- every legal, financial, technical, or institutional mechanism the argument requires;
- every modern controversy whose component claims could be confused;
- every dataset, quotation, or source dispute that readers must understand to evaluate the article.

Do not let one broad row such as “historical comparisons” stand in for several unexplained episodes. A source readout is not a substitute for a case module.

Map each central education module to its audited `claim_ids`, and ensure every load-bearing claim is covered by at least one central module. A claim may require several modules, but one general module may not stand in for unrelated questions, mechanisms, or controversies. Create separate modules when the subjects differ.

## Module Form

Use one `###` subsection in `## Education Brief` for every central module. Write connected prose under these visible fields:

1. **Reader orientation.** Establish time, place, institutions, actors, stakes, and unfamiliar terms.
2. **What happened or how it works.** Give a chronological narrative or step-by-step mechanism. Separate motive, access, attempt, immediate outcome, durable effect, and later consequence when relevant.
3. **Evidence guide.** Name and link the principal sources in human-readable form. Explain what each source is, what relevant evidence it contains, why that evidence bears on the account, and how its source type affects interpretation. Add claim/source identifiers only after this explanation.
4. **Dispute and limits.** Explain source bias, missing records, scholarly or institutional disagreement, alternative explanations, representativeness, and what the module cannot prove.
5. **Why it matters.** State how the module strengthens, weakens, or bounds the user's thesis, identify the strongest counterlesson, and give a publication-safe use.

Each field must contain a substantive prose explanation. Markdown or HTML tables, bullets, blockquotes, labels, fenced or indented code, HTML comments, and repeated filler do not count as narrative. Only rendered-visible prose counts. The subsection heading must exactly match the registered `packet_heading`; a prefix such as `M1` may not reuse `M10`.

Use additional fields such as actors and aims, stakes, outcome, or publication-safe takeaway when they improve comprehension. Do not force every subject into an identical length. Depth should follow complexity and importance.

## Citation Experience

- Never ask opaque identifiers such as `C201` or `S090` to carry meaning that is absent from the prose.
- Give a human-readable source name and direct link near the material claim.
- Use a real HTTP(S) target and a descriptive source label; `click here`, fragment links, script targets, and opaque IDs do not qualify.
- Explain the evidentiary bridge: why the document, dataset, testimony, or scholarship supports the sentence.
- Put at least one valid `(C<number>, S<number>)` extraction pair inside the Evidence guide after the human-readable explanation.
- Write that anchor as an explicit pair. Separate crossed citations such as `(C001, S002); (C002, S001)` do not validate `(C001, S001)` merely because all four identifiers appear nearby.
- Keep the pair visible in rendered text. IDs hidden in URL destinations, HTML comments, code blocks, or other nonrendered surfaces do not count.
- Distinguish primary account, later scholarship, official finding, advocacy, allegation, and inference.
- Give pinpoint pages, sections, tables, docket entries, or timestamps when practical.
- Treat source access as optional verification for the reader, not required homework.

## Tables And Compression

Teach before compressing. Comparison tables, verdict matrices, timelines, scorecards, and claim ledgers may recap completed modules but may not introduce unfamiliar cases as unexplained rows. Place the narrative first. Every case-comparison or comparison-matrix table must include a `Module ID` column, and every material row must put exactly one standalone, rendered-visible registered ID in that column; an ID in another cell, comment, or longer token does not count. The registered subject must materially match the row rather than share one generic word. This applies to Markdown and HTML tables and does not depend on the heading's wording. If a table mentions a material case not registered and taught as a module, revise or remove it.

## Cold-Reader Test

After the packet is complete, give only `writer-research-packet.md` to an independent evaluator who has not seen the source files, extraction tables, research notes, intended answer, or prior evaluator conclusions. Record the result in `cold-reader-evaluation.md` and mark `Other artifacts consulted: no`.

For every central module, the evaluator must be able to answer from the packet alone:

- What is this institution, event, system, or dispute?
- Who are the actors, and what did each want?
- What happened in sequence, or how does the mechanism work?
- Which named sources support the account, and why are they probative?
- What remains disputed or unknown?
- How does the module strengthen, weaken, or limit the thesis?

Any material failure returns the packet to revision. Do not fix a cold-reader failure by adding a caveat to the evaluator; fix the educational narrative itself.

The evaluation must contain exactly one substantive passing row per central module, affirmative answers for all five comprehension dimensions, exact unqualified `yes` answers to the three summary questions, `Case comprehension failures: none`, `Required revisions: none`, and substantive `cold_reader_notes` in `reader-education.csv`. Put explanatory rationale on separate labeled lines. Each dimension cell must reconstruct that module with distinct, topic-specific explanatory prose; repeated “yes” strings, two copied terms padded with filler, or generic assurances are not evidence of comprehension. Contradictory negative prose, unfinished placeholders, any qualified “yes” or “none,” `Other artifacts consulted: no, except ...`, any named non-packet artifact, or any later active, passive, or multiline admission that another artifact was opened invalidate the pass.

## Common Failure Pattern

Bad:

> Jugurtha gained delay and favorable decisions, then lost the war (C201-C202, S090-S091).

This is traceable but not educational. It assumes knowledge of Jugurtha, Numidia, Rome's role, the succession dispute, Sallust's allegations, the war, and the source controversy.

Good work first orients the reader to Numidia and the Roman Republic, introduces the rival claimants, narrates the appeals and alleged bribery, explains Sallust's political and temporal distance, describes the later Roman intervention and Jugurtha's defeat, and then states the bounded imperial-center lesson.
