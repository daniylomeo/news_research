#!/usr/bin/env python3
"""Initialize a version 2 world-research Evidence Audit Project."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date
from pathlib import Path

from research_gate.schema import (
    CLAIM_HEADERS,
    EXTRACTION_HEADERS,
    GATE_VERSION,
    MANIFEST_HEADERS,
    READER_EDUCATION_HEADERS,
    SCHEMA_VERSION,
    SOURCE_HEADERS,
)


def write_text_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8", newline="\n")


def write_json_if_missing(path: Path, value: dict) -> None:
    if not path.exists():
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def write_csv_if_missing(path: Path, headers: tuple[str, ...]) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        csv.writer(handle).writerow(headers)


def project_id_from_path(path: Path) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", path.name.lower()).strip("-")
    return value or "evidence-audit"


def packet_template(question: str, today: str) -> str:
    return f"""# Writer Research Packet

Created: {today}

Research readiness: incomplete

Writing readiness: weak

## Assignment And Boundary

Question: {question}

- Reader baseline: intelligent non-specialist
- Assumed prior knowledge: none
- Knowledge-transfer goal: explain the background, mechanism, evidence, uncertainty, and article relevance without requiring another artifact

Intended article use:

Time, geography, actors, and definitions:

Boundary and why it fully answers the assignment:

## Bottom Line

Do not synthesize until load-bearing evidence has been extracted and audited.

## How The System Works

Explain the history, institutions, technical machinery, incentives, causal pathways, and affected people required to understand the answer.

## Education Brief

Register each central reader question, mechanism, controversy, and material comparison in `reader-education.csv`, then teach it here in connected prose before using tables or compressed verdicts.

## Evidence By Claim

Explain each load-bearing verdict with assigned claim and source anchors. Include the strongest evidence, method quality, counterevidence, alternatives, confidence basis, and what would change the assessment.

## Method And Data Audits

Explain what central studies, datasets, reports, filings, or records actually did: provenance, measurement, method, magnitude, uncertainty, reproduction, limitations, and claim fit.

## Contradictions And Competing Explanations

Present the strongest contrary evidence and alternative mechanisms before deciding what survives.

## What Cannot Be Established

List only genuine unavailable, future, proprietary, sealed, destroyed, or nonexistent evidence. Do not place unfinished obtainable desk research here.

## Article Directions

Assess possible directions only after the evidence earns them. State evidence, strongest objection, optional original reporting, and readiness.

## Claims To Avoid

Identify tempting unsupported claims and the evidence required before publication.

## Optional Original Reporting

Include only interviews, FOIA or public-record requests, site visits, proprietary data, expert consultation, original analysis, or future evidence beyond a complete desk-research answer.

## Completion Statement

Research readiness: incomplete

Writing readiness: weak

Completion statement pending. Do not claim completion until the generated gate passes.
"""


def cold_reader_template() -> str:
    return """# Cold-Reader Evaluation

VERDICT: revise

Other artifacts consulted: no

Reader education: pending. Knowledge transfer: pending. Case comprehension: pending. Tables used as recaps: pending.

## Module Results

| Module ID | What happened or how it works | Actors and stakes understood | Evidence named and explained | Dispute or limit understood | Article relevance understood | Result |
|---|---|---|---|---|---|---|

## Reader Education And Knowledge Transfer Verdict

- Can the reader accurately explain every central module without consulting another artifact? no
- Does the packet define unfamiliar people, institutions, events, laws, and mechanisms before relying on them? no
- Are tables used as recaps rather than substitutes for explanation? no
- Case comprehension failures: not yet evaluated
- Required revisions: complete the packet and run a packet-only cold-reader evaluation
"""


def initialize_project(
    project: Path,
    question: str,
    boundary: str = "",
    parent_project: str | None = None,
    assignment_type: str = "original",
) -> None:
    if project.exists() and (project / "writer-research-packet.md").exists() and not (project / "project.json").exists():
        raise ValueError("Refusing to initialize v2 over a pre-v2 project. Use migrate_v1_project.py with a new output directory.")

    project.mkdir(parents=True, exist_ok=True)
    (project / "appendices").mkdir(exist_ok=True)
    (project / "source-cache").mkdir(exist_ok=True)
    (project / "updates").mkdir(exist_ok=True)

    today = date.today().isoformat()
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("A non-empty research question is required.")
    metadata = {
        "schema_version": SCHEMA_VERSION,
        "skill_version": "2.1.0",
        "gate_version": GATE_VERSION,
        "project_id": project_id_from_path(project),
        "assignment_type": assignment_type,
        "parent_project": parent_project,
        "question": clean_question,
        "boundary": boundary.strip(),
        "created_at": today,
        "as_of": today,
        "completed_at": None,
        "status": "researching",
        "research_readiness": "incomplete",
        "writing_readiness": "weak",
    }
    work_state = {
        "source_universe_complete": False,
        "central_tasks": [],
        "unresolved_central_tasks": ["Map the assignment into load-bearing claims and required evidence."],
        "contradiction_searches": [],
        "method_audits_complete": False,
        "adversarial_review": {
            "status": "pending",
            "blocking_issues": [],
            "resolved_issues": [],
        },
        "optional_original_reporting": [],
    }

    write_json_if_missing(project / "project.json", metadata)
    write_json_if_missing(project / "work-state.json", work_state)
    write_text_if_missing(project / "writer-research-packet.md", packet_template(clean_question, today))
    write_text_if_missing(project / "cold-reader-evaluation.md", cold_reader_template())
    write_csv_if_missing(project / "claims.csv", CLAIM_HEADERS)
    write_csv_if_missing(project / "sources.csv", SOURCE_HEADERS)
    write_csv_if_missing(project / "extractions.csv", EXTRACTION_HEADERS)
    write_csv_if_missing(project / "reader-education.csv", READER_EDUCATION_HEADERS)
    write_csv_if_missing(project / "source-cache" / "manifest.csv", MANIFEST_HEADERS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="New v2 project folder, e.g. research/example-topic")
    parser.add_argument("--question", required=True, help="Research question")
    parser.add_argument("--boundary", default="", help="Optional initial research boundary")
    args = parser.parse_args()

    project = Path(args.project_dir)
    try:
        initialize_project(project, args.question, args.boundary)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"Initialized v{SCHEMA_VERSION} Evidence Audit Project: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
