from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import cache_checks, citation_checks, editorial_checks, evidence_checks, structural_checks
from .schema import GATE_VERSION, SCHEMA_VERSION, Finding


def evaluate_project(project: Path | str) -> dict:
    project = Path(project)
    structural, data = structural_checks.check(project)
    findings: list[Finding] = list(structural)
    findings.extend(citation_checks.check(project, data))
    findings.extend(cache_checks.check(project, data))
    findings.extend(evidence_checks.check(project, data))
    findings.extend(editorial_checks.check(project, data))
    failures = sum(item.severity == "FAIL" for item in findings)
    warnings = sum(item.severity == "WARN" for item in findings)
    return {
        "schema_version": SCHEMA_VERSION,
        "gate_version": GATE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": str(project.resolve()),
        "status": "pass" if failures == 0 else "fail",
        "summary": {"failures": failures, "warnings": warnings},
        "findings": [item.to_dict() for item in findings],
    }
