#!/usr/bin/env python3
"""Initialize a unified Evidence Audit Project folder for world-research."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


CLAIM_HEADERS = [
    "claim_id",
    "claim_text",
    "claim_type",
    "viewpoint_or_source",
    "load_bearing",
    "evidence_needed",
    "confirming_evidence_expected",
    "falsifier_or_weakener",
    "status",
    "confidence",
    "notes",
]

SOURCE_HEADERS = [
    "source_id",
    "title",
    "author_or_org",
    "date",
    "url_or_citation",
    "source_type",
    "viewpoint",
    "economic_lens",
    "representative_status",
    "issue_specificity",
    "claims_made",
    "data_access",
    "source_access",
    "audit_state",
    "primary_available",
    "primary_used",
    "centrality",
    "evidence_limit",
    "funding_ownership_incentives",
    "eligible_for_central_evidence",
    "notes",
]

THREAD_HEADERS = [
    "thread_id",
    "thread_name",
    "user_question_parts",
    "central",
    "completion_standard",
    "required_primary_sources",
    "required_artifact",
    "status",
    "blocking_gap",
    "completion_evidence",
    "synthesis_allowed",
]

SOURCE_ACQUISITION_HEADERS = [
    "acquisition_id",
    "thread_id",
    "source_needed",
    "source_class",
    "why_needed",
    "minimum_depth",
    "primary_or_best_available_standard",
    "search_status",
    "best_current_source_id",
    "access_state",
    "publication_ready",
    "blocking_if_missing",
    "acquisition_notes",
    "next_step",
]

EXTRACTION_HEADERS = [
    "claim_id",
    "source_id",
    "exact_claim",
    "evidence_location",
    "extracted_data_or_quote",
    "method_notes",
    "assumptions_or_exclusions",
    "uncertainty_or_error",
    "our_critique",
    "status",
    "confidence",
    "follow_up_needed",
]

COVERAGE_HEADERS = [
    "question_part_id",
    "user_question_part",
    "central",
    "required_primary_sources",
    "required_artifact",
    "artifact_path",
    "status",
    "blocking_gap",
    "completion_evidence",
]

CACHE_MANIFEST_HEADERS = [
    "source_id",
    "path_or_url",
    "cached_status",
    "cache_reason",
    "access_date",
    "centrality",
    "copyright_limitations",
    "notes",
]


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8", newline="\n")


def write_csv_if_missing(path: Path, headers: list[str]) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="Project folder, e.g. research/ai-data-centers")
    parser.add_argument("--question", default="", help="Research question")
    args = parser.parse_args()

    project = Path(args.project_dir)
    project.mkdir(parents=True, exist_ok=True)
    (project / "appendices").mkdir(exist_ok=True)
    (project / "source-cache").mkdir(exist_ok=True)
    (project / "updates").mkdir(exist_ok=True)

    today = date.today().isoformat()
    question = args.question.strip() or "TODO: state the research question"

    write_if_missing(
        project / "writer-research-packet.md",
        f"""# Writer Research Packet

Created: {today}

Research readiness: incomplete

Writing readiness: weak

Deliverability status: incomplete

## Question And Boundary

Question: {question}

- Date handling:
- Geography:
- Time period:
- Actors/institutions:
- Definitions that change the answer:
- Included:
- Excluded:

## Assignment Brief

- User's intended use:
- Article, op-ed, explainer, or decision this research should serve:
- What the user needs to understand better than public discourse:
- Claims or angles the user is considering:
- What would make the work useful:
- What would make the work misleading or unusable:

## Source Universe Map

Map the sources needed to understand the issue before deciding what the evidence earns.

| Source class | Examples to seek | Why it matters | Centrality | Status |
|---|---|---|---|---|
| Primary records/documents | TODO | TODO | load-bearing | not started |
| Studies/data/reports | TODO | TODO | load-bearing/contextual | not started |
| Strongest critics | TODO | TODO | adversarial | not started |
| Strongest defenders | TODO | TODO | adversarial | not started |
| Context/reporting | TODO | TODO | context/lead | not started |

## Source Acquisition Plan

Track concrete source targets in `source-acquisition.csv`. A central source target that remains pending blocks synthesis unless the boundary is explicitly narrowed.

| Acquisition ID | Thread ID | Source needed | Minimum depth | Blocking if missing? | Status |
|---|---|---|---|---|---|
| A1 | T1 | TODO | full document/readout | yes | pending |

## Evidence Thread Contract

Before synthesis, split the project into evidence threads. The project is not deliverable until every central thread in `evidence-threads.csv` is complete or the packet clearly says the project is incomplete inside the chosen boundary.

