from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return list(reader.fieldnames or []), [dict(row) for row in reader]
    except (OSError, csv.Error):
        return [], []


def truthy(value: str | bool | int | None) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value != 0
    return str(value or "").strip().lower() in {"yes", "true", "1"}


def words(value: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", value or "", flags=re.UNICODE))


def normalized(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", (value or "").lower())).strip()


def valid_web_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc) and "." in parsed.netloc


def valid_iso_date(value: str) -> bool:
    try:
        date.fromisoformat((value or "").strip())
    except ValueError:
        return False
    return True


def url_or_substantive_citation(value: str) -> bool:
    value = (value or "").strip()
    if valid_web_url(value):
        return True
    if "://" in value or value.lower().startswith(("www.", "doi:")):
        return False
    return words(value) >= 5 and bool(re.search(r"\b(19|20)\d{2}\b|\bdoi\b|\bvol\.?\b|\bno\.?\b", value, flags=re.I))


def headings(text: str) -> set[str]:
    return {match.strip().lower() for match in re.findall(r"^#{1,6}\s+(.+?)\s*$", text or "", flags=re.M)}


def section_body(text: str, title: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(title)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text or "",
        flags=re.I | re.M | re.S,
    )
    return match.group(1).strip() if match else ""


def find_refs(text: str, prefix: str) -> set[str]:
    """Return IDs and expand forms such as S1-S4, S1–4, or C2—C3."""
    prefix = re.escape(prefix.upper())
    out: set[str] = set()
    range_re = re.compile(rf"\b{prefix}(\d+)\s*[-–—]\s*(?:{prefix})?(\d+)\b", flags=re.I)
    spans: list[tuple[int, int]] = []
    for match in range_re.finditer(text or ""):
        start, end = int(match.group(1)), int(match.group(2))
        if abs(end - start) <= 500:
            low, high = sorted((start, end))
            out.update(f"{prefix}{number}" for number in range(low, high + 1))
        spans.append(match.span())
    scrubbed = list(text or "")
    for start, end in spans:
        scrubbed[start:end] = " " * (end - start)
    for match in re.finditer(rf"\b{prefix}(\d+)\b", "".join(scrubbed), flags=re.I):
        out.add(f"{prefix}{int(match.group(1))}")
    return out


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_project_path(project: Path, relative: str) -> Path | None:
    try:
        root = project.resolve()
        target = (project / relative).resolve()
        target.relative_to(root)
    except (OSError, ValueError):
        return None
    return target
