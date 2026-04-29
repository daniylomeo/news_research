#!/usr/bin/env python3
"""Initialize an Evidence Audit Project folder for world-research."""

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
    "claims_made",
    "data_access",
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
    (project / "case-audits").mkdir(exist_ok=True)
    (project / "data-audits").mkdir(exist_ok=True)
    (project / "updates").mkdir(exist_ok=True)

    today = date.today().isoformat()
    question = args.question.strip() or "TODO: state the research question"

    write_if_missing(
        project / "protocol.md",
        f"""# Evidence Audit Protocol

Created: {today}

## Research Question

{question}

## Scope

- Geography:
- Time period:
- Actors/institutions:
- Outcomes:
- Exclusions:

## Definitions

- Key terms:
- Category boundaries that could change the answer:

## Done Criteria

- Claim map includes the major mainstream, academic, industry/state, local, dissident, conspiratorial, and ideological claims.
- Load-bearing claims are marked.
- Central sources are logged in `source-intake.csv`.
- Load-bearing claims have extraction rows in `evidence-extraction.csv` or are explicitly marked unauditable/incomplete.
- Relevant case/data audits and sensitivity tests exist.
- Final synthesis cites audited claim ids and source ids.
""",
    )

    write_if_missing(
        project / "claim-map.md",
        """# Claim Map

Use this file to map the full claim universe before deciding what is true.
Do not judge sources by prestige here; identify what claim they make and what evidence would decide it.

## Claim Universe

| Claim ID | Claim | Viewpoint/source | Evidence needed | Load-bearing? | Falsifier/weakener | Status |
|---|---|---|---|---|---|---|
| C1 | TODO | TODO | TODO | yes/no | TODO | unaudited |

## Load-Bearing Claims

- C1: TODO

## Claims Logged But Not Audited Yet

- TODO
""",
    )

    write_csv_if_missing(project / "source-intake.csv", SOURCE_HEADERS)
    write_csv_if_missing(project / "evidence-extraction.csv", EXTRACTION_HEADERS)
    write_csv_if_missing(project / "claim-register.csv", CLAIM_HEADERS)

    write_if_missing(
        project / "lens-review.md",
        """# Viewpoint And Economic Lens Review

Use relevant lenses as diagnostic tools, not decorations.

## Named Viewpoints

| Viewpoint/source | Actual argument | Strongest evidence | Incentives/blind spots | Claims to audit |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | TODO |

## Economic And Ideological Lenses

- Austrian/free-market:
- Chicago/neoclassical:
- Keynesian:
- MMT:
- Public choice:
- Marxian/labor:
- Institutionalist/localist/environmental:
- Industrial policy/security/state capacity:
""",
    )

    write_if_missing(
        project / "sensitivity-tests.md",
        """# Sensitivity Tests

Record definition changes, recoding tests, outlier removal, alternate model assumptions, and hard counterexamples.

| Test ID | Claim ID | Change tested | Result | Does conclusion change? |
|---|---|---|---|---|
| S1 | TODO | TODO | TODO | TODO |
""",
    )

    write_if_missing(
        project / "audit-trail.md",
        f"""# Audit Trail

Created: {today}

## Searches

- TODO

## Documents/Data Checked

- TODO

## Access Gaps

- TODO
""",
    )

    write_if_missing(
        project / "final-synthesis.md",
        """# Final Synthesis

Status: incomplete until the quality gate passes.

## Audited Claim Basis

- TODO: cite claim ids and source ids used for each conclusion.

## What Survived The Audit

- TODO

## What Failed Or Was Overstated

- TODO

## What Remains Unknown

- TODO

## What Would Change This Assessment

- TODO

## Quality Gate Result

Pending.
""",
    )

    print(f"Initialized Evidence Audit Project: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
