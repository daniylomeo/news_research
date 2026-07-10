#!/usr/bin/env python3
"""Migrate a pre-v2 project into a review-required v2 copy."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from init_evidence_audit import initialize_project
from research_gate.common import safe_project_path
from research_gate.schema import CLAIM_HEADERS, EXTRACTION_HEADERS, MANIFEST_HEADERS, SOURCE_HEADERS


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, headers: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def infer_document_type(value: str) -> str:
    lower = (value or "").lower()
    for pattern, document_type in (
        (r"court|opinion", "court_opinion"),
        (r"filing|sec", "financial_filing"),
        (r"dataset|data", "dataset"),
        (r"peer|study|academic|journal|paper", "scientific_study"),
        (r"press|release|announcement", "press_release"),
        (r"government|official|agency", "government_report"),
        (r"transcript", "transcript"),
        (r"advocacy|ngo|nonprofit|think", "advocacy_report"),
        (r"industry|trade", "industry_report"),
        (r"media|reporting|journalism", "journalism"),
    ):
        if re.search(pattern, lower):
            return document_type
    return "other"


def map_access(value: str) -> str:
    return {
        "full_document": "full_document",
        "partial_document": "partial_document",
        "dataset_inspected": "dataset_inspected",
        "filing_inspected": "filing_inspected",
        "docket_inspected": "docket_inspected",
        "transcript_inspected": "transcript_inspected",
        "secondary_summary": "partial_document",
        "snippet_only": "snippet_only",
        "not_applicable": "metadata_only",
    }.get((value or "").lower(), "partial_document")


def question_from_packet(text: str) -> str:
    match = re.search(r"^Question:\s*(.+)$", text, flags=re.I | re.M)
    return match.group(1).strip() if match else "Migrated v1 research assignment"


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_project", help="Pre-v2 project to preserve and read")
    parser.add_argument("output_project", help="New v2 migration copy; must not already contain a project")
    args = parser.parse_args()

    source = Path(args.source_project)
    output = Path(args.output_project)
    if not source.is_dir():
        parser.error("source_project does not exist")
    if (source / "project.json").exists():
        parser.error("source_project already appears to be v2")
    if output.exists() and any(output.iterdir()):
        parser.error("output_project must be absent or empty")

    legacy_packet_path = source / "writer-research-packet.md"
    legacy_packet = legacy_packet_path.read_text(encoding="utf-8", errors="replace") if legacy_packet_path.exists() else ""
    question = question_from_packet(legacy_packet)
    initialize_project(output, question, boundary="Migration copy; every v1 completion judgment requires v2 review.")

    old_sources = read_csv(source / "sources.csv")
    old_extractions = read_csv(source / "extractions.csv")
    old_manifest = read_csv(source / "source-cache" / "manifest.csv")
    old_source_by_id = {row.get("source_id", ""): row for row in old_sources}

    sources: list[dict[str, str]] = []
    for old in old_sources:
        centrality = old.get("centrality", "context").lower().replace("-", "_")
        if centrality in {"load bearing", "load_bearing"}:
            centrality = "load_bearing"
        elif centrality not in {"central", "load_bearing", "important", "context", "lead"}:
            centrality = "context"
        sources.append({
            "source_id": old.get("source_id", ""),
            "title": old.get("title", ""),
            "author_or_org": old.get("author_or_org", ""),
            "date": old.get("date", ""),
            "url_or_citation": old.get("url_or_citation", ""),
            "document_type": infer_document_type(old.get("source_type", "")),
            "source_role": "load_bearing" if centrality in {"central", "load_bearing"} else "context",
            "access_depth": map_access(old.get("source_access", "")),
            "audit_scope": old.get("claims_made", "") or "Migrated v1 scope requires claim-specific review before completion.",
            "provenance": f"Migrated from v1 source inventory attributed to {old.get('author_or_org', '') or 'the listed producer'}; provenance requires review.",
            "underlying_data_access": old.get("data_access", ""),
            "method_transparency": "Migrated v1 method field requires review against the underlying evidence.",
            "reproducibility": "pending_v2_review",
            "incentives_funding": old.get("funding_ownership_incentives", ""),
            "limitations": old.get("evidence_limit", "") or old.get("notes", "") or "Migrated v1 limitations require a claim-specific v2 audit.",
            "freshness_as_of": date.today().isoformat(),
            "centrality": centrality,
            "eligible_for_claims": old.get("eligible_for_central_evidence", "no"),
            "notes": "Migrated without certifying the previous audit state.",
        })

    status_map = {
        "supports": "supported",
        "weakens": "weakened",
        "mixed": "mixed",
        "fails": "contradicted",
        "inconclusive": "indeterminate",
        "unauditable": "unauditable",
        "incomplete": "pending",
        "context": "context",
    }
    claims_by_id: dict[str, dict[str, str]] = {}
    extractions: list[dict[str, str]] = []
    for number, old in enumerate(old_extractions, start=1):
        claim_id = old.get("claim_id", "")
        source_meta = old_source_by_id.get(old.get("source_id", ""), {})
        central = source_meta.get("centrality", "").lower() in {"central", "load-bearing", "load bearing"} or source_meta.get("eligible_for_central_evidence", "").lower() in {"yes", "true", "1"}
        old_status = old.get("status", "").lower()
        claims_by_id.setdefault(claim_id, {
            "claim_id": claim_id,
            "claim_text": old.get("exact_claim", ""),
            "claim_type": "factual",
            "load_bearing": "yes" if central else "no",
            "evidence_needed": "Review migrated v1 evidence against the v2 claim-level standard.",
            "status": status_map.get(old_status, "pending"),
            "confidence": old.get("confidence", "pending") if old.get("confidence", "").lower() in {"high", "moderate", "low", "indeterminate"} else "pending",
            "confidence_basis": " ".join(filter(None, [old.get("method_notes", ""), old.get("our_critique", "")])),
            "counterevidence_status": "pending",
            "what_would_change": old.get("follow_up_needed", "") or "Complete the v2 contradiction and method audit for this migrated claim.",
            "notes": "Migrated status is provisional until v2 review.",
        })
        extractions.append({
            "evidence_id": f"E{number}",
            "claim_id": claim_id,
            "source_id": old.get("source_id", ""),
            "proposition": old.get("exact_claim", ""),
            "evidence_locator": old.get("evidence_location", ""),
            "raw_evidence": old.get("extracted_data_or_quote", ""),
            "provenance_notes": "Migrated from v1; verify provenance against the underlying source.",
            "measurement_definition": old.get("assumptions_or_exclusions", ""),
            "method_notes": old.get("method_notes", ""),
            "reproduction_status": "pending",
            "reproduction_notes": "Migrated evidence has not received a v2 reproduction check.",
            "assumptions_or_exclusions": old.get("assumptions_or_exclusions", ""),
            "missingness": old.get("uncertainty_or_error", ""),
            "alternative_explanations": "Migration requires an explicit alternative-explanation audit.",
            "counterevidence": "Migration requires a completed contradiction search.",
            "claim_fit": old.get("our_critique", ""),
            "status": old_status if old_status in {"supports", "weakens", "mixed", "context", "unauditable", "pending"} else "pending",
            "confidence": old.get("confidence", "pending") if old.get("confidence", "").lower() in {"high", "moderate", "low", "indeterminate"} else "pending",
            "what_would_change": old.get("follow_up_needed", "") or "Complete the v2 method and contradiction audit.",
        })

    manifest: list[dict[str, str]] = []
    for old in old_manifest:
        old_reference = old.get("path_or_url", "") or old.get("cached_path_or_url", "")
        candidate = safe_project_path(source, old_reference) if old_reference and not re.match(r"https?://", old_reference, flags=re.I) else None
        if candidate and candidate.is_file():
            state = "local"
            local_path = f"source-cache/{old.get('source_id', 'source')}-{candidate.name}"
            target = output / local_path
            target.write_bytes(candidate.read_bytes())
            digest = hash_file(target)
            reason = ""
        else:
            state = "url_only" if re.match(r"https?://", old_reference, flags=re.I) else "metadata_only"
            local_path = ""
            digest = ""
            reason = "Legacy manifest preserved a URL or metadata but no verifiable local source bytes."
        manifest.append({
            "source_id": old.get("source_id", ""),
            "original_url": old_reference if re.match(r"https?://", old_reference, flags=re.I) else "",
            "capture_state": state,
            "local_path": local_path,
            "archive_url": "",
            "captured_at": old.get("access_date", "") if state == "local" else "",
            "sha256": digest,
            "mime_type": "application/octet-stream" if state == "local" else "",
            "reason_not_captured": reason,
            "copyright_notes": old.get("copyright_limitations", ""),
        })

    write_csv(output / "sources.csv", SOURCE_HEADERS, sources)
    write_csv(output / "claims.csv", CLAIM_HEADERS, list(claims_by_id.values()))
    write_csv(output / "extractions.csv", EXTRACTION_HEADERS, extractions)
    write_csv(output / "source-cache" / "manifest.csv", MANIFEST_HEADERS, manifest)

    if legacy_packet:
        (output / "appendices" / "legacy-writer-research-packet.md").write_text(legacy_packet, encoding="utf-8", newline="\n")
    metadata = json.loads((output / "project.json").read_text(encoding="utf-8"))
    metadata["status"] = "migrating"
    metadata["migration_source"] = str(source.resolve())
    (output / "project.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8", newline="\n")
    work = json.loads((output / "work-state.json").read_text(encoding="utf-8"))
    work["unresolved_central_tasks"] = [
        "Review migrated claim centrality and claim wording.",
        "Reacquire shallow central sources and verify source provenance.",
        "Complete reproduction, missingness, alternative-explanation, and contradiction audits.",
        "Rewrite the v2 packet from audited evidence rather than copying the legacy synthesis.",
    ]
    (output / "work-state.json").write_text(json.dumps(work, indent=2) + "\n", encoding="utf-8", newline="\n")
    report = {
        "source_project": str(source.resolve()),
        "output_project": str(output.resolve()),
        "sources_migrated": len(sources),
        "claims_migrated": len(claims_by_id),
        "extractions_migrated": len(extractions),
        "automatic_completion_certified": False,
        "next_step": "Run the v2 gate and resolve every finding in the copied project.",
    }
    (output / "migration-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Migrated v1 project into review-required v2 copy: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
