from __future__ import annotations

import html as html_lib
import re
from collections import Counter
from pathlib import Path

from .common import read_csv, section_body, truthy, words
from .schema import READER_EDUCATION_HEADERS, Finding


FIELD_RE = re.compile(
    r"^\s*(?:\*\*|__)?(Reader orientation|What happened or how it works|Evidence guide|Dispute and limits|Why it matters)"
    r"(?:[.:])?(?:\*\*|__)?\s*:?\s*",
    flags=re.I | re.M,
)
TABLE_DELIMITER_RE = re.compile(
    r"\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*"
)
PLACEHOLDER_RE = re.compile(r"\b(todo|tbd|placeholder|lorem ipsum|not yet evaluated|pending)\b", flags=re.I)
EDUCATION_STATUS = {"planned", "draft", "complete"}
COLD_STATUS = {"pending", "pass", "fail"}


def _finding(code: str, location: str, message: str) -> Finding:
    return Finding("FAIL", code, location, message)


def strip_nonrendered_markdown(text: str) -> str:
    """Remove comments and code containers that cannot count as rendered prose."""

    def mask_non_newlines(match: re.Match[str]) -> str:
        return re.sub(r"[^\r\n]", "", match.group(0))

    without_comments = re.sub(r"<!--[\s\S]*?(?:-->|\Z)", mask_non_newlines, text or "")
    visible_lines: list[str] = []
    fence_char = ""
    fence_width = 0
    for line in without_comments.splitlines():
        if fence_char:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence_char)}{{{fence_width},}}[ \t]*", line):
                fence_char = ""
                fence_width = 0
            visible_lines.append("")
            continue
        if re.match(r"^(?: {4,}| {0,3}\t)", line):
            visible_lines.append("")
            continue
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence and not (fence.group(1).startswith("`") and "`" in fence.group(2)):
            fence_char = fence.group(1)[0]
            fence_width = len(fence.group(1))
            visible_lines.append("")
            continue
        visible_lines.append(line)
    return "\n".join(visible_lines)


def mask_markdown_link_destinations(text: str) -> str:
    chars = list(text or "")
    index = 0
    while index + 1 < len(chars):
        if chars[index] != "]" or chars[index + 1] != "(" or (index and chars[index - 1] == "\\"):
            index += 1
            continue
        depth = 1
        cursor = index + 2
        while cursor < len(chars) and depth:
            if chars[cursor] == "\\":
                cursor += 2
                continue
            if chars[cursor] == "(":
                depth += 1
            elif chars[cursor] == ")":
                depth -= 1
                if depth == 0:
                    break
            cursor += 1
        if depth == 0:
            for target_index in range(index + 2, cursor):
                if chars[target_index] not in "\r\n":
                    chars[target_index] = " "
            index = cursor + 1
        else:
            index += 2
    return "".join(chars)


def rendered_visible_text(text: str) -> str:
    visible = strip_nonrendered_markdown(text)
    visible = re.sub(r"^ {0,3}\[[^\]\r\n]+\]:\s*(?:<[^>\r\n]*>|\S+).*$", "", visible, flags=re.M)
    visible = mask_markdown_link_destinations(visible)
    visible = re.sub(r"<https?://[^>]+>", "", visible, flags=re.I)
    visible = re.sub(r"https?://\S+", "", visible, flags=re.I)
    return re.sub(r"<[^>]+>", " ", visible)


def exact_section_body(text: str, title: str, level: int = 2) -> str:
    marker = "#" * level
    match = re.search(
        rf"^{marker}\s+{re.escape(title)}\s*$\n(.*?)(?=^#{{1,{level}}}\s+|\Z)",
        text or "",
        flags=re.I | re.M | re.S,
    )
    return match.group(1).strip() if match else ""


