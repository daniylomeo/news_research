#!/usr/bin/env python3
"""Heuristic quality gate for world-research Evidence Audit Projects.

This is not a substitute for judgment. It catches common failure modes:
summary filler, generic viewpoint maps, weak aggregators, unsupported rubrics,
and deferred central work.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


HARD_PATTERNS = [
    (r"\bneeds deeper review\b", "central work appears deferred"),
    (r"\bdeeper (second )?pass\b", "core research may be deferred to a later pass"),
    (r"\bfuture work\b", "possible deferred central work"),
    (r"\bnot covered in full\b", "boundary may be too broad for the conclusion"),
    (r"\bfirst-pass\b", "project labels itself a first pass; complete central work or narrow the boundary"),
    (r"\bnot a full\b", "project disclaims full central coverage"),
    (r"\bdoes not estimate\b", "project may be skipping central quantification"),
    (r"\bsource example:\b", "source may be illustrative rather than authoritative"),
]

WEAK_SOURCE_PATTERNS = [
    (r"worldometers\.info", "Worldometer is an aggregator; prefer official World Bank/IMF/OECD data"),
    (r"truth-and-beauty\.net", "third-party OECD visualization; prefer official OECD data"),
    (r"wikipedia\.org", "Wikipedia is useful for orientation, not central evidence"),
    (r"statista\.com", "Statista is an aggregator; prefer underlying data"),
]

SNIPPET_EVIDENCE_PATTERNS = [
    (r"\bsearch result(?:/open)? snippet\b", "central evidence appears to rely on a search-result snippet"),
    (r"\bopen snippet\b", "central evidence appears to rely on a source preview rather than an inspected document"),
    (r"\bgoogle snippet\b", "central evidence appears to rely on a search-result snippet"),
    (r"\bpreview snippet\b", "central evidence appears to rely on a preview rather than an inspected document"),
    (r"\bheadline only\b", "central evidence appears to rely on a headline rather than inspected evidence"),
]

GENERIC_VIEWPOINT_PATTERNS = [
    (r"representative sources/voices:\s*(market-oriented economists|business press|many|some|critics|supporters|opponents)", "generic representatives in viewpoint map"),
    (r"representative voices:\s*(social-democratic parties|labor unions|many|some|critics|supporters|opponents)", "generic representatives in viewpoint map"),
    (r"actual argument:\s*\n\n(the|this) ", "viewpoint may not be anchored to named actors"),
]

VAGUE_FUNDER_PATTERNS = [
    (r"funded by voluntary donations from individuals, foundations,? and companies", "vague funder summary; list named disclosed funders or flag donor opacity"),
    (r"funded by individuals, foundations,? and companies", "vague funder summary; list named disclosed funders or flag donor opacity"),
    (r"receives? (?:funding|donations) from individuals, foundations,? and companies", "vague funder summary; list named disclosed funders or flag donor opacity"),
]

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Research Boundary",
    "Explainer",
    "Source Cards",
    "Study",
    "Viewpoint",
    "Claim Ledger",
    "Audit Trail",
    "Adversarial Self-Review",
    "Quality Gate",
]

LINK_REQUIRED_SECTIONS = [
    "Source Cards",
    "Study and Data Readouts",
    "Case or Project Audits",
    "Case and Project Audit",
    "Case or Project Audit",
    "Policy Options",
    "Viewpoint and Commentary Map",
    "Claim Ledger",
    "Audit Trail",
]

SOURCE_CARD_REQUIRED_FIELDS = [
    "URL:",
    "Type:",
    "Use:",
    "Read/inspected:",
    "Method appraisal:",
    "Source weight:",
    "Limits:",
]

SOURCE_CARD_METHOD_FIELD_PATTERNS = [
    (r"\b(Evidence/method|Methodology and data|Method/data|Data and method):", "methodology/data field"),
    (r"\b(Findings readout|Finding readout|Findings|Results):", "findings/results field"),
]

VAGUE_READ_PATTERNS = [
    (r"Read/inspected:\s*(?:Abstract|Summary|Headline|Key findings|Central claims|Public summary|Landing page)\b", "source inspection is too shallow for a central source"),
    (r"Read/inspected:[^\n]*(?:abstract and summary|summary readouts|headline results|central claims|method overview)", "source inspection appears to rely on summaries/abstracts rather than the full source"),
]

CAUSAL_LANGUAGE_RE = re.compile(
    r"\b(cause[sd]?|causal|because|driven by|driver|led to|leads to|made\b|makes\b|"
    r"explains?|converted|created|validated|amplified|fueled|produced|resulted in|"
    r"responsible for|shifted|increased|decreased)\b",
    flags=re.IGNORECASE,
)

CAUSAL_SECTION_TERMS = (
    "cause",
    "causal",
    "why",
    "driver",
    "drivers",
    "mechanism",
    "mechanisms",
    "radicalization",
)

ADVOCACY_SOURCE_TERMS = [
    "advocacy",
    "think tank",
    "industry association",
    "coalition",
    "nonprofit",
    "ngo",
    "trade association",
    "consumer advocacy",
    "environmental",
]

PROJECT_REQUIRED_FILES = [
    "protocol.md",
    "coverage-ledger.csv",
    "claim-map.md",
    "source-intake.csv",
    "evidence-extraction.csv",
    "audit-trail.md",
    "adversarial-evaluation.md",
    "final-synthesis.md",
]

PROJECT_RECOMMENDED_FILES = [
    "lens-review.md",
    "sensitivity-tests.md",
]

CLAIM_REQUIRED_COLUMNS = {
    "claim_id",
    "claim_text",
    "claim_type",
    "load_bearing",
    "evidence_needed",
    "status",
    "confidence",
}

SOURCE_REQUIRED_COLUMNS = {
    "source_id",
    "title",
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
}

EXTRACTION_REQUIRED_COLUMNS = {
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
}

COVERAGE_REQUIRED_COLUMNS = {
    "question_part_id",
    "user_question_part",
    "central",
    "required_primary_sources",
    "required_artifact",
    "artifact_path",
    "status",
    "blocking_gap",
    "completion_evidence",
}

PRESTIGE_FIRST_PATTERNS = [
    (r"\bcredible because (?:it is|they are)\b", "source appears judged by reputation before evidence"),
    (r"\btrusted because (?:it is|they are)\b", "source appears judged by reputation before evidence"),
    (r"\breputable (?:source|institution|journal|think tank) (?:therefore|so)\b", "prestige is being used as evidence"),
    (r"\bfringe source,? so\b", "outsider status is being used as a shortcut against evidence"),
    (r"\bconspiracy source,? so\b", "conspiratorial label is being used as a shortcut against evidence"),
]

LEGAL_TOPIC_RE = re.compile(
    r"\b(court|supreme court|scotus|case|ruling|opinion|dissent|majority|standing|trial|oral argument|briefs?)\b",
    flags=re.IGNORECASE,
)

ARGUMENT_TOPIC_RE = re.compile(r"\b(arguments?|briefs?|oral argument|transcript)\b", flags=re.IGNORECASE)
TRIAL_TOPIC_RE = re.compile(r"\b(trial|witness(?:es)?|exhibits?|testimony|record)\b", flags=re.IGNORECASE)
STANDING_TOPIC_RE = re.compile(r"\bstanding\b", flags=re.IGNORECASE)
DOCTRINE_TOPIC_RE = re.compile(r"\b(doctrine|holding|majority|dissent|test|dicta|precedent|statutory interpretation)\b", flags=re.IGNORECASE)
QUANT_TOPIC_RE = re.compile(
    r"\b(methodolog(?:y|ical)|estimate|model|projection|forecast|seats?|districts?|maps?|quantitative|statistic|rate|percent|data)\b",
    flags=re.IGNORECASE,
)
PREDICTION_WORD_RE = re.compile(r"\b(likely|could|may|might|valid|actual effect|plausible|forecast|projection|estimate)\b", flags=re.IGNORECASE)

ECONOMIC_TOPIC_RE = re.compile(
    r"\b(economic|economics|cost benefit|cost-benefit|benefit|harms?|jobs?|tax|subsid(?:y|ies)|"
    r"ratepayer|inflation|wages?|productivity|market|industrial policy|externalit(?:y|ies)|"
    r"public investment|regulation|data centers?|ai infrastructure)\b",
    flags=re.IGNORECASE,
)

ECONOMIC_LENS_TERMS = [
    "austrian",
    "chicago",
    "neoclassical",
    "keynesian",
    "mmt",
    "public choice",
    "marx",
    "labor",
    "institutionalist",
]

ECONOMIC_REPRESENTATIVE_STATUS_ALLOWED = {
    "current_issue_specific",
    "current_adjacent",
    "canonical_background",
    "institutional_current",
    "non_economist_commentary",
    "not_applicable",
}

ECONOMIC_ISSUE_SPECIFICITY_ALLOWED = {
    "direct_this_issue",
    "direct_same_policy_area",
    "general_theory",
    "not_applicable",
}

SOURCE_ACCESS_ALLOWED = {
    "full_document",
    "partial_document",
    "dataset_inspected",
    "filing_inspected",
    "docket_inspected",
    "transcript_inspected",
    "secondary_summary",
    "snippet_only",
    "not_applicable",
}

EVALUATOR_REQUIRED_TERMS = [
    "blocking issues",
    "unsupported load-bearing claims",
    "evidence integrity",
    "causal inference",
    "quantitative",
    "viewpoint",
    "ideological bias",
    "left",
    "institutional bias",
    "reverse bias",
    "final evaluator decision",
]

UNIFIED_PROJECT_REQUIRED_FILES = [
    "research-brief.md",
    "sources.csv",
    "extractions.csv",
    "source-cache/manifest.csv",
    "adversarial-evaluation.md",
]

UNIFIED_BRIEF_REQUIRED_SECTIONS = [
    "Question And Boundary",
    "Bottom Line",
    "Timeline",
    "Claim Map",
    "Causal Model",
    "Source And Evidence Audit",
    "Bias And Symmetry Check",
    "Adversarial Evaluation",
    "Quality Gate Result",
    "Expert Evaluator Result",
]

CACHE_MANIFEST_REQUIRED_COLUMNS = {
    "source_id",
    "path_or_url",
    "cached_status",
    "cache_reason",
    "access_date",
    "centrality",
    "copyright_limitations",
}

CACHE_STATUS_ALLOWED = {
    "cached",
    "metadata_only",
    "not_cacheable",
    "not_available",
}

METADATA_ONLY_ALLOWED_REASON_RE = re.compile(
    r"\b(copyright|paywall|login|blocked|robots|dynamic|not cacheable|cannot cache|license|private|restricted)\b",
    flags=re.IGNORECASE,
)

UNSTABLE_LOCATION_RE = re.compile(r"\blines?\s+\d+", flags=re.IGNORECASE)

EXPERT_EVALUATOR_REQUIRED_TERMS = [
    "evidence integrity",
    "causal inference",
    "source preservation",
    "counterargument handling",
    "economic-perspective depth",
    "ideological symmetry",
    "reader coherence",
    "final-answer usefulness",
]


def headings(text: str) -> list[tuple[int, str, int]]:
    out: list[tuple[int, str, int]] = []
    for match in re.finditer(r"^(#{1,4})\s+(.+?)\s*$", text, flags=re.MULTILINE):
        out.append((len(match.group(1)), match.group(2).strip(), match.start()))
    return out


def section_bodies(text: str) -> list[tuple[str, str]]:
    hs = headings(text)
    bodies: list[tuple[str, str]] = []
    for idx, (_, title, start) in enumerate(hs):
        body_start = text.find("\n", start)
        body_end = hs[idx + 1][2] if idx + 1 < len(hs) else len(text)
        bodies.append((title, text[body_start:body_end]))
    return bodies


def count_links(body: str) -> int:
    return len(re.findall(r"https?://|\]\(", body))


def bullet_lines(body: str) -> int:
    return len(re.findall(r"^\s*[-*]\s+", body, flags=re.MULTILINE))


def prose_words(body: str) -> int:
    cleaned = re.sub(r"https?://\S+", "", body)
    return len(re.findall(r"[A-Za-z][A-Za-z'-]+", cleaned))


def split_subsections(body: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^###\s+(.+?)\s*$", body, flags=re.MULTILINE))
    out: list[tuple[str, str]] = []
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        out.append((match.group(1).strip(), body[start:end]))
    return out


def lens_slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()
    aliases = {
        "free market": "austrian",
        "market process": "austrian",
        "consumer welfare": "chicago",
        "industrial organization": "chicago",
        "neoclassical": "chicago",
        "mmt": "mmt",
        "modern monetary theory": "mmt",
        "labor": "labor",
        "marxian": "labor",
        "marxist": "labor",
        "institutionalist": "institutionalist",
        "regulatory": "institutionalist",
        "industrial policy": "industrial-policy",
        "state capacity": "industrial-policy",
        "security": "security",
    }
    for key, slug in aliases.items():
        if key in normalized:
            return slug
    for term in ("austrian", "chicago", "keynesian", "mmt", "public choice", "labor", "institutionalist"):
        if term in normalized:
            return term.replace(" ", "-")
    return normalized


def split_source_cards(body: str) -> list[str]:
    matches = list(re.finditer(r"^\d+\.\s+", body, flags=re.MULTILINE))
    if not matches:
        matches = list(re.finditer(r"^\*\*.+?\*\*", body, flags=re.MULTILINE))
    cards: list[str] = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(body)
        cards.append(body[match.start():end])
    return cards


def paragraphs(body: str) -> list[str]:
    return [
        para.strip()
        for para in re.split(r"\n\s*\n", body)
        if para.strip() and not para.lstrip().startswith(("#", "|"))
    ]


def is_source_section(title: str) -> bool:
    lower = title.lower()
    return lower.startswith("source cards") or "source notes" in lower or "source interrogation" in lower


def is_causal_topic(title: str, body: str) -> bool:
    lower = title.lower()
    return any(term in lower for term in CAUSAL_SECTION_TERMS)


def has_heading(text: str, expected: str) -> bool:
    expected_lower = expected.lower()
    return any(title.lower().startswith(expected_lower) for _, title, _ in headings(text))


def section_body(text: str, expected: str) -> str:
    expected_lower = expected.lower()
    for title, body in section_bodies(text):
        if title.lower().startswith(expected_lower):
            return body
    return ""


def add_pattern_findings(text: str, patterns: list[tuple[str, str]], severity: str, findings: list[tuple[str, str, str]]) -> None:
    for pattern, message in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            line = text.count("\n", 0, match.start()) + 1
            findings.append((severity, f"line {line}", message))


def read_csv_rows(path: Path, findings: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                findings.append(("FAIL", path.name, "CSV has no header row"))
                return []
            return [
                {key: (value or "").strip() for key, value in row.items() if key is not None}
                for row in reader
            ]
    except csv.Error as exc:
        findings.append(("FAIL", path.name, f"CSV parse error: {exc}"))
        return []


def csv_header(path: Path, findings: list[tuple[str, str, str]]) -> set[str]:
    if not path.exists():
        return set()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            return set(next(reader, []))
    except (csv.Error, StopIteration) as exc:
        findings.append(("FAIL", path.name, f"CSV header error: {exc}"))
        return set()


def truthy(value: str) -> bool:
    return value.strip().lower() in {"yes", "y", "true", "1", "load-bearing", "load bearing"}


def project_text(path: Path) -> str:
    parts: list[str] = []
    for child in sorted(path.rglob("*")):
        if child.is_file() and child.suffix.lower() in {".md", ".csv", ".txt"}:
            try:
                parts.append(child.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                continue
    return "\n".join(parts)


def project_file_texts(path: Path, folder: str) -> list[tuple[Path, str]]:
    root = path / folder
    if not root.exists():
        return []
    out: list[tuple[Path, str]] = []
    for child in sorted(root.rglob("*")):
        if child.is_file() and child.suffix.lower() in {".md", ".csv", ".txt"}:
            try:
                out.append((child, child.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    return out


def row_truthy(row: dict[str, str], key: str) -> bool:
    return truthy(row.get(key, ""))


def split_artifact_paths(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"[;,]", value or "") if part.strip()]


def page_range_width(location: str) -> int | None:
    match = re.search(r"\bpages?\s+(\d+)\s*[-–]\s*(\d+)\b", location, flags=re.IGNORECASE)
    if not match:
        return None
    start, end = int(match.group(1)), int(match.group(2))
    return abs(end - start) + 1


def table_data_rows(text: str) -> int:
    rows = 0
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and not re.fullmatch(r"\|[\s:|-]+\|", stripped):
            rows += 1
    return max(0, rows - 2) if rows >= 2 else 0


def is_unified_project(path: Path) -> bool:
    return any((path / name).exists() for name in ("research-brief.md", "sources.csv", "extractions.csv"))


def check_unified_project(path: Path) -> int:
    findings: list[tuple[str, str, str]] = []
    all_text = project_text(path)

    brief = path / "research-brief.md"
    sources_csv = path / "sources.csv"
    extractions_csv = path / "extractions.csv"
    cache_manifest = path / "source-cache" / "manifest.csv"
    adversarial_eval = path / "adversarial-evaluation.md"

    for name in UNIFIED_PROJECT_REQUIRED_FILES:
        target = path / name
        if not target.exists():
            findings.append(("FAIL", "project", f"missing required artifact: {name}"))
        elif target.stat().st_size < 40:
            findings.append(("FAIL", name, "artifact is empty or too thin"))

    for folder in ("source-cache", "appendices", "updates"):
        if not (path / folder).exists():
            findings.append(("FAIL", "project", f"missing folder: {folder}"))

    missing = SOURCE_REQUIRED_COLUMNS - csv_header(sources_csv, findings)
    if missing:
        findings.append(("FAIL", sources_csv.name, f"missing columns: {', '.join(sorted(missing))}"))
    missing = EXTRACTION_REQUIRED_COLUMNS - csv_header(extractions_csv, findings)
    if missing:
        findings.append(("FAIL", extractions_csv.name, f"missing columns: {', '.join(sorted(missing))}"))
    missing = CACHE_MANIFEST_REQUIRED_COLUMNS - csv_header(cache_manifest, findings)
    if missing:
        findings.append(("FAIL", str(cache_manifest.relative_to(path)), f"missing columns: {', '.join(sorted(missing))}"))

    source_rows = read_csv_rows(sources_csv, findings)
    extraction_rows = read_csv_rows(extractions_csv, findings)
    cache_rows = read_csv_rows(cache_manifest, findings)
    extracted_claim_ids = {row.get("claim_id", "") for row in extraction_rows}
    extracted_source_ids = {row.get("source_id", "") for row in extraction_rows}
    source_ids = {row.get("source_id", "") for row in source_rows}
    source_by_id = {row.get("source_id", ""): row for row in source_rows}
    cache_by_source = {row.get("source_id", ""): row for row in cache_rows}

    if not source_rows:
        findings.append(("FAIL", sources_csv.name, "sources.csv has no source rows"))
    if not extraction_rows:
        findings.append(("FAIL", extractions_csv.name, "extractions.csv has no extraction rows"))

    for source_id in extracted_source_ids:
        if source_id and source_id not in source_ids:
            findings.append(("FAIL", extractions_csv.name, f"extraction row references missing source_id: {source_id}"))

    for idx, row in enumerate(source_rows, start=2):
        source_access = row.get("source_access", "").lower()
        representative_status = row.get("representative_status", "").lower()
        issue_specificity = row.get("issue_specificity", "").lower()
        if representative_status and representative_status not in ECONOMIC_REPRESENTATIVE_STATUS_ALLOWED:
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", f"representative_status must be one of: {', '.join(sorted(ECONOMIC_REPRESENTATIVE_STATUS_ALLOWED))}"))
        if issue_specificity and issue_specificity not in ECONOMIC_ISSUE_SPECIFICITY_ALLOWED:
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", f"issue_specificity must be one of: {', '.join(sorted(ECONOMIC_ISSUE_SPECIFICITY_ALLOWED))}"))
        if source_access not in SOURCE_ACCESS_ALLOWED:
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", f"source_access must be one of: {', '.join(sorted(SOURCE_ACCESS_ALLOWED))}"))
        eligible = row_truthy(row, "eligible_for_central_evidence") or row.get("centrality", "").lower() in {"central", "load-bearing", "load bearing"}
        if eligible and source_access == "snippet_only":
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", "snippet_only source cannot support central evidence"))
        if eligible and source_access == "secondary_summary" and row_truthy(row, "primary_available") and not row_truthy(row, "primary_used"):
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", "secondary summary cannot support central evidence when a primary source is available and not used"))
        if eligible and not row.get("url_or_citation"):
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", "central source lacks url_or_citation"))
        if eligible and any(re.search(pattern, " ".join(row.values()), flags=re.IGNORECASE) for pattern, _ in SNIPPET_EVIDENCE_PATTERNS):
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", "central source row appears to rely on snippet/preview evidence"))
        if eligible:
            cache_row = cache_by_source.get(row.get("source_id", ""))
            if not cache_row:
                findings.append(("FAIL", f"{sources_csv.name} row {idx}", "central source lacks source-cache/manifest.csv row"))
            else:
                status = cache_row.get("cached_status", "").lower()
                if status not in CACHE_STATUS_ALLOWED:
                    findings.append(("FAIL", f"source-cache/manifest.csv source {row.get('source_id', '')}", f"cached_status must be one of: {', '.join(sorted(CACHE_STATUS_ALLOWED))}"))
                if status != "cached" and not cache_row.get("cache_reason"):
                    findings.append(("FAIL", f"source-cache/manifest.csv source {row.get('source_id', '')}", "non-cached central source lacks cache_reason"))
                if status == "metadata_only" and not METADATA_ONLY_ALLOWED_REASON_RE.search(cache_row.get("cache_reason", "")):
                    findings.append(("FAIL", f"source-cache/manifest.csv source {row.get('source_id', '')}", "central source is metadata_only without a concrete legal/access/practical reason caching was not done"))
                if status == "cached":
                    target = cache_row.get("path_or_url", "")
                    if target and not re.match(r"https?://", target):
                        cache_path = path / target
                        if not cache_path.exists():
                            findings.append(("FAIL", f"source-cache/manifest.csv source {row.get('source_id', '')}", f"cached file path does not exist: {target}"))
                if not cache_row.get("copyright_limitations"):
                    findings.append(("FAIL", f"source-cache/manifest.csv source {row.get('source_id', '')}", "missing copyright_limitations note"))
        if eligible and source_access == "partial_document" and re.search(r"\b(academic|peer|study|journal|paper|university|scholar)\b", row.get("source_type", ""), flags=re.IGNORECASE):
            findings.append(("FAIL", f"{sources_csv.name} row {idx}", "central academic/specialist study is only partially inspected; do not use abstracts/metadata as central evidence"))

    for idx, row in enumerate(extraction_rows, start=2):
        status = row.get("status", "").lower()
        if status not in {"supports", "weakens", "mixed", "inconclusive", "fails", "unauditable", "incomplete", "context"}:
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "status must be supports, weakens, mixed, inconclusive, fails, unauditable, incomplete, or context"))
        if not row.get("evidence_location"):
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "missing evidence_location; cite page, table, row, case, docket, or timestamp"))
        else:
            width = page_range_width(row.get("evidence_location", ""))
            if width is not None and width > 2:
                findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "evidence_location page range is too broad; use pinpoint pages, table, row, docket, or timestamp"))
        if not row.get("method_notes"):
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "missing method_notes"))
        if not row.get("our_critique"):
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "missing our_critique"))
        if prose_words(row.get("extracted_data_or_quote", "")) < 8:
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "extracted_data_or_quote is too thin to show what was actually extracted"))
        if row.get("confidence", "").lower() not in {"high", "moderate", "low", "very low", "incomplete"}:
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "confidence must be high, moderate, low, very low, or incomplete"))
        row_text = " ".join(row.values())
        for pattern, message in SNIPPET_EVIDENCE_PATTERNS:
            if re.search(pattern, row_text, flags=re.IGNORECASE):
                findings.append(("FAIL", f"{extractions_csv.name} row {idx}", message))
        source_row = source_by_id.get(row.get("source_id", ""), {})
        cache_row = cache_by_source.get(row.get("source_id", ""), {})
        if UNSTABLE_LOCATION_RE.search(row.get("evidence_location", "")) and cache_row.get("cached_status", "").lower() != "cached":
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "line-number evidence_location requires a cached/local snapshot because web-rendered line numbers are unstable"))
        if source_row.get("source_access", "").lower() == "snippet_only" and status not in {"context", "incomplete", "unauditable"}:
            findings.append(("FAIL", f"{extractions_csv.name} row {idx}", "extraction relies on snippet_only source for an evidentiary claim"))

    if source_rows:
        viewpoint_values = {row.get("viewpoint", "").lower() for row in source_rows}
        source_type_values = {row.get("source_type", "").lower() for row in source_rows}
        if not any(re.search(r"\b(dissident|contrarian|conspir|fringe|outsider|activist|local)\b", value) for value in viewpoint_values | source_type_values):
            findings.append(("WARN", sources_csv.name, "no dissident/local/outsider/conspiratorial source class logged; confirm this was intentional"))
        if not any(re.search(r"\b(academic|peer|study|university|scholar|specialist)\b", value) for value in source_type_values):
            if ECONOMIC_TOPIC_RE.search(all_text):
                findings.append(("FAIL", sources_csv.name, "economic/policy topic has no academic/specialist source class logged"))
            else:
                findings.append(("WARN", sources_csv.name, "no academic/specialist source class logged"))
        if not any(re.search(r"\b(primary|official|court|filing|dataset|record|transcript|local)\b", value) for value in source_type_values):
            findings.append(("FAIL", sources_csv.name, "no primary/official/local/dataset source class logged"))

    if brief.exists():
        brief_text = brief.read_text(encoding="utf-8", errors="ignore")
        brief_lower = brief_text.lower()
        if "todo" in brief_lower:
            findings.append(("FAIL", brief.name, "research brief still contains TODO placeholders"))
        if "pending" in brief_lower and ("quality gate result" in brief_lower or "expert evaluator result" in brief_lower):
            findings.append(("FAIL", brief.name, "quality gate or expert evaluator result is still pending"))
        quality_body = section_body(brief_text, "Quality Gate Result")
        if re.search(r"\b(PostgreSQL|pgAdmin)\b", quality_body, flags=re.IGNORECASE):
            findings.append(("FAIL", "Quality Gate Result", "quality gate command appears to cite an unrelated runtime path"))
        if quality_body and "research_quality_gate.py" not in quality_body:
            findings.append(("FAIL", "Quality Gate Result", "quality gate result does not include the gate command"))
        if re.search(r"\bstatus:\s*incomplete\b|\bdeliverability:\s*incomplete\b", brief_text, flags=re.IGNORECASE):
            findings.append(("FAIL", brief.name, "research brief still marks itself incomplete"))
        if not re.search(r"\bdeliverability status:\s*(deliverable|excellent)\b|\bdeliverability:\s*(deliverable|excellent)\b", brief_text, flags=re.IGNORECASE):
            findings.append(("FAIL", brief.name, "brief lacks deliverable/excellent deliverability status"))
        if prose_words(brief_text) < 1200:
            findings.append(("FAIL", brief.name, "research brief is too thin to be a coherent final output"))

        positions: list[int] = []
        for section in UNIFIED_BRIEF_REQUIRED_SECTIONS:
            if not has_heading(brief_text, section):
                findings.append(("FAIL", brief.name, f"missing required section: {section}"))
            else:
                match = re.search(rf"^#+\s+{re.escape(section)}\b", brief_text, flags=re.IGNORECASE | re.MULTILINE)
                if match:
                    positions.append(match.start())
        if positions != sorted(positions):
            findings.append(("FAIL", brief.name, "required sections are out of the expected reader-coherence order"))
        if not re.search(r"\bC\d+\b", brief_text):
            findings.append(("FAIL", brief.name, "research brief does not cite claim ids"))
        if not re.search(r"\bS\d+\b", brief_text):
            findings.append(("FAIL", brief.name, "research brief does not cite source ids"))
        unsupported_claim_ids = sorted(claim_id for claim_id in set(re.findall(r"\bC\d+\b", brief_text)) if claim_id not in extracted_claim_ids)
        unsupported_source_ids = sorted(source_id for source_id in set(re.findall(r"\bS\d+\b", brief_text)) if source_id not in extracted_source_ids)
        if unsupported_claim_ids:
            findings.append(("FAIL", brief.name, f"brief cites claim ids without extraction support: {', '.join(unsupported_claim_ids)}"))
        if unsupported_source_ids:
            findings.append(("FAIL", brief.name, f"brief cites source ids without extraction support: {', '.join(unsupported_source_ids)}"))

        if PREDICTION_WORD_RE.search(brief_text) and not re.search(r"assumption chain|causal model|causal pipeline|evidence pipeline", brief_text, flags=re.IGNORECASE):
            findings.append(("FAIL", brief.name, "predictive/evaluative language requires an assumption chain, causal model, or evidence pipeline"))

        if ECONOMIC_TOPIC_RE.search(all_text):
            lens_source_rows = [
                row for row in source_rows
                if row.get("economic_lens", "").strip()
                and row.get("economic_lens", "").strip().lower() != "not_applicable"
            ]
            current_lens_sources = [
                row for row in lens_source_rows
                if row.get("representative_status", "").lower() in {"current_issue_specific", "institutional_current"}
                and row.get("issue_specificity", "").lower() == "direct_this_issue"
            ]
            if len(current_lens_sources) < 3:
                findings.append(("FAIL", sources_csv.name, "economic perspectives require at least three current issue-specific economist/institution representative sources, not just canonical theory"))
            represented_lenses = {lens_slug(row.get("economic_lens", "")) for row in current_lens_sources}
            if len(represented_lenses) < 3:
                findings.append(("FAIL", sources_csv.name, "current issue-specific economic representative sources must cover at least three distinct perspectives"))

            econ_body = section_body(brief_text, "Economic Perspectives")
            if not econ_body:
                findings.append(("FAIL", brief.name, "economic/policy topic requires an Economic Perspectives section in the main brief"))
            else:
                present = [term for term in ECONOMIC_LENS_TERMS if term in econ_body.lower()]
                if len(present) < 5:
                    findings.append(("FAIL", "Economic Perspectives", "economic/policy topic lacks enough economic lens coverage"))
                lens_subsections = split_subsections(econ_body)
                if len(lens_subsections) < 3:
                    findings.append(("FAIL", "Economic Perspectives", "economic/policy topic must use per-lens subsections with headings, not paragraph labels or generic summaries"))
                for phrase in ("core claim", "evidence supporting", "evidence weakening", "what this lens explains", "what it misses", "verdict"):
                    if len(re.findall(re.escape(phrase), econ_body, flags=re.IGNORECASE)) < 3:
                        findings.append(("FAIL", "Economic Perspectives", f"lens review lacks repeated evidence-tested field: {phrase}"))
                named_count = len(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b|\b(?:DOJ|FTC|SEC|IMF|OECD|NBER|World Bank|Federal Reserve|Mises Institute|Cato Institute|Brookings Institution)\b", econ_body))
                if named_count < 2:
                    findings.append(("FAIL", "Economic Perspectives", "lens review lacks enough named people, institutions, or texts"))
                for title, body in lens_subsections:
                    if prose_words(body) < 80:
                        continue
                    if "current issue-specific representative source" not in body.lower():
                        findings.append(("FAIL", f"Economic Perspectives: {title}", "lens lacks current issue-specific representative source field"))
                    cited_source_ids = set(re.findall(r"\bS\d+\b", body))
                    if not cited_source_ids:
                        findings.append(("FAIL", f"Economic Perspectives: {title}", "lens analysis cites no source ids"))
                        continue
                    slug = lens_slug(title)
                    direct_matches = [
                        row for row in source_rows
                        if row.get("source_id", "") in cited_source_ids
                        and lens_slug(row.get("economic_lens", "")) == slug
                        and row.get("representative_status", "").lower() in {"current_issue_specific", "institutional_current"}
                        and row.get("issue_specificity", "").lower() == "direct_this_issue"
                    ]
                    incomplete_marker = "no current issue-specific representative found; lens incomplete" in body.lower()
                    if not direct_matches and not incomplete_marker:
                        findings.append(("FAIL", f"Economic Perspectives: {title}", "lens lacks a cited current issue-specific economist/institution source; use source-backed current representatives or write exactly: 'No current issue-specific representative found; lens incomplete.'"))
                    if incomplete_marker and re.search(r"\bverdict:\s*(valid|strong|supported|pass|complete)\b", body, flags=re.IGNORECASE):
                        findings.append(("FAIL", f"Economic Perspectives: {title}", "lens is marked incomplete but still gives a strong/complete verdict"))

        bias_body = section_body(brief_text, "Bias And Symmetry Check")
        for term in ("left/institutional", "right/business/libertarian", "establishment", "anti-establishment", "motive", "reversal"):
            if term not in bias_body.lower():
                findings.append(("FAIL", "Bias And Symmetry Check", f"missing bias/symmetry check term: {term}"))

        md_files = [
            child.relative_to(path).as_posix()
            for child in path.rglob("*.md")
            if child.is_file()
            and child.name not in {"research-brief.md", "adversarial-evaluation.md"}
            and not child.relative_to(path).as_posix().startswith(("appendices/", "updates/"))
        ]
        unreferenced = [name for name in md_files if name not in brief_text]
        if len(unreferenced) > 3:
            findings.append(("FAIL", "artifact sprawl", f"too many markdown artifacts not referenced from research-brief.md: {', '.join(unreferenced)}"))
        elif unreferenced:
            findings.append(("WARN", "artifact sprawl", f"markdown artifacts are not referenced from research-brief.md: {', '.join(unreferenced)}"))

    if adversarial_eval.exists():
        eval_text = adversarial_eval.read_text(encoding="utf-8", errors="ignore")
        eval_lower = eval_text.lower()
        if "todo" in eval_lower:
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation still contains TODO placeholders"))
        match = re.search(r"\bVERDICT:\s*(pass|revise|fail)\b", eval_text, flags=re.IGNORECASE)
        if not match:
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lacks VERDICT: pass|revise|fail"))
        elif match.group(1).lower() != "pass":
            findings.append(("FAIL", adversarial_eval.name, f"adversarial evaluator verdict is not pass: {match.group(1).lower()}"))
        for term in EXPERT_EVALUATOR_REQUIRED_TERMS:
            if term not in eval_lower:
                findings.append(("FAIL", adversarial_eval.name, f"adversarial evaluation lacks expert rubric term/section: {term}"))
        if re.search(r"unsupported load-bearing claims\s*\n+\s*-\s*(?:claim_id:\s*)?C\d+", eval_text, flags=re.IGNORECASE):
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lists unsupported load-bearing claims"))
        if re.search(r"blocking issues[\s\S]{0,800}claim_id:\s*C\d+", eval_text, flags=re.IGNORECASE):
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lists unresolved blocking issues"))

    add_pattern_findings(all_text, HARD_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, WEAK_SOURCE_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, PRESTIGE_FIRST_PATTERNS, "FAIL", findings)

    fail_count = sum(1 for sev, _, _ in findings if sev == "FAIL")
    warn_count = sum(1 for sev, _, _ in findings if sev == "WARN")

    if findings:
        for severity, location, message in findings:
            print(f"{severity}: {location}: {message}")
    else:
        print("PASS: no heuristic quality-gate findings")

    print(f"Summary: {fail_count} fail(s), {warn_count} warning(s)")
    return 1 if fail_count else 0


def check_project(path: Path) -> int:
    if is_unified_project(path):
        return check_unified_project(path)

    findings: list[tuple[str, str, str]] = []
    all_text = project_text(path)

    for name in PROJECT_REQUIRED_FILES:
        target = path / name
        if not target.exists():
            findings.append(("FAIL", "project", f"missing required artifact: {name}"))
        elif target.stat().st_size < 40:
            findings.append(("FAIL", name, "artifact is empty or too thin"))

    for name in PROJECT_RECOMMENDED_FILES:
        target = path / name
        if not target.exists():
            findings.append(("WARN", "project", f"missing recommended artifact: {name}"))

    case_dir = path / "case-audits"
    data_dir = path / "data-audits"
    updates_dir = path / "updates"
    for folder in (case_dir, data_dir, updates_dir):
        if not folder.exists():
            findings.append(("FAIL", "project", f"missing folder: {folder.name}"))

    claim_csv = path / "claim-register.csv"
    coverage_csv = path / "coverage-ledger.csv"
    claim_map = path / "claim-map.md"
    source_csv = path / "source-intake.csv"
    extraction_csv = path / "evidence-extraction.csv"
    synthesis = path / "final-synthesis.md"
    protocol = path / "protocol.md"
    lens_review = path / "lens-review.md"
    adversarial_eval = path / "adversarial-evaluation.md"

    if claim_csv.exists():
        missing = CLAIM_REQUIRED_COLUMNS - csv_header(claim_csv, findings)
        if missing:
            findings.append(("FAIL", claim_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    missing = COVERAGE_REQUIRED_COLUMNS - csv_header(coverage_csv, findings)
    if missing:
        findings.append(("FAIL", coverage_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    missing = SOURCE_REQUIRED_COLUMNS - csv_header(source_csv, findings)
    if missing:
        findings.append(("FAIL", source_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    missing = EXTRACTION_REQUIRED_COLUMNS - csv_header(extraction_csv, findings)
    if missing:
        findings.append(("FAIL", extraction_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    claim_rows = read_csv_rows(claim_csv, findings) if claim_csv.exists() else []
    coverage_rows = read_csv_rows(coverage_csv, findings)
    source_rows = read_csv_rows(source_csv, findings)
    extraction_rows = read_csv_rows(extraction_csv, findings)
    extracted_claim_ids = {row.get("claim_id", "") for row in extraction_rows}
    extracted_source_ids = {row.get("source_id", "") for row in extraction_rows}

    if not coverage_rows:
        findings.append(("FAIL", coverage_csv.name, "coverage-ledger.csv has no rows mapping user subquestions to evidence work"))
    if claim_csv.exists() and not claim_rows:
        findings.append(("FAIL", claim_csv.name, "claim-register.csv has no claim rows"))
    if not source_rows:
        findings.append(("FAIL", source_csv.name, "source-intake.csv has no source rows"))
    if not extraction_rows:
        findings.append(("FAIL", extraction_csv.name, "evidence-extraction.csv has no extraction rows"))

    for idx, row in enumerate(coverage_rows, start=2):
        status = row.get("status", "").lower()
        if status not in {"complete", "partial", "incomplete", "blocked", "not_applicable"}:
            findings.append(("FAIL", f"{coverage_csv.name} row {idx}", "status must be complete, partial, incomplete, blocked, or not_applicable"))
        if row_truthy(row, "central") and status != "complete":
            findings.append(("FAIL", f"{coverage_csv.name} row {idx}", "central user subquestion is not complete; do not deliver settled synthesis"))
        if row_truthy(row, "central") and not row.get("required_primary_sources"):
            findings.append(("FAIL", f"{coverage_csv.name} row {idx}", "central subquestion lacks required_primary_sources"))
        if row_truthy(row, "central") and not row.get("completion_evidence"):
            findings.append(("FAIL", f"{coverage_csv.name} row {idx}", "central subquestion lacks completion_evidence"))
        if row_truthy(row, "central") and status == "complete":
            completion_claim_ids = set(re.findall(r"\bC\d+\b", row.get("completion_evidence", "")))
            if not completion_claim_ids:
                findings.append(("FAIL", f"{coverage_csv.name} row {idx}", "central completion_evidence must cite audited claim ids"))
            else:
                missing_completion_claims = sorted(claim_id for claim_id in completion_claim_ids if claim_id not in extracted_claim_ids)
                if missing_completion_claims:
                    findings.append(("FAIL", f"{coverage_csv.name} row {idx}", f"completion_evidence cites claim ids without extraction rows: {', '.join(missing_completion_claims)}"))
        for artifact in split_artifact_paths(row.get("artifact_path", "")):
            target = path / artifact
            if not target.exists():
                findings.append(("FAIL", f"{coverage_csv.name} row {idx}", f"artifact_path does not exist: {artifact}"))
            elif row_truthy(row, "central") and target.is_file() and target.stat().st_size < 700:
                findings.append(("FAIL", f"{coverage_csv.name} row {idx}", f"central artifact is too thin: {artifact}"))

    source_ids = {row.get("source_id", "") for row in source_rows}
    source_by_id = {row.get("source_id", ""): row for row in source_rows}

    for source_id in extracted_source_ids:
        if source_id and source_id not in source_ids:
            findings.append(("FAIL", extraction_csv.name, f"extraction row references missing source_id: {source_id}"))

    for idx, row in enumerate(source_rows, start=2):
        source_access = row.get("source_access", "").lower()
        if source_access not in SOURCE_ACCESS_ALLOWED:
            findings.append(("FAIL", f"{source_csv.name} row {idx}", f"source_access must be one of: {', '.join(sorted(SOURCE_ACCESS_ALLOWED))}"))
        eligible = row_truthy(row, "eligible_for_central_evidence") or row.get("centrality", "").lower() in {"central", "load-bearing", "load bearing"}
        if eligible and source_access == "snippet_only":
            findings.append(("FAIL", f"{source_csv.name} row {idx}", "snippet_only source cannot support central evidence"))
        if eligible and source_access == "secondary_summary" and row_truthy(row, "primary_available") and not row_truthy(row, "primary_used"):
            findings.append(("FAIL", f"{source_csv.name} row {idx}", "secondary summary cannot support central evidence when a primary source is available and not used"))
        if eligible and not row.get("url_or_citation"):
            findings.append(("FAIL", f"{source_csv.name} row {idx}", "central source lacks url_or_citation"))
        if eligible and any(re.search(pattern, " ".join(row.values()), flags=re.IGNORECASE) for pattern, _ in SNIPPET_EVIDENCE_PATTERNS):
            findings.append(("FAIL", f"{source_csv.name} row {idx}", "central source row appears to rely on snippet/preview evidence"))

    load_bearing_claims = [row for row in claim_rows if truthy(row.get("load_bearing", ""))]
    for row in load_bearing_claims:
        claim_id = row.get("claim_id", "")
        if claim_id and claim_id not in extracted_claim_ids:
            findings.append(("FAIL", extraction_csv.name, f"load-bearing claim lacks extraction row: {claim_id}"))

    for idx, row in enumerate(extraction_rows, start=2):
        status = row.get("status", "").lower()
        if status not in {"supports", "weakens", "mixed", "inconclusive", "fails", "unauditable", "incomplete", "context"}:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "status must be supports, weakens, mixed, inconclusive, fails, unauditable, incomplete, or context"))
        if not row.get("evidence_location"):
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "missing evidence_location; cite page, table, row, case, docket, or timestamp"))
        else:
            width = page_range_width(row.get("evidence_location", ""))
            if width is not None and width > 2:
                findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "evidence_location page range is too broad; use pinpoint pages, table, row, docket, or timestamp"))
        if not row.get("method_notes"):
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "missing method_notes"))
        if not row.get("our_critique"):
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "missing our_critique"))
        if prose_words(row.get("extracted_data_or_quote", "")) < 8:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "extracted_data_or_quote is too thin to show what was actually extracted"))
        if row.get("confidence", "").lower() not in {"high", "moderate", "low", "very low", "incomplete"}:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "confidence must be high, moderate, low, very low, or incomplete"))
        row_text = " ".join(row.values())
        for pattern, message in SNIPPET_EVIDENCE_PATTERNS:
            if re.search(pattern, row_text, flags=re.IGNORECASE):
                findings.append(("FAIL", f"{extraction_csv.name} row {idx}", message))
        source_id = row.get("source_id", "")
        source_row = source_by_id.get(source_id, {})
        if source_row.get("source_access", "").lower() == "snippet_only" and status not in {"context", "incomplete", "unauditable"}:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "extraction relies on snippet_only source for an evidentiary claim"))
        if source_row.get("source_access", "").lower() == "secondary_summary" and row_truthy(source_row, "primary_available") and not row_truthy(source_row, "primary_used") and status not in {"context", "incomplete", "unauditable"}:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "extraction relies on secondary summary even though primary source is available and unused"))

    if source_rows:
        viewpoint_values = {row.get("viewpoint", "").lower() for row in source_rows}
        source_type_values = {row.get("source_type", "").lower() for row in source_rows}
        if not any(re.search(r"\b(dissident|contrarian|conspir|fringe|outsider|activist|local)\b", value) for value in viewpoint_values | source_type_values):
            findings.append(("WARN", source_csv.name, "no dissident/local/outsider/conspiratorial source class logged; confirm this was intentional"))
        if not any(re.search(r"\b(academic|peer|study|university|scholar)\b", value) for value in source_type_values):
            if ECONOMIC_TOPIC_RE.search(all_text):
                findings.append(("FAIL", source_csv.name, "economic/policy topic has no academic/specialist source class logged"))
            else:
                findings.append(("WARN", source_csv.name, "no academic/specialist source class logged"))
        if not any(re.search(r"\b(primary|official|court|filing|dataset|record|transcript|local)\b", value) for value in source_type_values):
            findings.append(("FAIL", source_csv.name, "no primary/official/local/dataset source class logged"))

    if protocol.exists():
        protocol_text = protocol.read_text(encoding="utf-8", errors="ignore")
        for needed in ("Research Question", "Scope", "Definitions", "Done Criteria"):
            if needed.lower() not in protocol_text.lower():
                findings.append(("FAIL", protocol.name, f"missing protocol section: {needed}"))

    if claim_map.exists():
        claim_text = claim_map.read_text(encoding="utf-8", errors="ignore")
        if not re.search(r"\bload-bearing\b", claim_text, flags=re.IGNORECASE):
            findings.append(("FAIL", claim_map.name, "claim map does not identify load-bearing claims"))
        if not re.search(r"\bfalsifier|weakener|would change\b", claim_text, flags=re.IGNORECASE):
            findings.append(("FAIL", claim_map.name, "claim map lacks falsifier/weakener notes"))

    if synthesis.exists():
        synthesis_text = synthesis.read_text(encoding="utf-8", errors="ignore")
        if "incomplete until the quality gate passes" in synthesis_text.lower():
            findings.append(("FAIL", synthesis.name, "synthesis still contains template incomplete status"))
        if "pending" in synthesis_text.lower() and "quality gate result" in synthesis_text.lower():
            findings.append(("FAIL", synthesis.name, "quality gate result still pending"))
        if "pending" in synthesis_text.lower() and "evaluator result" in synthesis_text.lower():
            findings.append(("FAIL", synthesis.name, "evaluator result still pending"))
        if not re.search(r"\bC\d+\b", synthesis_text):
            findings.append(("FAIL", synthesis.name, "final synthesis does not cite claim ids"))
        if not re.search(r"\bS\d+\b", synthesis_text):
            findings.append(("FAIL", synthesis.name, "final synthesis does not cite source ids"))
        if not re.search(r"what survived|survived the audit", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "final synthesis lacks what-survived section"))
        if not re.search(r"failed|overstated|weak", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "final synthesis lacks failed/overstated/weak evidence section"))
        if PREDICTION_WORD_RE.search(synthesis_text) and not re.search(r"assumption chain|assumptions? pipeline|causal pipeline|evidence pipeline", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "predictive/evaluative language requires an Assumption Chain or evidence-pipeline section"))
        if not re.search(r"evaluator result", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "final synthesis lacks Evaluator Result section"))
        synthesis_claim_ids = set(re.findall(r"\bC\d+\b", synthesis_text))
        synthesis_source_ids = set(re.findall(r"\bS\d+\b", synthesis_text))
        unsupported_claim_ids = sorted(claim_id for claim_id in synthesis_claim_ids if claim_id not in extracted_claim_ids)
        unsupported_source_ids = sorted(source_id for source_id in synthesis_source_ids if source_id not in extracted_source_ids)
        if unsupported_claim_ids:
            findings.append(("FAIL", synthesis.name, f"final synthesis cites claim ids without extraction support: {', '.join(unsupported_claim_ids)}"))
        if unsupported_source_ids:
            findings.append(("FAIL", synthesis.name, f"final synthesis cites source ids without extraction support: {', '.join(unsupported_source_ids)}"))

    if adversarial_eval.exists():
        eval_text = adversarial_eval.read_text(encoding="utf-8", errors="ignore")
        eval_lower = eval_text.lower()
        if "todo" in eval_lower:
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation still contains TODO placeholders"))
        match = re.search(r"\bVERDICT:\s*(pass|revise|fail)\b", eval_text, flags=re.IGNORECASE)
        if not match:
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lacks VERDICT: pass|revise|fail"))
        elif match.group(1).lower() != "pass":
            findings.append(("FAIL", adversarial_eval.name, f"adversarial evaluator verdict is not pass: {match.group(1).lower()}"))
        for term in EVALUATOR_REQUIRED_TERMS:
            if term not in eval_lower:
                findings.append(("FAIL", adversarial_eval.name, f"adversarial evaluation lacks required review term/section: {term}"))
        if re.search(r"blocking issues\s*\n+\s*(?:-|none|no blocking)", eval_text, flags=re.IGNORECASE):
            # Accept explicit none/no blocking; detailed blocking lists are allowed only when verdict is not pass.
            pass
        if re.search(r"unsupported load-bearing claims\s*\n+\s*-\s*(?:claim_id:\s*)?C\d+", eval_text, flags=re.IGNORECASE):
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lists unsupported load-bearing claims"))
        if re.search(r"blocking issues[\s\S]{0,800}claim_id:\s*C\d+", eval_text, flags=re.IGNORECASE):
            findings.append(("FAIL", adversarial_eval.name, "adversarial evaluation lists unresolved blocking issues"))

    coverage_text = "\n".join(row.get("user_question_part", "") for row in coverage_rows)
    source_text = "\n".join(
        " ".join([row.get("title", ""), row.get("source_type", ""), row.get("url_or_citation", "")])
        for row in source_rows
    )
    case_audit_text = "\n".join(text for _, text in project_file_texts(path, "case-audits"))
    data_audit_text = "\n".join(text for _, text in project_file_texts(path, "data-audits"))

    def coverage_mentions(pattern: re.Pattern[str], label: str) -> None:
        if pattern.search(all_text) and not pattern.search(coverage_text):
            findings.append(("FAIL", coverage_csv.name, f"user asked about {label}, but coverage ledger has no matching row"))

    coverage_mentions(STANDING_TOPIC_RE, "standing")
    coverage_mentions(TRIAL_TOPIC_RE, "trial/record")
    coverage_mentions(ARGUMENT_TOPIC_RE, "arguments/briefs/transcript")
    coverage_mentions(QUANT_TOPIC_RE, "quantitative/methodology questions")

    if LEGAL_TOPIC_RE.search(all_text):
        if ARGUMENT_TOPIC_RE.search(all_text) and not re.search(r"\b(brief|transcript|oral argument)\b", source_text, flags=re.IGNORECASE):
            findings.append(("FAIL", source_csv.name, "legal argument question requires primary briefs and/or oral-argument transcript in source intake"))
        if DOCTRINE_TOPIC_RE.search(all_text) and not re.search(r"\b(holding|test|dicta|application|inference|prediction|old rule|new rule|counterargument)\b", all_text, flags=re.IGNORECASE):
            findings.append(("FAIL", "legal analysis", "doctrinal topic requires layered analysis separating holding, test, dicta/application, inference/prediction, and counterarguments"))
        if STANDING_TOPIC_RE.search(all_text) and not re.search(r"\b(plaintiff|injury|district|doctrine|weakness|hays|standing)\b", case_audit_text, flags=re.IGNORECASE):
            findings.append(("FAIL", "case-audits", "standing question requires plaintiff-by-plaintiff or injury-by-injury standing audit"))
        if TRIAL_TOPIC_RE.search(all_text):
            for term in ("witness", "exhibit", "finding"):
                if not re.search(rf"\b{term}s?\b", case_audit_text, flags=re.IGNORECASE):
                    findings.append(("FAIL", "case-audits", f"trial-record question requires {term} analysis, not just timeline summary"))

    if QUANT_TOPIC_RE.search(all_text):
        if not data_audit_text:
            findings.append(("FAIL", "data-audits", "quantitative/methodology question requires a data audit"))
        else:
            for term, message in [
                (r"\b(row-level|seat-by-seat|unit_id|district-by-district|case-by-case)\b", "row-level/unit reconstruction"),
                (r"\bbaseline|threshold|denominator|classification rule\b", "baseline and classification-rule discussion"),
                (r"\bassumption|constraint|sensitivity\b", "assumption/constraint sensitivity discussion"),
                (r"\bconfidence|uncertainty|error\b", "confidence/uncertainty rating"),
            ]:
                if not re.search(term, data_audit_text, flags=re.IGNORECASE):
                    findings.append(("FAIL", "data-audits", f"quantitative/methodology audit lacks {message}"))
            if table_data_rows(data_audit_text) < 3:
                findings.append(("FAIL", "data-audits", "quantitative/methodology audit lacks a row-level table with multiple units"))

    add_pattern_findings(all_text, HARD_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, WEAK_SOURCE_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, PRESTIGE_FIRST_PATTERNS, "FAIL", findings)

    if ECONOMIC_TOPIC_RE.search(all_text):
        if not lens_review.exists():
            findings.append(("FAIL", "project", "economic/policy topic requires lens-review.md"))
        else:
            lens_original = lens_review.read_text(encoding="utf-8", errors="ignore")
            lens_text = lens_original.lower()
            present = [term for term in ECONOMIC_LENS_TERMS if term in lens_text]
            if len(present) < 5:
                findings.append(("FAIL", lens_review.name, "economic/policy topic lacks enough economic lens coverage"))
            if not re.search(r"\bactual argument\b|\bnamed viewpoint\b|\brepresentative\b", lens_text):
                findings.append(("FAIL", lens_review.name, "economic/policy lens review lacks named representatives or actual-argument structure"))
            named_count = len(re.findall(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b|\b(?:DOJ|FTC|SEC|IMF|OECD|NBER|World Bank|Federal Reserve|Mises Institute|Cato Institute|Brookings Institution)\b", lens_original))
            if named_count < 2:
                findings.append(("FAIL", lens_review.name, "economic/policy lens review lacks enough named people, institutions, or texts"))

    fail_count = sum(1 for sev, _, _ in findings if sev == "FAIL")
    warn_count = sum(1 for sev, _, _ in findings if sev == "WARN")

    if findings:
        for severity, location, message in findings:
            print(f"{severity}: {location}: {message}")
    else:
        print("PASS: no heuristic quality-gate findings")

    print(f"Summary: {fail_count} fail(s), {warn_count} warning(s)")
    return 1 if fail_count else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Evidence Audit Project directory or legacy Markdown dossier to check")
    args = parser.parse_args()

    path = Path(args.path)
    if path.is_dir():
        return check_project(path)

    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    findings: list[tuple[str, str, str]] = []
    total_links = count_links(text)

    if total_links == 0:
        findings.append(("FAIL", "document", "legacy dossier contains no retraceable URLs or markdown links"))
    elif total_links < 8:
        findings.append(("WARN", "document", f"legacy dossier has only {total_links} link(s); source trail may be too thin"))
    if total_links < 15:
        findings.append(("FAIL", "document", f"legacy dossier has only {total_links} link(s); full legacy dossiers need a deeper source trail"))

    for required in REQUIRED_SECTIONS:
        if required.lower() not in lower:
            findings.append(("FAIL", "document", f"missing expected section containing '{required}'"))

    implementation_terms = r"\b(project|facility|facilities|permit|zoning|tariff|contract|ratepayer|utility|data center|datacenter|power plant|transmission|substation|water rights?)\b"
    if re.search(implementation_terms, text, flags=re.IGNORECASE):
        if not re.search(r"^##\s+Case (?:or|and) Project Audit|^##\s+Case/Project Audit", text, flags=re.IGNORECASE | re.MULTILINE):
            findings.append(("FAIL", "document", "implementation-dependent topic requires a Case and Project Audit section"))

    add_pattern_findings(text, HARD_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, WEAK_SOURCE_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, GENERIC_VIEWPOINT_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, VAGUE_FUNDER_PATTERNS, "FAIL", findings)

    if re.search(r"\b(what caused|why has|why did|causes? of|drivers? of|causal question|radicalization)\b", text, flags=re.IGNORECASE):
        if not has_heading(text, "Causal Claim Matrix"):
            findings.append(("FAIL", "document", "causal research requires a Causal Claim Matrix with evidence, alternatives, counterevidence, confidence, and falsifiers"))

    for title, body in section_bodies(text):
        words = prose_words(body)
        bullets = bullet_lines(body)
        links = count_links(body)
        if any(title.lower().startswith(name.lower()) for name in LINK_REQUIRED_SECTIONS) and links == 0:
            findings.append(("FAIL", title, "section requires retraceable links to sources/records"))
        if is_source_section(title):
            source_card_markers = len(re.findall(r"^\*\*.+?\*\*", body, flags=re.MULTILINE))
            cards = split_source_cards(body)
            source_count = max(source_card_markers, len(cards))
            if source_count < 8:
                findings.append(("FAIL", title, f"too few source cards ({source_count}); full legacy dossiers need a broader source base"))
            if source_count >= 3 and links < max(3, source_count):
                findings.append(("FAIL", title, "source cards name sources without enough direct links"))
            if "what parts" not in body.lower() and "parts read" not in body.lower() and "inspected" not in body.lower():
                findings.append(("FAIL", title, "source cards do not say what parts were read or inspected"))
            for idx, card in enumerate(cards, start=1):
                missing = [field for field in SOURCE_CARD_REQUIRED_FIELDS if field.lower() not in card.lower()]
                if missing:
                    findings.append(("FAIL", f"{title} card {idx}", f"source card missing fields: {', '.join(missing)}"))
                for pattern, label in SOURCE_CARD_METHOD_FIELD_PATTERNS:
                    if not re.search(pattern, card, flags=re.IGNORECASE):
                        findings.append(("FAIL", f"{title} card {idx}", f"source card missing {label}"))
                for pattern, message in VAGUE_READ_PATTERNS:
                    if re.search(pattern, card, flags=re.IGNORECASE):
                        findings.append(("FAIL", f"{title} card {idx}", message))
                if prose_words(card) < 150:
                    findings.append(("FAIL", f"{title} card {idx}", "source card is too thin; material sources need source-interrogation detail, not a bibliography summary"))
                if re.search(r"\b(peer-reviewed|study|survey|dataset|analysis|report|paper|methodology|model|experiment)\b", card, flags=re.IGNORECASE):
                    required_method_terms = [
                        r"\b(sample|n\s*=|respondents|unit of analysis|dataset|data)\b",
                        r"\b(method|methodology|model|coding|specification|experiment|regression|case selection)\b",
                        r"\b(uncertainty|confidence interval|robustness|sensitivity|limitation|bias|confound|selection|measurement)\b",
                    ]
                    for req in required_method_terms:
                        if not re.search(req, card, flags=re.IGNORECASE):
                            findings.append(("FAIL", f"{title} card {idx}", "study/data source card lacks sample/data, method, or uncertainty/bias appraisal detail"))
                            break
                if any(term in card.lower() for term in ADVOCACY_SOURCE_TERMS):
                    if not re.search(r"\b(fund|donor|member|owner|financial|revenue|opaque|incentive|conflict)\b", card, flags=re.IGNORECASE):
                        findings.append(("FAIL", f"{title} card {idx}", "advocacy/industry/think-tank source lacks funding, ownership, member, or incentive note"))
        if title.lower().startswith("study and data readouts") and not re.search(r"\b(method|methodology|scenario|sample|model|uncertainty|confidence interval|limitation)\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "study/data readouts lack method or uncertainty discussion"))
        if title.lower().startswith(("study and data readouts", "study")) and prose_words(body) < 450:
            findings.append(("FAIL", title, "study/data readouts are too thin for a full legacy dossier"))
        if title.lower().startswith(("study and data readouts", "study")):
            required_readout_terms = [
                (r"\b(research question|question tested|what .* tested|authors tested)\b", "research question tested"),
                (r"\b(sample|n\s*=|respondents|observations|unit of analysis|cases|dataset)\b", "sample/unit/data"),
                (r"\b(method|methodology|model|coding|specification|experiment|regression|identification|instrument)\b", "method/design"),
                (r"\b(effect size|magnitude|percentage|percent|confidence interval|uncertainty|estimate|rate|count)\b", "magnitude/uncertainty"),
                (r"\b(confound|selection bias|measurement error|external validity|causal|descriptive|correlation|limitation|robustness|sensitivity)\b", "validity limits"),
                (r"\b(source weight|weight|high confidence|moderate confidence|low confidence|quality)\b", "source weight/quality judgment"),
            ]
            for pattern, label in required_readout_terms:
                if not re.search(pattern, body, flags=re.IGNORECASE):
                    findings.append(("FAIL", title, f"study/data readouts lack {label}"))
        if title.lower().startswith(("case or project audits", "case and project audit", "case or project audit")) and not re.search(r"\b(permit|tariff|order|filing|docket|zoning|minutes|agreement|audit|regulator|commission)\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "case/project audit lacks primary-record indicators"))
        if title.lower().startswith(("case or project audits", "case and project audit", "case or project audit")):
            case_words = prose_words(body)
            case_links = count_links(body)
            if case_words < 700:
                findings.append(("FAIL", title, "case/project audit is too thin; inspect concrete cases with records"))
            if case_links < 4:
                findings.append(("FAIL", title, "case/project audit needs direct links to several local/project/regulatory records"))
            case_subsections = split_subsections(body)
            if case_subsections and len(case_subsections) < 4:
                findings.append(("FAIL", title, "case/project audit needs at least four concrete cases or a narrowed boundary"))
            for case_title, case_body in case_subsections:
                if prose_words(case_body) < 150:
                    findings.append(("FAIL", f"{title}: {case_title}", "case entry is too thin"))
                if count_links(case_body) == 0:
                    findings.append(("FAIL", f"{title}: {case_title}", "case entry lacks direct source links"))
                if not re.search(r"\b(developer|operator|utility|regulator|commission|docket|permit|tariff|order|agreement|status|mw|megawatt|water|substation|transmission)\b", case_body, flags=re.IGNORECASE):
                    findings.append(("FAIL", f"{title}: {case_title}", "case entry lacks concrete project/regulatory fields"))
        if title.lower().startswith("viewpoint") and re.search(r"represented by groups such as|represented by hyperscalers|represented by energy-policy commentators|represented by .*advocates", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "viewpoint representatives are too generic; name specific actors/institutions/texts"))
        if title.lower().startswith("viewpoint") and re.search(r"\blocal opposition groups\b|\bhyperscalers\b|\bstate utility commissions\b|\benergy-market conservatives\b|\bsome industry groups\b|\blocal conservation groups\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "viewpoint map still relies on generic groups instead of named actors"))
        if title.lower().startswith("viewpoint"):
            if prose_words(body) < 900:
                findings.append(("FAIL", title, "viewpoint map is too thin for a contested topic"))
            if not re.search(r"\b(funding|funded|donor|member|membership|ownership|financial|incentive|conflict|opaque)\b", body, flags=re.IGNORECASE):
                findings.append(("FAIL", title, "viewpoint map lacks funding/ownership/incentive analysis"))
        if title.lower().startswith("policy options") and links == 0:
            findings.append(("FAIL", title, "policy options need source links or evidence anchors"))
        if title.lower().startswith("policy options") and prose_words(body) < 700:
            findings.append(("FAIL", title, "policy options are too thin; include mechanism, implementation, enforcement, tradeoffs, and objections"))
        if is_causal_topic(title, body):
            if not has_heading(text, "Causal Claim Matrix"):
                findings.append(("FAIL", title, "causal question/section requires a Causal Claim Matrix before narrative synthesis"))
            if title.lower().startswith(("causal synthesis", "why", "cause")):
                for para_idx, para in enumerate(paragraphs(body), start=1):
                    if prose_words(para) >= 60 and CAUSAL_LANGUAGE_RE.search(para) and count_links(para) == 0:
                        findings.append(("FAIL", f"{title} paragraph {para_idx}", "causal assertion lacks a direct citation/evidence anchor"))
                    if re.search(r"\bmade .{0,80} feel\b|\bfeel newly\b|\bthe common pathway is\b|\bthe feedback loop\b", para, flags=re.IGNORECASE):
                        findings.append(("FAIL", f"{title} paragraph {para_idx}", "causal prose uses speculative narrative framing; tie it to a causal matrix or rewrite as an evidenced claim"))
        if title.lower().startswith("claim ledger") and not re.search(r"\b(Status|Assessment):", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "claim ledger lacks explicit status/assessment rows"))
        if title.lower().startswith("quality gate") and not re.search(r"\b(pass|fail|warning|0 fail|0 warning|gate)\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "quality gate section does not report gate result"))
        if words > 120 and bullets >= 5 and links == 0:
            findings.append(("WARN", title, "bullet-heavy section has no citations/links"))
        if title.lower().startswith(("rubric", "assessment")) and "threshold" not in body.lower():
            findings.append(("FAIL", title, "rubric/assessment section lacks explicit thresholds"))
        if title.lower().startswith(("rubric", "assessment")) and "counterexample" not in body.lower() and "consistency" not in body.lower():
            findings.append(("FAIL", title, "rubric/assessment section lacks counterexample or consistency check"))
        if title.lower().startswith(("debate", "viewpoint")) and re.search(r"\brepresentative (sources/)?voices?:", body, flags=re.IGNORECASE):
            if not re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b", body):
                findings.append(("FAIL", title, "viewpoint section appears not to name representative people"))

    fail_count = sum(1 for sev, _, _ in findings if sev == "FAIL")
    warn_count = sum(1 for sev, _, _ in findings if sev == "WARN")

    if findings:
        for severity, location, message in findings:
            print(f"{severity}: {location}: {message}")
    else:
        print("PASS: no heuristic quality-gate findings")

    print(f"Summary: {fail_count} fail(s), {warn_count} warning(s)")
    return 1 if fail_count else 0


if __name__ == "__main__":
    sys.exit(main())
