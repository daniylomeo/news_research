#!/usr/bin/env python3
"""Run the world-research v2 structural and evidence-integrity gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from research_gate import SCHEMA_VERSION, evaluate_project


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="Version 2 Evidence Audit Project directory")
    parser.add_argument("--no-write", action="store_true", help="Do not write gate-report.json")
    parser.add_argument("--json", action="store_true", help="Print the full JSON report")
    args = parser.parse_args()

    project = Path(args.project_dir)
    if not project.is_dir():
        parser.error(f"project directory does not exist: {project}")
    if not (project / "project.json").exists():
        print(
            f"FAIL: project uses a pre-v{SCHEMA_VERSION} layout; preserve it and migrate a copy with "
            "migrate_v1_project.py before using the v2 gate."
        )
        return 1

    report = evaluate_project(project)
    if not args.no_write:
        (project / "gate-report.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for finding in report["findings"]:
            print(f"{finding['severity']}: {finding['code']}: {finding['location']}: {finding['message']}")
        summary = report["summary"]
        print(f"Summary: {summary['failures']} failure(s), {summary['warnings']} warning(s)")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