def section_bodies(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^(#{2,6})\s+(.+?)\s*$", text or "", flags=re.M))
    out: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        level = len(match.group(1))
        end = len(text)
        for later in matches[index + 1 :]:
            if len(later.group(1)) <= level:
                end = later.start()
                break
        out.append((match.group(2).strip(), text[match.end() : end].strip()))
    return out


def markdown_table_blocks(text: str) -> list[tuple[int, int]]:
    lines = (text or "").splitlines()
    normalized = [re.sub(r"^\s*(?:>\s*)+", "", line) for line in lines]
    blocks: list[tuple[int, int]] = []
    index = 0
    while index + 1 < len(lines):
        if "|" not in normalized[index] or not TABLE_DELIMITER_RE.fullmatch(normalized[index + 1]):
            index += 1
            continue
        end = index + 2
        while end < len(lines):
            stripped = normalized[end].strip()
            if not stripped or stripped.startswith("#") or "|" not in stripped:
                break
            end += 1
        blocks.append((index, end))
        index = end
    return blocks


def markdown_table_rows(text: str) -> list[tuple[list[str], list[list[str]]]]:
    lines = (text or "").splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    for start, end in markdown_table_blocks(text):
        parsed: list[list[str]] = []
        for line in lines[start:end]:
            normalized = re.sub(r"^\s*(?:>\s*)+", "", line).strip().strip("|")
            parsed.append([cell.strip() for cell in re.split(r"(?<!\\)\|", normalized)])
        if len(parsed) >= 2:
            tables.append((parsed[0], parsed[2:]))
    return tables


def html_table_rows(text: str) -> list[tuple[list[str], list[list[str]]]]:
    tables: list[tuple[list[str], list[list[str]]]] = []
    for table in re.findall(r"<table\b[\s\S]*?</table\s*>", text or "", flags=re.I):
        parsed: list[list[str]] = []
        for row in re.findall(r"<tr\b[^>]*>([\s\S]*?)</tr\s*>", table, flags=re.I):
            cells = []
            for cell in re.findall(r"<t[hd]\b[^>]*>([\s\S]*?)</t[hd]\s*>", row, flags=re.I):
                plain = re.sub(r"<[^>]+>", " ", cell)
                cells.append(re.sub(r"\s+", " ", html_lib.unescape(plain)).strip())
            if cells:
                parsed.append(cells)
        if parsed:
            tables.append((parsed[0], parsed[1:]))
    return tables


def non_table_text(text: str) -> str:
    rendered = strip_nonrendered_markdown(text)
    rendered = re.sub(r"<table\b[\s\S]*?</table\s*>", "", rendered, flags=re.I)
    lines = rendered.splitlines()
    excluded = {index for start, end in markdown_table_blocks(rendered) for index in range(start, end)}
    return "\n".join(line for index, line in enumerate(lines) if index not in excluded)


def narrative_paragraphs(text: str) -> list[str]:
    narrative: list[str] = []
    for paragraph in re.split(r"\n\s*\n", non_table_text(text)):
        lines = [line for line in paragraph.splitlines() if line.strip()]
        if lines and FIELD_RE.fullmatch(lines[0].strip()):
            lines = lines[1:]
        if not lines or any(re.match(r"^\s*(?:>|[-*+]\s+|\d+[.)]\s+)", line) for line in lines):
            continue
        candidate = "\n".join(lines)
        if words(candidate) >= 25:
            narrative.append(candidate)
    return narrative


def education_module_fields(text: str) -> tuple[dict[str, str], set[str]]:
    visible = non_table_text(text)
    matches = list(FIELD_RE.finditer(visible))
    fields: dict[str, str] = {}
    duplicates: set[str] = set()
    for index, match in enumerate(matches):
        raw = match.group(1).lower()
        if raw.startswith("reader orientation"):
            key = "reader orientation"
        elif raw.startswith("what happened"):
            key = "what happened or how it works"
        elif raw.startswith("evidence guide"):
            key = "evidence guide"
        elif raw.startswith("dispute"):
            key = "dispute and limits"
        else:
            key = "why it matters"
        end = matches[index + 1].start() if index + 1 < len(matches) else len(visible)
        if key in fields:
            duplicates.add(key)
        fields[key] = visible[match.end() : end].strip()
    return fields, duplicates


def markdown_field_value(text: str, label: str) -> str:
    match = re.search(
        rf"^\s*[-*+]\s+(?:\*\*{re.escape(label)}:\*\*|\*\*{re.escape(label)}\*\*\s*:|"
        rf"__{re.escape(label)}:__|__{re.escape(label)}__\s*:|{re.escape(label)}\s*:)\s*(.+?)\s*$",
        text or "",
        flags=re.I | re.M,
    )
    return match.group(1).strip() if match else ""


def significant_terms(value: str) -> set[str]:
    stopwords = {
        "about", "after", "again", "against", "among", "article", "before", "between",
        "brief", "case", "cases", "central", "comparison", "counterexample", "evidence",
        "from", "historical", "history", "into", "module", "political", "research", "that",
        "their", "this", "through", "under", "what", "when", "where", "which", "with", "without",
    }
    return {
        token[:6]
        for token in re.findall(r"[a-z0-9]+", (value or "").lower())
        if len(token) >= 4 and token not in stopwords
    }


def cold_specific_terms(value: str) -> set[str]:
    generic = {
        "actor", "articl", "case", "clearl", "comple", "disput", "eviden", "explai", "guide",
        "happen", "limit", "matter", "module", "named", "packet", "reader", "releva", "result",
        "sequen", "source", "unders", "works",
    }
    return significant_terms(value) - generic


def explicit_extraction_pairs(text: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    separator = r"(?:\s*[,/&+]\s*|\s+and\s+)"
    for claim_id, source_id in re.findall(rf"\b(C\d+)\b{separator}\b(S\d+)\b", text or "", flags=re.I):
        pairs.add((claim_id.upper(), source_id.upper()))
    for source_id, claim_id in re.findall(rf"\b(S\d+)\b{separator}\b(C\d+)\b", text or "", flags=re.I):
        pairs.add((claim_id.upper(), source_id.upper()))
    return pairs


def human_readable_link_count(text: str) -> int:
    generic_labels = {"click here", "read more", "source link", "this source", "the source"}
    count = 0
    for label, target in re.findall(r"\[([^\]]+)\]\((https?://[^\s)]+(?:\([^)]*\)[^\s)]*)?)\)", text or "", flags=re.I):
        normalized_label = re.sub(r"\s+", " ", label.strip().lower())
        if words(label) >= 2 and normalized_label not in generic_labels and not re.fullmatch(r"[CSM]\d+", label.strip(), flags=re.I):
            count += 1
    return count


def is_case_comparison_table(section_title: str, header: list[str]) -> bool:
    title = section_title.lower()
    header_text = " ".join(header).lower()
    title_signal = bool(re.search(r"\b(?:compar\w*|matrix|parallel\w*|precedent\w*|analog\w*|illustrat\w*|cross[- ]case|case recap|historical recap|selected examples)\b", title))
    case_signal = bool(re.search(r"\b(?:case|episode|center|empire|kingdom|institution|polity|precedent|parallel|example|subject)\b", header_text))
    jurisdiction_signal = bool(re.search(r"\bjurisdiction\w*\b", header_text))
    analytic_signal = bool(re.search(r"\b(?:channel|route|outcome|consequence\w*|lesson|mechanism|causal|access(?:\s+route)?|effect|result|implication|takeaway)\b", header_text))
    return (title_signal and (case_signal or analytic_signal)) or (case_signal and analytic_signal) or (jurisdiction_signal and analytic_signal)


def _split_ids(value: str, prefix: str) -> set[str]:
    return {item.upper() for item in re.findall(rf"\b{re.escape(prefix)}\d+\b", value or "", flags=re.I)}


def _check_reader_contract(packet: str, findings: list[Finding]) -> None:
    assignment = section_body(strip_nonrendered_markdown(packet), "Assignment And Boundary")
    reader_baseline = markdown_field_value(assignment, "Reader baseline")
    assumed = markdown_field_value(assignment, "Assumed prior knowledge")
    goal = markdown_field_value(assignment, "Knowledge-transfer goal")
    exception = markdown_field_value(assignment, "Reader-baseline exception authorized by user")
    reason = markdown_field_value(assignment, "Reader-baseline exception reason")
    for label, value in (("reader baseline", reader_baseline), ("assumed prior knowledge", assumed), ("knowledge-transfer goal", goal)):
        if not value:
            findings.append(_finding("reader_contract_field", "Assignment And Boundary", f"Missing nonempty {label}."))
        elif PLACEHOLDER_RE.search(value):
            findings.append(_finding("reader_contract_placeholder", "Assignment And Boundary", f"Unfinished {label}."))
    default_reader = bool(
        re.match(r"^(?:an?\s+)?intelligent\s+(?:non[- ]specialist|general reader)\b", reader_baseline, flags=re.I)
        and not re.search(r"\b(?:experts?|specialists?)\s+only\b|\bdoctoral\b|\b(?:advanced|extensive|graduate[- ]level)\s+(?:knowledge|expertise|background|familiarity)\b", reader_baseline, flags=re.I)
    )
    first_clause = re.split(r"[.;]", assumed, maxsplit=1)[0].strip()
    no_prior = bool(
        re.fullmatch(r"(?:none|no(?:\s+assumed)?(?:\s+prior)?(?:\s+topic)?\s+knowledge|no\s+prior\s+subject\s+familiarity\s+is\s+expected)", first_clause, flags=re.I)
        and not re.search(r"\b(?:except|but|however|although|yet)\b|\bextensive\s+(?:expertise|knowledge)\b", assumed, flags=re.I)
    )
    explicit_exception = exception.strip().lower() == "yes" and words(reason) >= 5
    if not (default_reader and no_prior) and not explicit_exception:
        findings.append(_finding("reader_baseline", "Assignment And Boundary", "Default to an intelligent non-specialist with no assumed topic knowledge unless the user explicitly authorizes and explains an exception."))
    if goal and words(goal) < 8:
        findings.append(_finding("knowledge_transfer_goal", "Assignment And Boundary", "Knowledge-transfer goal is too thin."))


def _check_modules(packet: str, rows: list[dict[str, str]], data: dict, findings: list[Finding]) -> dict[str, dict[str, str]]:
    education = exact_section_body(strip_nonrendered_markdown(packet), "Education Brief", 2)
    if not education:
        findings.append(_finding("education_brief", "writer-research-packet.md", "Packet lacks a reader-facing Education Brief."))
        return {}
    if not rows:
        findings.append(_finding("no_education_modules", "reader-education.csv", "No education modules are registered."))
        return {}

    claim_ids = {row.get("claim_id", "") for row in data.get("claims", [])}
    load_claims = {row.get("claim_id", "") for row in data.get("claims", []) if truthy(row.get("load_bearing"))}
    extraction_pairs = {
        (row.get("claim_id", "").upper(), row.get("source_id", "").upper())
        for row in data.get("extractions", [])
        if row.get("claim_id") and row.get("source_id")
    }
    covered_load_claims: set[str] = set()
    seen_ids: set[str] = set()
    seen_headings: set[str] = set()
    central_modules: dict[str, dict[str, str]] = {}
    required_csv_fields = (
        "reader_questions", "required_background", "required_sequence_or_mechanism",
        "required_evidence_explanation", "required_dispute_or_limit", "required_article_relevance", "packet_heading",
    )
    field_labels = {
        "reader orientation": "Reader orientation",
        "what happened or how it works": "What happened or how it works",
        "evidence guide": "Evidence guide",
        "dispute and limits": "Dispute and limits",
        "why it matters": "Why it matters",
    }

    for index, row in enumerate(rows, start=2):
        location = f"reader-education.csv row {index}"
        module_id = row.get("module_id", "").strip().upper()
        heading = row.get("packet_heading", "").strip()
        central = truthy(row.get("central"))
        if not re.fullmatch(r"M\d+", module_id):
            findings.append(_finding("invalid_module_id", location, f"Invalid module_id: {module_id or '<blank>'}"))
        elif module_id in seen_ids:
            findings.append(_finding("duplicate_module_id", location, f"Duplicate module_id: {module_id}"))
        seen_ids.add(module_id)
        if heading and heading.lower() in seen_headings:
            findings.append(_finding("duplicate_module_heading", location, f"Duplicate packet_heading: {heading}"))
        seen_headings.add(heading.lower())
        if row.get("status", "").strip().lower() not in EDUCATION_STATUS:
            findings.append(_finding("education_status", location, "status must be planned, draft, or complete."))
        if row.get("cold_reader_status", "").strip().lower() not in COLD_STATUS:
            findings.append(_finding("cold_reader_status", location, "cold_reader_status must be pending, pass, or fail."))

        mapped_claims = _split_ids(row.get("claim_ids", ""), "C")
        unknown = sorted(mapped_claims - claim_ids)
        if unknown:
            findings.append(_finding("unknown_education_claim", location, f"Unknown claim_ids: {', '.join(unknown)}"))
        if central:
            for field in required_csv_fields:
                if not row.get(field, "").strip():
                    findings.append(_finding("education_csv_field", location, f"Central module lacks {field}."))
            if not (mapped_claims & load_claims):
                findings.append(_finding("education_claim_mapping", location, "Central module must map to at least one load-bearing claim."))
            covered_load_claims.update(mapped_claims & load_claims)
            if row.get("status", "").strip().lower() != "complete":
                findings.append(_finding("education_incomplete", location, "Central module is not complete."))
            if row.get("cold_reader_status", "").strip().lower() != "pass":
                findings.append(_finding("cold_reader_pending", location, "Central module has not passed the cold-reader test."))
            if words(row.get("cold_reader_notes", "")) < 5:
                findings.append(_finding("cold_reader_notes", location, "Central module lacks substantive cold-reader notes."))
            if module_id:
                central_modules[module_id] = row

        if not heading:
            continue
        module = exact_section_body(education, heading, 3)
        if not module:
            findings.append(_finding("education_module_missing", location, f"Education Brief subsection not found: {heading}"))
            continue
        fields, duplicates = education_module_fields(module)
        for key, label in field_labels.items():
            body = fields.get(key, "")
            if not body:
                findings.append(_finding("education_field_missing", heading, f"Missing field: {label}"))
            elif words(non_table_text(body)) < 25 or not narrative_paragraphs(body):
                findings.append(_finding("education_field_thin", heading, f"{label} needs a substantive connected-prose paragraph; tables, bullets, blockquotes, comments, and code do not count."))
            elif PLACEHOLDER_RE.search(body):
                findings.append(_finding("education_field_placeholder", heading, f"{label} contains placeholder language."))
        for duplicate in sorted(duplicates):
            findings.append(_finding("education_field_duplicate", heading, f"Repeated field: {field_labels.get(duplicate, duplicate)}"))
        if len(narrative_paragraphs(module)) < 5:
            findings.append(_finding("education_module_prose", heading, "Module needs five substantive prose paragraphs, one per required field."))

        evidence = fields.get("evidence guide", "")
        visible_evidence = rendered_visible_text(evidence)
        if not explicit_extraction_pairs(visible_evidence):
            findings.append(_finding("education_evidence_pair", heading, "Evidence guide must show an explicit visible claim/source pair."))
        elif not (explicit_extraction_pairs(visible_evidence) & extraction_pairs):
            findings.append(_finding("education_extraction_pair", heading, "Evidence guide lacks an explicit claim/source pair present in extractions.csv."))
        if human_readable_link_count(evidence) < 1:
            findings.append(_finding("education_source_link", heading, "Evidence guide needs a descriptive HTTP(S) source link."))
        if evidence and not re.search(r"\b(report|study|record|filing|dataset|data|archive|article|document|testimony|statute|docket|biography|speech|treaty|inquiry|assessment|analysis|research|primary|official|transcript|edition)\b", evidence, flags=re.I):
            findings.append(_finding("education_source_type", heading, "Evidence guide does not identify the source type."))
        if evidence and not re.search(r"\b(establish|show|support|document|trace|reconstruct|provide|identify|record|prove|explain|test|preserve|suppl|point)\w*\b", evidence, flags=re.I):
            findings.append(_finding("education_evidence_bridge", heading, "Evidence guide does not explain why the source supports the account."))
        topic_terms = significant_terms(f"{row.get('topic_or_case', '')} {heading}")
        if topic_terms and not (topic_terms & significant_terms(module)):
            findings.append(_finding("education_topic_mismatch", heading, "Module prose does not name its registered topic or case."))

    missing_claims = sorted(load_claims - covered_load_claims)
    if missing_claims:
        findings.append(_finding("education_claim_coverage", "reader-education.csv", f"Load-bearing claims lack a central education module: {', '.join(missing_claims)}"))
    return central_modules


def _check_comparisons(packet: str, central_modules: dict[str, dict[str, str]], findings: list[Finding]) -> None:
    visible_packet = strip_nonrendered_markdown(packet)
    for title, body in section_bodies(visible_packet):
        for header, rows in markdown_table_rows(body) + html_table_rows(body):
            if not is_case_comparison_table(title, header):
                continue
            normalized_header = [re.sub(r"\s+", " ", rendered_visible_text(cell)).strip().lower() for cell in header]
            module_columns = [index for index, value in enumerate(normalized_header) if value in {"module id", "education module"}]
            if len(module_columns) != 1:
                findings.append(_finding("comparison_module_column", title, "Case-comparison table lacks a stable Module ID column."))
            module_column = module_columns[0] if len(module_columns) == 1 else None
            seen: set[str] = set()
            for cells in rows:
                visible_cells = [rendered_visible_text(cell) for cell in cells]
                row_text = " | ".join(visible_cells)
                module_cell = visible_cells[module_column] if module_column is not None and module_column < len(visible_cells) else ""
                match = re.fullmatch(r"M\d+", module_cell.strip(), flags=re.I)
                row_ids = {match.group(0).upper()} if match else set()
                all_ids = {item.upper() for item in re.findall(r"\bM\d+\b", row_text, flags=re.I)}
                valid = row_ids & set(central_modules)
                if len(row_ids) != 1 or len(valid) != 1 or all_ids != row_ids:
                    findings.append(_finding("comparison_module_id", title, f"Comparison row lacks exactly one registered central Module ID: {row_text.strip()}"))
                    continue
                module_id = next(iter(valid))
                if module_id in seen:
                    findings.append(_finding("comparison_duplicate_module", title, f"Comparison table repeats Module ID: {module_id}"))
                seen.add(module_id)
                row = central_modules[module_id]
                module_terms = significant_terms(f"{row.get('topic_or_case', '')} {row.get('packet_heading', '')}")
                if len(module_terms) < 2 or len(module_terms & significant_terms(row_text)) < 2:
                    findings.append(_finding("comparison_subject_mismatch", title, f"Comparison row does not match registered subject for {module_id}: {row_text.strip()}"))


def _check_cold_reader(packet: str, cold: str, rows: list[dict[str, str]], findings: list[Finding]) -> None:
    visible = strip_nonrendered_markdown(cold)
    verdicts = re.findall(r"^\s*VERDICT:\s*(pass|revise|fail)\s*$", visible, flags=re.I | re.M)
    if len(verdicts) != 1 or verdicts[0].lower() != "pass":
        findings.append(_finding("cold_reader_verdict", "cold-reader-evaluation.md", "Cold-reader verdict must be one unambiguous pass."))
    disclosures = re.findall(r"^\s*Other artifacts consulted:\s*([^\n]+?)\s*$", visible, flags=re.I | re.M)
    if len(disclosures) != 1 or disclosures[0].strip().lower() != "no":
        findings.append(_finding("cold_reader_scope", "cold-reader-evaluation.md", "Cold-reader test must use the packet only."))

    artifact_target = (
        r"(?:claims?\.csv|sources?\.csv|extractions?\.csv|reader-education\.csv|manifest\.csv|source-cache|"
        r"argument-outline|adversarial-evaluation|research notes?|source files?|source spreadsheet|"
        r"(?:auxiliary\s+)?evidence ledgers?|another artifact|other artifacts?|outside (?:source|material)|internet|web)"
    )
    consultation_verb = (
        r"(?:open(?:ed)?|consult(?:ed)?|access(?:ed)?|review(?:ed)?|examin(?:e|ed)|read|use(?:d)?|search(?:ed)?|"
        r"brows(?:e|ed)|look(?:ed)?\s+(?:at|up)|check(?:ed)?|cross[- ]check(?:ed)?|reli(?:ed|es?)\s+(?:on|upon)|"
        r"(?:draw|draws|drew|drawn)\s+(?:on|upon|from)|inform(?:ed)?\s+by|verif(?:y|ied))"
    )
    admission = re.compile(
        rf"(?:\b{consultation_verb}\b[\s\S]{{0,120}}\b{artifact_target}\b|\b{artifact_target}\b[\s\S]{{0,120}}\b(?:was\s+|were\s+|also\s+)?{consultation_verb}\b)",
        flags=re.I,
    )
    admission_text = re.sub(r"^\s*Other artifacts consulted:\s*no\s*$", "", cold or "", flags=re.I | re.M)
    named_artifact = re.compile(r"\b(?:claims?\.csv|sources?\.csv|extractions?\.csv|reader-education\.csv|manifest\.csv|source-cache|argument-outline|adversarial-evaluation|source spreadsheet)\b", flags=re.I)
    if admission.search(admission_text) or named_artifact.search(admission_text):
        findings.append(_finding("cold_reader_external_artifact", "cold-reader-evaluation.md", "Evaluation admits consulting material beyond the packet."))
    if PLACEHOLDER_RE.search(visible):
        findings.append(_finding("cold_reader_placeholder", "cold-reader-evaluation.md", "Evaluation contains unfinished placeholder language."))

    expected_header = [
        "module id", "what happened or how it works", "actors and stakes understood", "evidence named and explained",
        "dispute or limit understood", "article relevance understood", "result",
    ]
    results_body = exact_section_body(visible, "Module Results", 2)
    canonical: list[list[list[str]]] = []
    for header, table_rows in markdown_table_rows(results_body):
        if [re.sub(r"\s+", " ", cell.strip().lower()) for cell in header] == expected_header:
            canonical.append(table_rows)
    if len(canonical) != 1:
        findings.append(_finding("cold_reader_table", "cold-reader-evaluation.md", "Evaluation needs exactly one canonical seven-column Module Results table."))
    parsed: dict[str, list[list[str]]] = {}
    for cells in canonical[0] if len(canonical) == 1 else []:
        if cells and re.fullmatch(r"M\d+", cells[0], flags=re.I):
            parsed.setdefault(cells[0].upper(), []).append(cells)

    education = exact_section_body(strip_nonrendered_markdown(packet), "Education Brief", 2)
    for row in rows:
        if not truthy(row.get("central")):
            continue
        module_id = row.get("module_id", "").strip().upper()
        module_rows = parsed.get(module_id, [])
        if len(module_rows) != 1:
            findings.append(_finding("cold_reader_module_row", "cold-reader-evaluation.md", f"Expected exactly one result row for {module_id}."))
            continue
        cells = module_rows[0]
        if len(cells) != 7:
            findings.append(_finding("cold_reader_columns", "cold-reader-evaluation.md", f"Result row for {module_id} needs seven columns."))
            continue
        dimensions = ("sequence/mechanism", "actors/stakes", "evidence explanation", "dispute/limit", "article relevance")
        for dimension, cell in zip(dimensions, cells[1:6]):
            if not re.match(r"^yes\b", cell, flags=re.I):
                findings.append(_finding("cold_reader_dimension", "cold-reader-evaluation.md", f"{module_id} does not affirm {dimension}."))
            content_words = [word.lower() for word in re.findall(r"[A-Za-z][A-Za-z'-]+", cell) if word.lower() not in {"yes", "the", "a", "an", "and", "or", "of", "to", "in", "it", "is"}]
            if words(cell) < 8 or len(set(content_words)) < 6:
                findings.append(_finding("cold_reader_conclusory", "cold-reader-evaluation.md", f"{module_id} gives a conclusory {dimension} answer."))
        if cells[-1].strip().lower() != "pass":
            findings.append(_finding("cold_reader_module_result", "cold-reader-evaluation.md", f"{module_id} is not pass."))
        normalized_cells = [re.sub(r"\W+", " ", re.sub(r"^yes\b", "", cell, flags=re.I)).strip().lower() for cell in cells[1:6]]
        if len(set(normalized_cells)) < 5:
            findings.append(_finding("cold_reader_repetition", "cold-reader-evaluation.md", f"{module_id} repeats generic text across comprehension dimensions."))
        subject_terms = significant_terms(f"{row.get('topic_or_case', '')} {row.get('packet_heading', '')}")
        if subject_terms and not (subject_terms & significant_terms(" ".join(cells[1:6]))):
            findings.append(_finding("cold_reader_subject", "cold-reader-evaluation.md", f"{module_id} does not reconstruct its registered subject."))

        packet_module = exact_section_body(education, row.get("packet_heading", ""), 3)
        packet_fields, _ = education_module_fields(packet_module)
        module_terms = cold_specific_terms(packet_module)
        field_map = (
            ("what happened or how it works", cells[1], "sequence/mechanism"),
            ("reader orientation", cells[2], "actors/stakes"),
            ("evidence guide", cells[3], "evidence explanation"),
            ("dispute and limits", cells[4], "dispute/limit"),
            ("why it matters", cells[5], "article relevance"),
        )
        for field_name, cell, dimension in field_map:
            reference_terms = cold_specific_terms(packet_fields.get(field_name, ""))
            cell_terms = cold_specific_terms(cell)
            field_overlap = reference_terms & cell_terms
            module_overlap = module_terms & cell_terms
            required_field = min(3, len(reference_terms)) if reference_terms else 0
            required_module = min(5, len(module_terms)) if module_terms else 0
            field_generic = required_field and (len(field_overlap) < required_field or len(field_overlap) / max(1, len(cell_terms)) < 0.2)
            module_generic = required_module and (len(module_overlap) < required_module or len(module_overlap) / max(1, len(cell_terms)) < 0.45)
            if field_generic or module_generic:
                findings.append(_finding("cold_reader_generic", "cold-reader-evaluation.md", f"{module_id} gives a generic {dimension} answer rather than reconstructing the packet."))
        if not re.search(r"\b(?:report|study|record|filing|dataset|data|archive|document|testimony|statute|docket|speech|analysis|research|source|text|transcript|law|account)\w*\b|\b[A-Z]{2,}\b", cells[3], flags=re.I):
            findings.append(_finding("cold_reader_evidence", "cold-reader-evaluation.md", f"{module_id} does not name or characterize evidence."))
        if not re.search(r"\b(?:limit|uncertain|unknown|bias|cannot|does not|did not|not |no |alternative|confound|incomplete|dispute|unresolved|missing|counterfactual|caution|weak|remain|contested|partial|only)\w*\b", cells[4], flags=re.I):
            findings.append(_finding("cold_reader_limit", "cold-reader-evaluation.md", f"{module_id} does not explain a dispute or limit."))
        if not re.search(r"\b(?:article|thesis|support|strengthen|weaken|limit|bound|illustrat|show|undercut|establish|distinguish|provide|guardrail|warning|framework|counterexample)\w*\b", cells[5], flags=re.I):
            findings.append(_finding("cold_reader_relevance", "cold-reader-evaluation.md", f"{module_id} does not explain article relevance."))

    contradictions = (
        r"\b(?:packet|module|reader)\s+(?:itself\s+)?(?:fails?\s+to|cannot|does not)\s+(?:explain|name|identify|reconstruct|clarify|teach|establish)\b|"
        r"\b(?:sequence|actors?|evidence explanation|article relevance)\s+(?:is|are|remains?)\s+(?:unclear|missing|insufficient|incomplete|unexplained)\b"
    )
    if re.search(contradictions, visible, flags=re.I):
        findings.append(_finding("cold_reader_contradiction", "cold-reader-evaluation.md", "Evaluation contains a comprehension contradiction."))
    questions = (
        "Can the reader accurately explain every central module without consulting another artifact?",
        "Does the packet define unfamiliar people, institutions, events, laws, and mechanisms before relying on them?",
        "Are tables used as recaps rather than substitutes for explanation?",
    )
    for question in questions:
        values = re.findall(rf"^\s*[-*+]\s*{re.escape(question)}\s*(.+?)\s*$", visible, flags=re.I | re.M)
        if len(values) != 1 or not re.fullmatch(r"yes[.!]?", values[0].strip(), flags=re.I):
            findings.append(_finding("cold_reader_summary", "cold-reader-evaluation.md", f"Summary does not unambiguously affirm: {question}"))
    for label in ("Case comprehension failures", "Required revisions"):
        values = re.findall(rf"^\s*[-*+]\s*{re.escape(label)}[^:\n]*:\s*(.+?)\s*$", visible, flags=re.I | re.M)
        if len(values) != 1 or not re.fullmatch(r"none[.!]?", values[0].strip(), flags=re.I):
            findings.append(_finding("cold_reader_clearance", "cold-reader-evaluation.md", f"{label} is not unambiguously none."))


def check(project: Path, data: dict) -> list[Finding]:
    findings: list[Finding] = []
    header, rows = read_csv(project / "reader-education.csv")
    if (project / "reader-education.csv").exists():
        missing = sorted(set(READER_EDUCATION_HEADERS) - set(header))
        if missing:
            findings.append(_finding("reader_csv_columns", "reader-education.csv", f"Missing columns: {', '.join(missing)}"))
    packet = data.get("packet_text", "")
    cold_path = project / "cold-reader-evaluation.md"
    cold = cold_path.read_text(encoding="utf-8", errors="replace") if cold_path.exists() else ""
    if packet:
        _check_reader_contract(packet, findings)
        central_modules = _check_modules(packet, rows, data, findings)
        _check_comparisons(packet, central_modules, findings)
    if cold:
        _check_cold_reader(packet, cold, rows, findings)
    data["reader_education"] = rows
    return findings
