from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from .common import headings, read_csv, read_json, truthy, valid_iso_date, words
from .schema import (
    CLAIM_HEADERS,
    EXTRACTION_HEADERS,
    MANIFEST_HEADERS,
    OPTIONAL_REPORTING_TYPES,
    REQUIRED_FILES,
    REQUIRED_PACKET_SECTIONS,
    SCHEMA_VERSION,
    SOURCE_HEADERS,
    Finding,
)


def _headers(path: Path, required: tuple[str, ...], findings: list[Finding]) -> list[dict[str, str]]:
    header, rows = read_csv(path)
    if path.exists() and not header:
        findings.append(Finding("FAIL", "csv_unreadable", path.name, "CSV is empty, malformed, or missing a header row."))
        return []
    missing = sorted(set(required) - set(header))
    if missing:
        findings.append(Finding("FAIL", "csv_columns", path.name, f"Missing columns: {', '.join(missing)}"))
    return rows


def _unique_ids(rows: list[dict[str, str]], field: str, pattern: str, location: str, findings: list[Finding]) -> None:
    values = [row.get(field, "").strip() for row in rows]
    for index, value in enumerate(values, start=2):
        if not re.fullmatch(pattern, value):
            findings.append(Finding("FAIL", "invalid_id", f"{location} row {index}", f"Invalid {field}: {value or '<blank>'}"))
    for value, count in Counter(values).items():
        if value and count > 1:
            findings.append(Finding("FAIL", "duplicate_id", location, f"Duplicate {field}: {value}"))


