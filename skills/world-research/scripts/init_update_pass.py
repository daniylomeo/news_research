#!/usr/bin/env python3
"""Initialize a user-requested v2 follow-up without mutating the original project."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from init_evidence_audit import initialize_project
from research_gate.schema import SCHEMA_VERSION


SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_dir", help="Existing v2 research project")
    parser.add_argument("--slug", required=True, help="Follow-up topic slug, not process language")
    parser.add_argument("--question", required=True, help="Genuinely new user follow-up question")
    parser.add_argument("--boundary", default="", help="Optional follow-up boundary")
    args = parser.parse_args()

    project = Path(args.project_dir)
    metadata_path = project / "project.json"
    if not metadata_path.exists():
        parser.error("project is not a v2 Evidence Audit Project")
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        parser.error("project.json is malformed")
    if metadata.get("schema_version") != SCHEMA_VERSION:
        parser.error(f"project schema is not {SCHEMA_VERSION}")

    slug = args.slug.strip().lower()
    if not SLUG_RE.fullmatch(slug):
        parser.error("--slug must contain lowercase letters, digits, and hyphens")
    if re.search(r"(?:^|-)(?:first|second|third|fourth|proper|repair)-pass(?:-|$)", slug):
        parser.error("name the update for the new question, not a numbered research pass")

    update_dir = project / "updates" / f"{date.today().isoformat()}-{slug}"
    initialize_project(
        update_dir,
        args.question,
        args.boundary,
        parent_project=str(project.resolve()),
        assignment_type="user_follow_up",
    )
    print(f"Initialized user-requested follow-up: {update_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
