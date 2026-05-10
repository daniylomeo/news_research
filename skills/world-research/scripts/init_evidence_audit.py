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
    "primary_available",
    "primary_used",
    "centrality",
    "evidence_limit",
    "funding_ownership_incentives",
    "eligible_for_central_evidence",
    "notes",
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
        project / "research-brief.md",
        f"""# Research Brief

Created: {today}

Status: incomplete

Deliverability: incomplete

## Question And Boundary

Question: {question}

- Date handling:
- Geography:
- Time period:
- Actors/institutions:
- Definitions that change the answer:
- Included:
- Excluded:

## Bottom Line

- Direct answer:
- Confidence:
- What would change the answer:

## Timeline

- TODO

## Claim Map

| Claim ID | Claim | Load-bearing? | Evidence needed | Falsifier or weakener | Status | Confidence |
|---|---|---|---|---|---|---|
| C1 | TODO | yes | TODO | TODO | unaudited | incomplete |

## Causal Model

| Cause or mechanism | Claim IDs | Evidence for | Evidence against | Alternatives/confounders | Verdict | Confidence |
|---|---|---|---|---|---|---|
| TODO | C1 | TODO | TODO | TODO | TODO | incomplete |

## Source And Evidence Audit

Use this section to narrate only the evidence that matters. Every load-bearing claim must connect to `extractions.csv` rows and use `(C#, S#)` anchors.

### Source Readouts

- TODO

### Extraction Summary

- TODO

## Economic Perspectives

For economic or policy topics, each perspective must be tested against evidence, not summarized as a slogan.

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

## Bias And Symmetry Check

- Left/institutional bias check:
- Right/business/libertarian bias check:
- Establishment/deference bias check:
- Anti-establishment bias check:
- Motive-language symmetry check:
- Reversal test:

## Unknowns And What Would Change The Assessment

- TODO

## Adversarial Evaluation

Expert evaluator: pending

Deliverability status: incomplete

## Quality Gate Result

Pending.

## Expert Evaluator Result

Pending.
""",
    )

    write_csv_if_missing(project / "sources.csv", SOURCE_HEADERS)
    write_csv_if_missing(project / "extractions.csv", EXTRACTION_HEADERS)
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
- reader coherence:
- final-answer usefulness:

## Evidence Integrity Review

Check whether central claims rely on full documents, filings, datasets, dockets, transcripts, or inspected source pages rather than snippets, search results, press releases, or secondary summaries where primary sources were available.

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

Check whether `research-brief.md` reads as one guided investigation rather than disconnected artifact summaries.

## Final-Answer Usefulness Review

Check whether the user can understand the answer, evidence, uncertainty, and strongest objections without opening random side files.

## Revision Requirements

- TODO

## Final Evaluator Decision

Do not mark VERDICT: pass until every blocking issue is fixed in `research-brief.md`, `sources.csv`, `extractions.csv`, and `source-cache/manifest.csv`.
""",
    )

    print(f"Initialized Evidence Audit Project: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
