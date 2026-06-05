#!/usr/bin/env python3
"""Initialize a targeted Writer Research Desk update pass."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

from init_evidence_audit import (
    CACHE_MANIFEST_HEADERS,
    EXTRACTION_HEADERS,
    SOURCE_ACQUISITION_HEADERS,
    SOURCE_HEADERS,
    THREAD_HEADERS,
    write_csv_if_missing,
    write_if_missing,
)


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def pass_packet_template(slug: str, question: str, today: str) -> str:
    title = slug.replace("-", " ").title()
    return f"""# {title} Writer Research Packet

Created: {today}

Research readiness: incomplete

Writing readiness: weak

Deliverability status: incomplete

## Assignment Brief

Question: {question}

- User's intended use:
- Article, op-ed, explainer, or decision this pass should serve:
- What the user needs to understand better than public discourse:
- Earlier-pass conclusion or open question being escalated:
- Claims or angles under consideration:
- What would make this pass useful:
- What would make this pass misleading or unusable:

## Research Boundary

- Date handling:
- Geography:
- Time period:
- Actors/institutions:
- Definitions that change the answer:
- Included in this pass:
- Excluded from this pass:
- Boundary reason:
- Completion standard:

## Source Universe Map

Map what must be read to understand the question, then rank by centrality. Coverage is not the enemy of depth; shallow coverage is.

| Source class | Examples to seek | Why it matters | Centrality | Status |
|---|---|---|---|---|
| Primary records/documents | TODO | TODO | load-bearing | not started |
| Studies/data/reports | TODO | TODO | load-bearing/contextual | not started |
| Strongest critics | TODO | TODO | adversarial | not started |
| Strongest defenders | TODO | TODO | adversarial | not started |
| Context/reporting | TODO | TODO | context/lead | not started |

## Evidence Thread Contract

This pass is not deliverable until every central thread in `{slug}-evidence-threads.csv` is complete and allows synthesis, or the packet explicitly narrows the boundary and marks unresolved work incomplete.

| Thread ID | Thread | Central? | Completion standard | Required primary sources | Status | Synthesis allowed? |
|---|---|---|---|---|---|---|
| T1 | TODO | yes | TODO | TODO | incomplete | no |

## Source Acquisition Plan

Track source targets in `{slug}-source-acquisition.csv`. A blocking source target that remains pending prevents usable/strong research readiness and promising/ready article status.

| Acquisition ID | Thread ID | Source needed | Minimum depth | Blocking if missing? | Status |
|---|---|---|---|---|---|
| A1 | T1 | TODO | full document/readout | yes | pending |

## Primary Source Readouts

For every load-bearing source, write a real readout before synthesis. The readout must show that the source was understood, not merely cited.

### Source: TODO

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

## Claim Ledger

| Claim ID | Claim | Load-bearing? | Source IDs | Status | Confidence | Article use |
|---|---|---|---|---|---|---|
| C1 | TODO | yes | S# | unaudited | incomplete | not usable yet |

## Evidence Synthesis

Do not write a settled synthesis until the source readouts, extraction rows, and central evidence threads are complete.

- What survived:
- What weakened:
- What failed:
- What remains unknown:
- What changed from the earlier pass:

## Live Viewpoints

Name actual people, institutions, publications, movements, or texts. Do not invent generic camps.

| Viewpoint | Representative source IDs | Actual argument | Evidence they rely on | What they get right | What they overstate or miss |
|---|---|---|---|---|---|
| TODO | S# | TODO | TODO | TODO | TODO |

## Article Use Memo

- Best article direction, if any:
- What can be written now:
- What cannot be written yet:
- Strongest usable claim:
- Strongest caveat:
- Most tempting but unsupported claim:
- What would embarrass the article if published:
- Current writing readiness:

## Claims To Avoid

- Claim:
- Why to avoid it:
- What evidence would be needed:

## Reporting Plan

| Source/document to get | Why it matters | Claim it would test | Where to find it | How it could change the article |
|---|---|---|---|---|
| TODO | TODO | C# | TODO | TODO |

## Hostile Professor Review

