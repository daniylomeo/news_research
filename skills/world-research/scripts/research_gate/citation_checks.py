from __future__ import annotations

from pathlib import Path

from .common import find_refs, truthy
from .schema import Finding


def check(project: Path, data: dict) -> list[Finding]:
    findings: list[Finding] = []
    packet = data.get("packet_text", "")
    claim_ids = {row.get("claim_id", "") for row in data.get("claims", [])}
    source_ids = {row.get("source_id", "") for row in data.get("sources", [])}
    packet_claims = find_refs(packet, "C")
    packet_sources = find_refs(packet, "S")

    for claim_id in sorted(packet_claims - claim_ids):
        findings.append(Finding("FAIL", "unknown_packet_claim", "writer-research-packet.md", f"Packet cites unknown claim: {claim_id}"))
    for source_id in sorted(packet_sources - source_ids):
        findings.append(Finding("FAIL", "unknown_packet_source", "writer-research-packet.md", f"Packet cites unknown source: {source_id}"))
    for row in data.get("claims", []):
        if truthy(row.get("load_bearing")) and row.get("claim_id", "") not in packet_claims:
            findings.append(Finding("FAIL", "uncited_load_bearing_claim", "writer-research-packet.md", f"Load-bearing claim is not explained in the packet: {row.get('claim_id', '')}"))
    if data.get("claims") and not packet_claims:
        findings.append(Finding("FAIL", "no_claim_citations", "writer-research-packet.md", "Packet cites no claim IDs."))
    if data.get("sources") and not packet_sources:
        findings.append(Finding("FAIL", "no_source_citations", "writer-research-packet.md", "Packet cites no source IDs."))
    return findings