def check(project: Path) -> tuple[list[Finding], dict]:
    findings: list[Finding] = []
    for relative in REQUIRED_FILES:
        target = project / relative
        if not target.exists():
            findings.append(Finding("FAIL", "missing_file", "project", f"Missing required artifact: {relative}"))

    metadata = read_json(project / "project.json")
    work_state = read_json(project / "work-state.json")
    if (project / "project.json").exists() and not metadata:
        findings.append(Finding("FAIL", "invalid_json", "project.json", "File is not a valid JSON object."))
    if (project / "work-state.json").exists() and not work_state:
        findings.append(Finding("FAIL", "invalid_json", "work-state.json", "File is not a valid JSON object."))

    if metadata and metadata.get("schema_version") != SCHEMA_VERSION:
        findings.append(Finding("FAIL", "schema_version", "project.json", f"Expected schema_version {SCHEMA_VERSION}; use the migration tool for v1 projects."))
    if metadata and not str(metadata.get("question", "")).strip():
        findings.append(Finding("FAIL", "missing_question", "project.json", "Question is required."))
    for field in ("created_at", "as_of"):
        if metadata and not valid_iso_date(str(metadata.get(field, ""))):
            findings.append(Finding("FAIL", "project_date", "project.json", f"{field} must be an ISO date."))
    if metadata and metadata.get("status") not in {"researching", "migrating", "complete"}:
        findings.append(Finding("FAIL", "project_status", "project.json", "status must be researching, migrating, or complete."))
    if metadata and metadata.get("status") != "complete":
        findings.append(Finding("FAIL", "project_not_complete", "project.json", "The final quality gate passes only completed projects; continue the current research task."))
    if metadata.get("status") == "complete" and words(str(metadata.get("boundary", ""))) < 8:
        findings.append(Finding("FAIL", "missing_boundary", "project.json", "A completed project needs a substantive boundary."))

    claim_rows = _headers(project / "claims.csv", CLAIM_HEADERS, findings)
    source_rows = _headers(project / "sources.csv", SOURCE_HEADERS, findings)
    extraction_rows = _headers(project / "extractions.csv", EXTRACTION_HEADERS, findings)
    manifest_rows = _headers(project / "source-cache" / "manifest.csv", MANIFEST_HEADERS, findings)

    if not claim_rows:
        findings.append(Finding("FAIL", "no_claims", "claims.csv", "Project has no claim rows."))
    if not source_rows:
        findings.append(Finding("FAIL", "no_sources", "sources.csv", "Project has no source rows."))
    if not extraction_rows:
        findings.append(Finding("FAIL", "no_extractions", "extractions.csv", "Project has no extraction rows."))

    _unique_ids(claim_rows, "claim_id", r"C\d+", "claims.csv", findings)
    _unique_ids(source_rows, "source_id", r"S\d+", "sources.csv", findings)
    _unique_ids(extraction_rows, "evidence_id", r"E\d+", "extractions.csv", findings)

    claim_ids = {row.get("claim_id", "") for row in claim_rows}
    source_ids = {row.get("source_id", "") for row in source_rows}
    manifest_ids = {row.get("source_id", "") for row in manifest_rows}
    load_bearing_claim_ids = {row.get("claim_id", "") for row in claim_rows if truthy(row.get("load_bearing"))}
    load_bearing_source_ids = {
        row.get("source_id", "") for row in extraction_rows if row.get("claim_id", "") in load_bearing_claim_ids
    }
    for index, row in enumerate(extraction_rows, start=2):
        if row.get("claim_id", "") not in claim_ids:
            findings.append(Finding("FAIL", "orphan_claim", f"extractions.csv row {index}", f"Unknown claim_id: {row.get('claim_id', '')}"))
        if row.get("source_id", "") not in source_ids:
            findings.append(Finding("FAIL", "orphan_source", f"extractions.csv row {index}", f"Unknown source_id: {row.get('source_id', '')}"))
    for index, row in enumerate(manifest_rows, start=2):
        if row.get("source_id", "") not in source_ids:
            findings.append(Finding("FAIL", "orphan_manifest", f"manifest.csv row {index}", f"Unknown source_id: {row.get('source_id', '')}"))
    for row in source_rows:
        central = (
            row.get("centrality", "").lower() in {"central", "load_bearing"}
            or truthy(row.get("eligible_for_claims"))
            or row.get("source_id", "") in load_bearing_source_ids
        )
        if central and row.get("source_id", "") not in manifest_ids:
            findings.append(Finding("FAIL", "missing_manifest", "source-cache/manifest.csv", f"Central source lacks preservation record: {row.get('source_id', '')}"))

    packet_path = project / "writer-research-packet.md"
    packet_text = packet_path.read_text(encoding="utf-8", errors="replace") if packet_path.exists() else ""
    packet_headings = headings(packet_text)
    for section in REQUIRED_PACKET_SECTIONS:
        if section.lower() not in packet_headings:
            findings.append(Finding("FAIL", "packet_section", packet_path.name, f"Missing required section: {section}"))
    if packet_text and words(packet_text) < 700:
        findings.append(Finding("WARN", "packet_length", packet_path.name, "Packet is unusually short; confirm it explains the evidence rather than only listing verdicts."))

    if metadata.get("status") == "complete":
        if not valid_iso_date(str(metadata.get("completed_at", ""))):
            findings.append(Finding("FAIL", "completion_date", "project.json", "Completed project requires completed_at as an ISO date."))
        if metadata.get("research_readiness") not in {"usable", "strong"}:
            findings.append(Finding("FAIL", "research_readiness", "project.json", "Completed project requires research_readiness usable or strong."))
        if metadata.get("writing_readiness") not in {"weak", "explanatory_only", "promising", "ready"}:
            findings.append(Finding("FAIL", "writing_readiness", "project.json", "Completed project has an invalid writing_readiness."))
        if work_state.get("source_universe_complete") is not True:
            findings.append(Finding("FAIL", "source_universe", "work-state.json", "Completed project must mark source_universe_complete true."))
        unresolved = work_state.get("unresolved_central_tasks", [])
        if not isinstance(unresolved, list) or unresolved:
            findings.append(Finding("FAIL", "unresolved_tasks", "work-state.json", "Completed project has unresolved central tasks."))
        if work_state.get("method_audits_complete") is not True:
            findings.append(Finding("FAIL", "method_audits", "work-state.json", "Completed project must mark method_audits_complete true."))
        adversarial = work_state.get("adversarial_review", {})
        if not isinstance(adversarial, dict) or adversarial.get("status") != "pass":
            findings.append(Finding("FAIL", "adversarial_review", "work-state.json", "Completed project requires adversarial_review.status=pass."))
        if isinstance(adversarial, dict) and adversarial.get("blocking_issues"):
            findings.append(Finding("FAIL", "adversarial_blockers", "work-state.json", "Adversarial review still lists blocking issues."))
        completion_sentence = "No further Codex research pass is required for the stated boundary."
        if completion_sentence.lower() not in packet_text.lower():
            findings.append(Finding("FAIL", "completion_sentence", packet_path.name, f"Completion Statement must include: {completion_sentence}"))
        if not re.search(r"\bresearch readiness:\s*(usable|strong)\b", packet_text, flags=re.I):
            findings.append(Finding("FAIL", "packet_research_readiness", packet_path.name, "Completed packet must report research readiness usable or strong."))
        if not re.search(r"\bwriting readiness:\s*(weak|explanatory[-_ ]only|promising|ready)\b", packet_text, flags=re.I):
            findings.append(Finding("FAIL", "packet_writing_readiness", packet_path.name, "Completed packet must report a valid writing readiness."))
        if re.search(r"\bcompletion statement pending\b", packet_text, flags=re.I):
            findings.append(Finding("FAIL", "pending_completion_statement", packet_path.name, "Completed packet still contains the initializer's pending completion statement."))

    optional = work_state.get("optional_original_reporting", [])
    if optional and not isinstance(optional, list):
        findings.append(Finding("FAIL", "optional_reporting_shape", "work-state.json", "optional_original_reporting must be a list."))
    elif isinstance(optional, list):
        for index, item in enumerate(optional, start=1):
            if not isinstance(item, dict):
                findings.append(Finding("FAIL", "optional_reporting_shape", f"work-state.json item {index}", "Optional reporting entry must be an object."))
                continue
            if item.get("type") not in OPTIONAL_REPORTING_TYPES:
                findings.append(Finding("FAIL", "optional_reporting_type", f"work-state.json item {index}", "Optional reporting is limited to work beyond completed desk research."))
            if item.get("beyond_desk_research") is not True:
                findings.append(Finding("FAIL", "deferred_desk_research", f"work-state.json item {index}", "Optional reporting entry must explicitly be beyond ordinary desk research."))

    data = {
        "metadata": metadata,
        "work_state": work_state,
        "packet_text": packet_text,
        "claims": claim_rows,
        "sources": source_rows,
        "extractions": extraction_rows,
        "manifest": manifest_rows,
    }
    return findings, data
