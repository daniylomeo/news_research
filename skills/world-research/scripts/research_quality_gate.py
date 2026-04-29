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
    "claim-map.md",
    "source-intake.csv",
    "evidence-extraction.csv",
    "audit-trail.md",
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
    "claims_made",
    "data_access",
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

PRESTIGE_FIRST_PATTERNS = [
    (r"\bcredible because (?:it is|they are)\b", "source appears judged by reputation before evidence"),
    (r"\btrusted because (?:it is|they are)\b", "source appears judged by reputation before evidence"),
    (r"\breputable (?:source|institution|journal|think tank) (?:therefore|so)\b", "prestige is being used as evidence"),
    (r"\bfringe source,? so\b", "outsider status is being used as a shortcut against evidence"),
    (r"\bconspiracy source,? so\b", "conspiratorial label is being used as a shortcut against evidence"),
]

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


def check_project(path: Path) -> int:
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
    claim_map = path / "claim-map.md"
    source_csv = path / "source-intake.csv"
    extraction_csv = path / "evidence-extraction.csv"
    synthesis = path / "final-synthesis.md"
    protocol = path / "protocol.md"
    lens_review = path / "lens-review.md"

    if claim_csv.exists():
        missing = CLAIM_REQUIRED_COLUMNS - csv_header(claim_csv, findings)
        if missing:
            findings.append(("FAIL", claim_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    missing = SOURCE_REQUIRED_COLUMNS - csv_header(source_csv, findings)
    if missing:
        findings.append(("FAIL", source_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    missing = EXTRACTION_REQUIRED_COLUMNS - csv_header(extraction_csv, findings)
    if missing:
        findings.append(("FAIL", extraction_csv.name, f"missing columns: {', '.join(sorted(missing))}"))

    claim_rows = read_csv_rows(claim_csv, findings) if claim_csv.exists() else []
    source_rows = read_csv_rows(source_csv, findings)
    extraction_rows = read_csv_rows(extraction_csv, findings)

    if claim_csv.exists() and not claim_rows:
        findings.append(("FAIL", claim_csv.name, "claim-register.csv has no claim rows"))
    if not source_rows:
        findings.append(("FAIL", source_csv.name, "source-intake.csv has no source rows"))
    if not extraction_rows:
        findings.append(("FAIL", extraction_csv.name, "evidence-extraction.csv has no extraction rows"))

    source_ids = {row.get("source_id", "") for row in source_rows}
    extracted_claim_ids = {row.get("claim_id", "") for row in extraction_rows}
    extracted_source_ids = {row.get("source_id", "") for row in extraction_rows}

    for source_id in extracted_source_ids:
        if source_id and source_id not in source_ids:
            findings.append(("FAIL", extraction_csv.name, f"extraction row references missing source_id: {source_id}"))

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
        if not row.get("method_notes"):
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "missing method_notes"))
        if not row.get("our_critique"):
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "missing our_critique"))
        if row.get("confidence", "").lower() not in {"high", "moderate", "low", "very low", "incomplete"}:
            findings.append(("FAIL", f"{extraction_csv.name} row {idx}", "confidence must be high, moderate, low, very low, or incomplete"))

    if source_rows:
        viewpoint_values = {row.get("viewpoint", "").lower() for row in source_rows}
        source_type_values = {row.get("source_type", "").lower() for row in source_rows}
        if not any(re.search(r"\b(dissident|contrarian|conspir|fringe|outsider|activist|local)\b", value) for value in viewpoint_values | source_type_values):
            findings.append(("WARN", source_csv.name, "no dissident/local/outsider/conspiratorial source class logged; confirm this was intentional"))
        if not any(re.search(r"\b(academic|peer|study|university|scholar)\b", value) for value in source_type_values):
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
        if not re.search(r"\bC\d+\b", synthesis_text):
            findings.append(("FAIL", synthesis.name, "final synthesis does not cite claim ids"))
        if not re.search(r"\bS\d+\b", synthesis_text):
            findings.append(("FAIL", synthesis.name, "final synthesis does not cite source ids"))
        if not re.search(r"what survived|survived the audit", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "final synthesis lacks what-survived section"))
        if not re.search(r"failed|overstated|weak", synthesis_text, flags=re.IGNORECASE):
            findings.append(("FAIL", synthesis.name, "final synthesis lacks failed/overstated/weak evidence section"))

    add_pattern_findings(all_text, HARD_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, WEAK_SOURCE_PATTERNS, "FAIL", findings)
    add_pattern_findings(all_text, PRESTIGE_FIRST_PATTERNS, "FAIL", findings)

    if ECONOMIC_TOPIC_RE.search(all_text):
        if not lens_review.exists():
            findings.append(("FAIL", "project", "economic/policy topic requires lens-review.md"))
        else:
            lens_text = lens_review.read_text(encoding="utf-8", errors="ignore").lower()
            present = [term for term in ECONOMIC_LENS_TERMS if term in lens_text]
            if len(present) < 5:
                findings.append(("FAIL", lens_review.name, "economic/policy topic lacks enough economic lens coverage"))

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