| Thread ID | Thread | Central? | Completion standard | Required primary sources | Status | Synthesis allowed? |
|---|---|---|---|---|---|---|
| T1 | TODO | yes | TODO | TODO | incomplete | no |

## Orientation

- Why this topic may matter:
- Current event hook or user doorway:
- What must be true for the story to be worth writing:
- What would make the story less interesting or wrong:

## Timeline

- TODO

## System Explainer

- Institutions and actors:
- Money, legal, technical, or operational machinery:
- Incentives and constraints:
- Definitions a reader needs:
- What a curious non-specialist must understand before judging the narrative:

## Evidence Backbone

Use this section to narrate only the evidence that matters. Every load-bearing claim must connect to `extractions.csv` rows and use `(C#, S#)` anchors.

### Claim Map

| Claim ID | Claim | Load-bearing? | Evidence needed | Falsifier or weakener | Status | Confidence |
|---|---|---|---|---|---|---|
| C1 | TODO | yes | TODO | TODO | unaudited | incomplete |

### Source Readouts

For every load-bearing source, write a real readout. Do not summarize the source's reputation or media reception as a substitute for understanding the source.

- Source ID:
- What the source is:
- What parts were read:
- Research question or institutional purpose:
- Data/method/evidence:
- What it actually says:
- What it does not prove:
- Strengths:
- Weaknesses/method limits:
- Funding/ownership/incentives:
- What media or advocates get right:
- What media or advocates overstate:
- Article/op-ed use:

### Extraction Summary

- TODO

## Live Viewpoints

Map actual living/current voices, institutions, publications, or movements. Do not invent generic camps.

| Viewpoint | Representative source IDs | Actual argument | Evidence they rely on | What they get right | What they overstate or miss |
|---|---|---|---|---|---|
| TODO | S# | TODO | TODO | TODO | TODO |

## Economic Perspectives

Include this section only when the research question has a real economic mechanism such as prices, budgets, markets, labor, taxation, subsidies, ratepayers, industry structure, regulation-as-economic-control, or resource allocation. If not economically relevant, write: `Economic perspectives: not applicable; no material economic mechanism in this research boundary.`

For economic topics, each perspective must be tested against evidence, not summarized as a slogan. Canonical thinkers may provide background, but current issue-specific representatives or active institutions must carry the lens where available.

### Austrian / Free-Market

- Current issue-specific representative source(s):
- Core claim:
- Evidence supporting:
- Evidence weakening:
- What this lens explains better than others:
- What it misses:
- Verdict:

### Chicago / Neoclassical

- Current issue-specific representative source(s):
- Core claim:
- Evidence supporting:
- Evidence weakening:
- What this lens explains better than others:
- What it misses:
- Verdict:

### Keynesian

- Current issue-specific representative source(s):
- Core claim:
- Evidence supporting:
- Evidence weakening:
- What this lens explains better than others:
- What it misses:
- Verdict:

### Public Choice

- Current issue-specific representative source(s):
- Core claim:
- Evidence supporting:
- Evidence weakening:
- What this lens explains better than others:
- What it misses:
- Verdict:

## Causal Models

| Cause or mechanism | Claim IDs | Evidence for | Evidence against | Alternatives/confounders | Verdict | Confidence |
|---|---|---|---|---|---|---|
| TODO | C1 | TODO | TODO | TODO | TODO | incomplete |

## Emerging Tensions

- Tension:
- Why it matters:
- Evidence on each side:
- What would resolve it:

## Angle Readiness

Do not pitch angles before evidence earns them. Each possible angle must say whether it is weak, explanatory-only, promising, or ready.

### Angle: TODO

- Why it might be interesting:
- Evidence currently supporting it:
- Evidence missing:
- Strongest counterargument:
- Readiness: weak

## Claims To Avoid

- Claim:
- Why to avoid it:
- What evidence would be needed:

## So What?

- Why should a reader care beyond the headline?
- What changes if the strongest interpretation is true?
- Who is made uncomfortable by this framing?
- What larger system does this reveal?
- What is the most honest boring version of the story?

## Reporting Plan

| Source/document to get | Why it matters | Claim it would test | Where to find it | How it could change the article |
|---|---|---|---|---|
| TODO | TODO | C# | TODO | TODO |

## Writer's Current Position

- Current thesis, if any:
- Confidence:
- What survived the audit:
- What failed or weakened:
- What remains unknown:

## Bias And Symmetry Check