- Research readiness:
- Writing readiness:
- Would this survive a hostile professor or expert editor inside the stated boundary?:
- Strongest objection:
- Source class still missing:
- Under-read source:
- Unsupported load-bearing claims:
- Missing documents/interviews/data:
- Best counterexample:
- Most likely ideological bias:
- Required deeper research before publication:

## Adversarial Review Loop

Treat hostile review as a research loop, not a deliverable. If the reviewer identifies a missing source class, under-read source, unsupported load-bearing claim, weak method critique, or untested counterargument, return to source acquisition and extraction before synthesis.

| Iteration | Blocking critique | Research task created | Artifact updated | Resolved? |
|---|---|---|---|---|
| 1 | TODO | TODO | TODO | no |

## Quality Gate Result

Pending.

## Expert Evaluator Result

- Expert evaluator: pending
- Research readiness: incomplete
- Writing readiness: weak
- Deliverability status: incomplete
"""


def evaluator_template() -> str:
    return """# Update-Pass Adversarial Evaluation

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

## Source Comprehension Review

- Missing source classes:
- Under-read load-bearing sources:
- Readouts too thin:
- Primary records avoided:
- Studies/reports needing method readout:

## Evidence Integrity Review

- Central threads incomplete:
- Central sources not audited/publication-ready:
- Available primary sources bypassed:
- Exact quotes relying on AI transcript, aggregator transcript, snippet, or secondary summary:

## Article Use Review

- What can be written:
- What cannot be written:
- Claims that sound good but are not earned:
- Strongest counterargument:
- What would embarrass publication:

## Bias And Symmetry Review

- Left/institutional bias:
- Right/business/libertarian bias:
- Establishment/deference bias:
- Anti-establishment bias:
- Motive-language asymmetry:
- Reversal test:

## Revision Requirements

- TODO

## Final Evaluator Decision

Do not mark VERDICT: pass until every blocking issue has become a concrete research task and is resolved in the packet, source acquisition table, source rows, extraction rows, and cache manifest.
"""


def update_note_template(slug: str, question: str, today: str) -> str:
    return f"""# {slug.replace("-", " ").title()} Update

Created: {today}

Question: {question}

## Update-Pass Artifacts

- `{slug}-writer-research-packet.md`
- `{slug}-evidence-threads.csv`
- `{slug}-source-acquisition.csv`
- `{slug}-sources.csv`
- `{slug}-extractions.csv`
- `{slug}-source-cache-manifest.csv`
- `{slug}-adversarial-evaluation.md`

## Status

Research readiness: incomplete

Writing readiness: weak

Deliverability status: incomplete

This update is not complete until `research_quality_gate.py <project-dir> --pass {slug}` passes and the evaluator returns `VERDICT: pass` without unresolved blocking issues.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="Existing research project folder")
    parser.add_argument("--slug", required=True, help="Update pass slug, e.g. second-pass")
    parser.add_argument("--question", default="", help="Update-pass question or assignment")
    args = parser.parse_args()

    slug = args.slug.strip().lower()
    if not SLUG_RE.fullmatch(slug):
        parser.error("--slug must use lowercase letters, digits, and hyphens only")

    project = Path(args.project_dir)
    project.mkdir(parents=True, exist_ok=True)
    (project / "updates").mkdir(exist_ok=True)

    today = date.today().isoformat()
    question = args.question.strip() or "TODO: state the update-pass research question"

    write_if_missing(project / f"{slug}-writer-research-packet.md", pass_packet_template(slug, question, today))
    write_csv_if_missing(project / f"{slug}-evidence-threads.csv", THREAD_HEADERS)
    write_csv_if_missing(project / f"{slug}-source-acquisition.csv", SOURCE_ACQUISITION_HEADERS)
    write_csv_if_missing(project / f"{slug}-sources.csv", SOURCE_HEADERS)
    write_csv_if_missing(project / f"{slug}-extractions.csv", EXTRACTION_HEADERS)
    write_csv_if_missing(project / f"{slug}-source-cache-manifest.csv", CACHE_MANIFEST_HEADERS)
    write_if_missing(project / f"{slug}-adversarial-evaluation.md", evaluator_template())
    write_if_missing(project / "updates" / f"{today}-{slug}.md", update_note_template(slug, question, today))

    print(f"Initialized update pass '{slug}' in {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
