#!/usr/bin/env python3
"""Heuristic quality gate for world-research dossiers.

This is not a substitute for judgment. It catches common failure modes:
summary filler, generic viewpoint maps, weak aggregators, unsupported rubrics,
and deferred central work.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


HARD_PATTERNS = [
    (r"\bneeds deeper review\b", "central work appears deferred"),
    (r"\bdeeper (second )?pass\b", "core research may be deferred to a later pass"),
    (r"\bfuture work\b", "possible deferred central work"),
    (r"\bnot covered in full\b", "boundary may be too broad for the conclusion"),
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
    "Source",
    "Viewpoint",
    "Claim",
    "Audit Trail",
]

LINK_REQUIRED_SECTIONS = [
    "Source Cards",
    "Study and Data Readouts",
    "Case or Project Audits",
    "Viewpoint and Commentary Map",
    "Claim Ledger",
    "Audit Trail",
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


def add_pattern_findings(text: str, patterns: list[tuple[str, str]], severity: str, findings: list[tuple[str, str, str]]) -> None:
    for pattern, message in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            line = text.count("\n", 0, match.start()) + 1
            findings.append((severity, f"line {line}", message))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Markdown dossier to check")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    findings: list[tuple[str, str, str]] = []
    total_links = count_links(text)

    if total_links == 0:
        findings.append(("FAIL", "document", "dossier contains no retraceable URLs or markdown links"))
    elif total_links < 8:
        findings.append(("WARN", "document", f"dossier has only {total_links} link(s); source trail may be too thin"))

    for required in REQUIRED_SECTIONS:
        if required.lower() not in lower:
            findings.append(("FAIL", "document", f"missing expected section containing '{required}'"))

    add_pattern_findings(text, HARD_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, WEAK_SOURCE_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, GENERIC_VIEWPOINT_PATTERNS, "FAIL", findings)
    add_pattern_findings(text, VAGUE_FUNDER_PATTERNS, "FAIL", findings)

    for title, body in section_bodies(text):
        words = prose_words(body)
        bullets = bullet_lines(body)
        links = count_links(body)
        if any(title.lower().startswith(name.lower()) for name in LINK_REQUIRED_SECTIONS) and links == 0:
            findings.append(("FAIL", title, "section requires retraceable links to sources/records"))
        if title.lower().startswith("source cards"):
            source_card_markers = len(re.findall(r"^\*\*.+?\*\*", body, flags=re.MULTILINE))
            if source_card_markers >= 3 and links < max(3, source_card_markers // 2):
                findings.append(("FAIL", title, "source cards name sources without enough direct links"))
            if "what parts" not in body.lower() and "parts read" not in body.lower() and "inspected" not in body.lower():
                findings.append(("FAIL", title, "source cards do not say what parts were read or inspected"))
        if title.lower().startswith("study and data readouts") and not re.search(r"\b(method|methodology|scenario|sample|model|uncertainty|confidence interval|limitation)\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "study/data readouts lack method or uncertainty discussion"))
        if title.lower().startswith("case or project audits") and not re.search(r"\b(permit|tariff|order|filing|docket|zoning|minutes|agreement|audit|regulator|commission)\b", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "case/project audit lacks primary-record indicators"))
        if title.lower().startswith("viewpoint") and re.search(r"represented by groups such as|represented by hyperscalers|represented by energy-policy commentators|represented by .*advocates", body, flags=re.IGNORECASE):
            findings.append(("FAIL", title, "viewpoint representatives are too generic; name specific actors/institutions/texts"))
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
