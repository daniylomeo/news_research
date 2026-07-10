from __future__ import annotations

import re
from pathlib import Path

from .common import safe_project_path, sha256_file, valid_web_url, words
from .schema import CAPTURE_STATES, Finding


def check(project: Path, data: dict) -> list[Finding]:
    findings: list[Finding] = []
    for index, row in enumerate(data.get("manifest", []), start=2):
        location = f"source-cache/manifest.csv row {index}"
        state = row.get("capture_state", "").strip().lower()
        if state not in CAPTURE_STATES:
            findings.append(Finding("FAIL", "capture_state", location, f"Invalid capture_state: {state or '<blank>'}"))
            continue
        if row.get("original_url") and not valid_web_url(row.get("original_url", "")):
            findings.append(Finding("FAIL", "invalid_original_url", location, "original_url is not a valid HTTP(S) URL."))
        if state == "local":
            local_path = row.get("local_path", "").strip()
            if re.match(r"https?://", local_path, flags=re.I):
                findings.append(Finding("FAIL", "url_not_cache", location, "A URL cannot be recorded as a local cache path."))
                continue
            target = safe_project_path(project, local_path) if local_path else None
            if target is None or not target.is_file():
                findings.append(Finding("FAIL", "missing_cache_file", location, f"Local cached file does not exist inside the project: {local_path or '<blank>'}"))
                continue
            expected = row.get("sha256", "").strip().lower()
            if not re.fullmatch(r"[0-9a-f]{64}", expected):
                findings.append(Finding("FAIL", "cache_hash", location, "Local cache requires a 64-character SHA-256 hash."))
            elif sha256_file(target) != expected:
                findings.append(Finding("FAIL", "cache_hash_mismatch", location, "Cached file SHA-256 does not match the manifest."))
            if not row.get("captured_at") or not row.get("mime_type"):
                findings.append(Finding("FAIL", "cache_metadata", location, "Local cache requires captured_at and mime_type."))
        elif state == "external_archive":
            if not valid_web_url(row.get("archive_url", "")):
                findings.append(Finding("FAIL", "archive_url", location, "External archive state requires a valid archive_url."))
            if not row.get("captured_at"):
                findings.append(Finding("FAIL", "archive_date", location, "External archive state requires captured_at."))
        elif state in {"url_only", "metadata_only", "unavailable"}:
            if words(row.get("reason_not_captured", "")) < 8:
                findings.append(Finding("FAIL", "capture_reason", location, "Non-captured source needs a concrete reason of at least eight words."))
            if row.get("local_path") or row.get("sha256"):
                findings.append(Finding("FAIL", "false_cache_metadata", location, "Non-local source cannot carry local_path or sha256 values."))
    return findings
