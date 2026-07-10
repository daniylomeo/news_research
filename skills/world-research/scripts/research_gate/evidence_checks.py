from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

from .common import normalized, truthy, url_or_substantive_citation, valid_iso_date, words
from .schema import (
    ACCESS_DEPTH_VALUES,
    CLAIM_STATUSES,
    CONFIDENCE_VALUES,
    COUNTEREVIDENCE_VALUES,
    EXTRACTION_STATUSES,
    METHOD_DOCUMENT_TYPES,
    REPRODUCTION_DOCUMENT_TYPES,
    REPRODUCTION_VALUES,
    Finding,
)


PLACEHOLDER_RE = re.compile(r"\b(todo|tbd|generic filler|lorem ipsum|some unspecified|not yet researched|placeholder)\b", flags=re.I)
PRESTIGE_REASON_RE = re.compile(
    r"\b(credible|trusted|correct|reliable) because (?:it|they|the source) (?:is|are)\b|"
    r"\b(peer reviewed|official|reputable|prestigious) (?:therefore|so|proves|establishes)\b",
    flags=re.I,
)
SHALLOW_ACCESS = {"partial_document", "abstract_only", "snippet_only", "metadata_only", "unavailable"}


def check(project: Path, data: dict) -> list[Finding]:
    del project
    findings: list[Finding] = []
    claims = data.get("claims", [])
    sources = data.get("sources", [])
    extractions = data.get("extractions", [])
    metadata = data.get("metadata", {})
    source_by_id = {row.get("source_id", ""): row for row in sources}
    extractions_by_claim: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in extractions:
        extractions_by_claim[row.get("claim_id", "")].append(row)
    load_bearing_claim_ids = {row.get("claim_id", "") for row in claims if truthy(row.get("load_bearing"))}
    load_bearing_source_ids = {
        row.get("source_id", "") for row in extractions if row.get("claim_id", "") in load_bearing_claim_ids
    }
    load_claims_by_source: dict[str, list[dict[str, str]]] = defaultdict(list)
    claim_by_id = {row.get("claim_id", ""): row for row in claims}
    for row in extractions:
        claim = claim_by_id.get(row.get("claim_id", ""), {})
        if truthy(claim.get("load_bearing")):
            load_claims_by_source[row.get("source_id", "")].append(claim)

    for index, row in enumerate(claims, start=2):
        location = f"claims.csv row {index}"
        status = row.get("status", "").strip().lower()
        confidence = row.get("confidence", "").strip().lower()
        counter_status = row.get("counterevidence_status", "").strip().lower()
        load_bearing = truthy(row.get("load_bearing"))
        if status not in CLAIM_STATUSES:
            findings.append(Finding("FAIL", "claim_status", location, f"Invalid claim status: {status or '<blank>'}"))
        if confidence not in CONFIDENCE_VALUES:
            findings.append(Finding("FAIL", "claim_confidence", location, f"Invalid confidence: {confidence or '<blank>'}"))
        if counter_status not in COUNTEREVIDENCE_VALUES:
            findings.append(Finding("FAIL", "counterevidence_status", location, f"Invalid counterevidence_status: {counter_status or '<blank>'}"))
        if load_bearing:
            if not extractions_by_claim.get(row.get("claim_id", "")):
                findings.append(Finding("FAIL", "missing_evidence", location, "Load-bearing claim has no extraction row."))
            if metadata.get("status") == "complete" and status == "pending":
                findings.append(Finding("FAIL", "pending_claim", location, "Completed project has a pending load-bearing claim."))
            if metadata.get("status") == "complete" and counter_status == "pending":
                findings.append(Finding("FAIL", "counterevidence_pending", location, "Completed load-bearing claim lacks a completed contradiction search."))
            if row.get("claim_type", "").lower() in {"causal", "implementation", "outcome"} and counter_status == "not_applicable":
                findings.append(Finding("FAIL", "counterevidence_required", location, "Causal, implementation, and outcome claims require a contradiction search."))
            if words(row.get("confidence_basis", "")) < 12:
                findings.append(Finding("FAIL", "thin_confidence_basis", location, "Load-bearing claim needs an evidence-based confidence explanation of at least twelve words."))
            if words(row.get("what_would_change", "")) < 8:
                findings.append(Finding("FAIL", "missing_revision_condition", location, "Load-bearing claim needs a concrete revision condition."))
        if status in {"indeterminate", "unauditable"} and confidence != "indeterminate":
            findings.append(Finding("FAIL", "indeterminate_confidence", location, "Indeterminate or unauditable claims must use indeterminate confidence."))
        if PRESTIGE_REASON_RE.search(row.get("confidence_basis", "")):
            findings.append(Finding("FAIL", "prestige_reasoning", location, "Confidence relies on source status rather than audited evidence."))

    for index, row in enumerate(sources, start=2):
        location = f"sources.csv row {index}"
        access = row.get("access_depth", "").strip().lower()
        if access not in ACCESS_DEPTH_VALUES:
            findings.append(Finding("FAIL", "access_depth", location, f"Invalid access_depth: {access or '<blank>'}"))
        if not url_or_substantive_citation(row.get("url_or_citation", "")):
            findings.append(Finding("FAIL", "invalid_source_citation", location, "Source needs a valid HTTP(S) URL or a substantive formal citation."))
        central = (
            row.get("centrality", "").lower() in {"central", "load_bearing"}
            or truthy(row.get("eligible_for_claims"))
            or row.get("source_id", "") in load_bearing_source_ids
        )
        unavailable_limit = (
            access == "unavailable"
            and load_claims_by_source.get(row.get("source_id", ""))
            and all(claim.get("status", "").lower() in {"indeterminate", "unauditable"} for claim in load_claims_by_source[row.get("source_id", "")])
        )
        if central and access in SHALLOW_ACCESS and not unavailable_limit:
            findings.append(Finding("FAIL", "shallow_central_source", location, f"Central source cannot use access_depth={access}; mark the affected claim indeterminate or acquire the relevant source."))
        if central:
            if not valid_iso_date(row.get("freshness_as_of", "")):
                findings.append(Finding("FAIL", "source_freshness", location, "Central source requires freshness_as_of as an ISO date."))
            for field, minimum in (("audit_scope", 8), ("provenance", 8), ("limitations", 8)):
                if words(row.get(field, "")) < minimum:
                    findings.append(Finding("FAIL", f"thin_{field}", location, f"Central source needs a substantive {field.replace('_', ' ')}."))

    raw_counts = Counter(normalized(row.get("raw_evidence", "")) for row in extractions if row.get("raw_evidence"))
    if extractions and raw_counts and raw_counts.most_common(1)[0][1] / len(extractions) >= 0.5 and raw_counts.most_common(1)[0][1] >= 3:
        findings.append(Finding("FAIL", "repeated_evidence_filler", "extractions.csv", "At least half of extraction rows repeat identical evidence text."))

    for index, row in enumerate(extractions, start=2):
        location = f"extractions.csv row {index}"
        status = row.get("status", "").strip().lower()
        confidence = row.get("confidence", "").strip().lower()
        reproduction = row.get("reproduction_status", "").strip().lower()
        claim = next((item for item in claims if item.get("claim_id") == row.get("claim_id")), {})
        source = source_by_id.get(row.get("source_id", ""), {})
        load_bearing = truthy(claim.get("load_bearing"))
        if status not in EXTRACTION_STATUSES:
            findings.append(Finding("FAIL", "extraction_status", location, f"Invalid extraction status: {status or '<blank>'}"))
        if confidence not in CONFIDENCE_VALUES:
            findings.append(Finding("FAIL", "extraction_confidence", location, f"Invalid confidence: {confidence or '<blank>'}"))
        if reproduction not in REPRODUCTION_VALUES:
            findings.append(Finding("FAIL", "reproduction_status", location, f"Invalid reproduction_status: {reproduction or '<blank>'}"))
        joined = " ".join(str(value or "") for value in row.values())
        if PLACEHOLDER_RE.search(joined):
            findings.append(Finding("FAIL", "placeholder_evidence", location, "Extraction contains placeholder or generic filler language."))
        if load_bearing:
            if metadata.get("status") == "complete" and status == "pending":
                findings.append(Finding("FAIL", "pending_extraction", location, "Completed project has a pending load-bearing extraction."))
            if metadata.get("status") == "complete" and confidence == "pending":
                findings.append(Finding("FAIL", "pending_extraction_confidence", location, "Completed project has pending confidence for load-bearing evidence."))
            if words(row.get("proposition", "")) < 6:
                findings.append(Finding("FAIL", "thin_proposition", location, "Load-bearing extraction needs a precise proposition."))
            if words(row.get("evidence_locator", "")) < 4:
                findings.append(Finding("FAIL", "thin_locator", location, "Load-bearing extraction needs a pinpoint page, table, row, docket, timestamp, or named section."))
            if words(row.get("raw_evidence", "")) < 12:
                findings.append(Finding("FAIL", "thin_raw_evidence", location, "Load-bearing extraction needs substantive raw evidence, not a headline paraphrase."))
            for field in ("provenance_notes", "alternative_explanations", "counterevidence", "claim_fit", "what_would_change"):
                if words(row.get(field, "")) < 6:
                    findings.append(Finding("FAIL", f"thin_{field}", location, f"Load-bearing extraction needs substantive {field.replace('_', ' ')}."))
        document_type = source.get("document_type", "").strip().lower()
        if load_bearing and document_type in METHOD_DOCUMENT_TYPES:
            if words(row.get("measurement_definition", "")) < 6:
                findings.append(Finding("FAIL", "missing_measurement", location, "Method-bearing evidence needs units, denominators, categories, or an explicit non-applicability explanation."))
            if words(row.get("method_notes", "")) < 12:
                findings.append(Finding("FAIL", "thin_method_audit", location, "Method-bearing evidence needs a substantive method audit."))
            if words(row.get("missingness", "")) < 5:
                findings.append(Finding("FAIL", "missing_missingness", location, "Method-bearing evidence needs missing-data or record-completeness analysis."))
        if load_bearing and document_type in REPRODUCTION_DOCUMENT_TYPES:
            if reproduction in {"pending", "not_applicable"}:
                findings.append(Finding("FAIL", "reproduction_required", location, "Quantitative or classification evidence requires a reproduction attempt or a concrete not-possible result."))
            if words(row.get("reproduction_notes", "")) < 6:
                findings.append(Finding("FAIL", "reproduction_notes", location, "Record what was reproduced, checked, or why reproduction was not possible."))

    for claim in claims:
        if not truthy(claim.get("load_bearing")):
            continue
        if claim.get("claim_type", "").lower() not in {"causal", "implementation", "outcome"}:
            continue
        if claim.get("status", "").lower() not in {"supported", "mostly_supported"}:
            continue
        evidence_rows = extractions_by_claim.get(claim.get("claim_id", ""), [])
        supporting = [row for row in evidence_rows if row.get("status", "").lower() == "supports"]
        source_types = {source_by_id.get(row.get("source_id", ""), {}).get("document_type", "").lower() for row in supporting}
        if supporting and source_types == {"press_release"}:
            findings.append(Finding("FAIL", "press_release_implementation", f"claim {claim.get('claim_id', '')}", "A press release alone can establish an announcement or position, not implementation, outcome, or causation."))

    return findings
