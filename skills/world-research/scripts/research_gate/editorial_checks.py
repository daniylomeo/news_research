from __future__ import annotations

import re
from pathlib import Path

from .common import find_refs, section_body, truthy, words
from .schema import METHOD_DOCUMENT_TYPES, Finding


USER_FACING_DEFERRAL_RE = re.compile(
    r"\b(another|second|future) Codex (?:research )?pass (?:is|will be|would be) (?:needed|required)\b|"
    r"\bask (?:me|Codex) (?:for|to do) another pass\b|"
    r"\breturn for another research pass\b",
    flags=re.I,
)


def check(project: Path, data: dict) -> list[Finding]:
    del project
    findings: list[Finding] = []
    packet = data.get("packet_text", "")
    if not packet:
        return findings

    bottom = section_body(packet, "Bottom Line")
    if bottom and (not find_refs(bottom, "C") or not find_refs(bottom, "S")):
        findings.append(Finding("FAIL", "bottom_line_anchors", "Bottom Line", "Bottom Line must cite audited claim and source IDs."))

    evidence = section_body(packet, "Evidence By Claim")
    evidence_claims = find_refs(evidence, "C")
    for row in data.get("claims", []):
        if truthy(row.get("load_bearing")) and row.get("claim_id", "") not in evidence_claims:
            findings.append(Finding("FAIL", "claim_not_explained", "Evidence By Claim", f"Load-bearing claim lacks a reader-facing explanation: {row.get('claim_id', '')}"))

    method_source_ids = set()
    claim_by_id = {row.get("claim_id", ""): row for row in data.get("claims", [])}
    source_by_id = {row.get("source_id", ""): row for row in data.get("sources", [])}
    for extraction in data.get("extractions", []):
        claim = claim_by_id.get(extraction.get("claim_id", ""), {})
        source = source_by_id.get(extraction.get("source_id", ""), {})
        if truthy(claim.get("load_bearing")) and source.get("document_type", "").lower() in METHOD_DOCUMENT_TYPES:
            method_source_ids.add(extraction.get("source_id", ""))
    method_body = section_body(packet, "Method And Data Audits")
    method_refs = find_refs(method_body, "S")
    for source_id in sorted(method_source_ids - method_refs):
        findings.append(Finding("FAIL", "method_not_explained", "Method And Data Audits", f"Method-bearing load-bearing source lacks a reader-facing audit: {source_id}"))

    contradictions = section_body(packet, "Contradictions And Competing Explanations")
    if contradictions and words(contradictions) < 35:
        findings.append(Finding("WARN", "thin_contradiction_narrative", "Contradictions And Competing Explanations", "Contradiction narrative is unusually thin."))
    if USER_FACING_DEFERRAL_RE.search(packet):
        findings.append(Finding("FAIL", "user_facing_deferral", "writer-research-packet.md", "Packet asks the user for another Codex research pass instead of completing available research internally."))

    article = section_body(packet, "Article Directions")
    if article and not re.search(r"\b(ready|promising|unsupported|not ready|explanatory)\b", article, flags=re.I):
        findings.append(Finding("WARN", "angle_readiness", "Article Directions", "Article directions should state readiness rather than only suggest topics."))
    return findings