- Left/institutional bias check:
- Right/business/libertarian bias check:
- Establishment/deference bias check:
- Anti-establishment bias check:
- Motive-language symmetry check:
- Reversal test:

## Hostile Editor Review

- Research readiness:
- Writing readiness:
- Strongest objection to the article:
- Would this survive a hostile professor or expert editor inside the stated boundary?:
- Source class still missing:
- Under-read source:
- Unsupported load-bearing claims:
- Missing documents/interviews/data:
- Best counterexample:
- Most likely ideological bias:
- Required deeper research before publication:

## Adversarial Review Loop

Treat hostile review as a research loop, not a decorative deliverable. Every blocking critique must become a source-acquisition, extraction, or packet-revision task before readiness can improve.

| Iteration | Blocking critique | Research task created | Artifact updated | Resolved? |
|---|---|---|---|---|
| 1 | TODO | TODO | TODO | no |

## Unknowns And What Would Change The Assessment

- TODO

## Quality Gate Result

Pending.

## Expert Evaluator Result

- Expert evaluator: pending
- Research readiness: incomplete
- Writing readiness: weak
- Deliverability status: incomplete
""",
    )

    write_csv_if_missing(project / "sources.csv", SOURCE_HEADERS)
    write_csv_if_missing(project / "extractions.csv", EXTRACTION_HEADERS)
    write_csv_if_missing(project / "evidence-threads.csv", THREAD_HEADERS)
    write_csv_if_missing(project / "source-acquisition.csv", SOURCE_ACQUISITION_HEADERS)
    write_csv_if_missing(project / "source-cache" / "manifest.csv", CACHE_MANIFEST_HEADERS)

    write_if_missing(
        project / "adversarial-evaluation.md",
        """# Adversarial Evaluation

VERDICT: revise

## Blocking Issues

- claim_id: TODO
  artifact: TODO
  problem: TODO
  required_fix: TODO

## Unsupported Load-Bearing Claims

- claim_id: TODO
  source_ids: TODO
  problem: TODO
  required_evidence: TODO

## Rubric

- evidence integrity:
- causal inference:
- source preservation:
- counterargument handling:
- economic-perspective depth:
- ideological symmetry:
- live-viewpoint grounding:
- angle readiness:
- so-what test:
- reporting plan:
- reader coherence:
- final-answer usefulness:

## Evidence Integrity Review

Check whether central claims rely on full documents, filings, datasets, dockets, transcripts, or inspected source pages rather than snippets, search results, press releases, or secondary summaries where primary sources were available.

Fail the project if any central evidence thread is incomplete, if any central source is only found/opened rather than audited/publication-ready, or if the packet synthesizes from secondary summaries where primary records were reasonably available.

Check `source-acquisition.csv`. Fail the project if a blocking source target remains pending while the packet gives a settled conclusion, article-ready angle, or usable/strong research readiness.

Check source readouts. Fail the project if the packet names a load-bearing study, report, legal record, dataset, transcript, or clip without explaining what it is, what parts were read, what it actually says, methods/evidence, weaknesses, and article use.

## Causal Inference Review

Check mechanisms, counterfactuals, alternatives, counterevidence, confidence, and what would falsify each causal claim.

## Source Preservation Review

Check `source-cache/manifest.csv`. Central sources must be cached when legally and practically possible, or must have explicit metadata/excerpt/access reasons when caching is not appropriate.

## Counterargument Handling Review

Check whether the strongest opposing arguments were represented with their actual evidence before being rejected.

## Economic-Perspective Depth Review

For economic/policy questions, check each relevant school for core claim, supporting evidence, weakening evidence, comparative strength, omissions, and verdict.

## Ideological Symmetry Review

Check left/institutional bias, right/business/libertarian bias, establishment/deference bias, anti-establishment bias, and motive-language asymmetry.

## Reader Coherence Review

Check whether `writer-research-packet.md` reads as one guided investigation rather than disconnected artifact summaries.

## Final-Answer Usefulness Review

Check whether the user can understand the answer, evidence, uncertainty, and strongest objections without opening random side files.

## Readiness Review

- research readiness:
- writing readiness:
- ready angles:
- claims to avoid:
- reporting needed:

## Revision Requirements

- TODO

Every blocking critique must become a concrete research task and be resolved in the artifacts before VERDICT: pass.

## Final Evaluator Decision

Do not mark VERDICT: pass until every blocking issue is fixed in `writer-research-packet.md`, `sources.csv`, `extractions.csv`, and `source-cache/manifest.csv`.
""",
    )

    print(f"Initialized Evidence Audit Project: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
