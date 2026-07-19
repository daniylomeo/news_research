from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL / "scripts"
sys.path.insert(0, str(SCRIPTS))

from init_evidence_audit import initialize_project  # noqa: E402
from research_gate.runner import evaluate_project  # noqa: E402


class CliWorkflowTests(unittest.TestCase):
    def test_initializer_creates_versioned_incomplete_project(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "new-project"
            initialize_project(project, "What does the evidence establish?", "A bounded test of initializer behavior and completion safeguards.")
            metadata = json.loads((project / "project.json").read_text(encoding="utf-8"))
            self.assertEqual("2.0", metadata["schema_version"])
            self.assertEqual("2.1.0", metadata["gate_version"])
            self.assertEqual("researching", metadata["status"])
            self.assertTrue((project / "reader-education.csv").exists())
            self.assertTrue((project / "cold-reader-evaluation.md").exists())
            codes = {item["code"] for item in evaluate_project(project)["findings"]}
            self.assertTrue({"no_claims", "no_sources", "no_extractions"}.issubset(codes))
            self.assertIn("project_not_complete", codes)
            self.assertNotIn("unknown_packet_claim", codes)
            self.assertNotIn("unknown_packet_source", codes)

    def test_migration_creates_review_required_copy_without_mutating_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "v1"
            output = root / "v2"
            (source / "source-cache").mkdir(parents=True)
            packet = "# Writer Research Packet\n\nQuestion: Did the event occur?\n"
            (source / "writer-research-packet.md").write_text(packet, encoding="utf-8")
            with (source / "sources.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "source_id", "title", "author_or_org", "date", "url_or_citation", "source_type",
                    "claims_made", "data_access", "source_access", "centrality", "evidence_limit",
                    "funding_ownership_incentives", "eligible_for_central_evidence", "notes",
                ])
                writer.writeheader()
                writer.writerow({
                    "source_id": "S1", "title": "Official record", "author_or_org": "Agency",
                    "date": "2025-01-01", "url_or_citation": "https://example.org/record",
                    "source_type": "official record", "claims_made": "The event occurred on the recorded date.",
                    "data_access": "full", "source_access": "full_document", "centrality": "central",
                    "evidence_limit": "Does not establish the cause of the event.",
                    "funding_ownership_incentives": "Agency produced the record for administration.",
                    "eligible_for_central_evidence": "yes", "notes": "",
                })
            with (source / "extractions.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "claim_id", "source_id", "exact_claim", "evidence_location", "extracted_data_or_quote",
                    "method_notes", "assumptions_or_exclusions", "uncertainty_or_error", "our_critique",
                    "status", "confidence", "follow_up_needed",
                ])
                writer.writeheader()
                writer.writerow({
                    "claim_id": "C1", "source_id": "S1", "exact_claim": "The event occurred.",
                    "evidence_location": "Record section 2", "extracted_data_or_quote": "The dated record states that the event occurred on January 1, 2025.",
                    "method_notes": "Direct administrative record; no causal method is present.",
                    "assumptions_or_exclusions": "Assumes the record was entered contemporaneously.",
                    "uncertainty_or_error": "No independent event record is included.",
                    "our_critique": "Usable for the recorded event, not its cause.", "status": "supports",
                    "confidence": "moderate", "follow_up_needed": "Check an independent contemporaneous record.",
                })
            with (source / "source-cache" / "manifest.csv").open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=[
                    "source_id", "path_or_url", "cached_status", "cache_reason", "access_date",
                    "centrality", "copyright_limitations",
                ])
                writer.writeheader()
                writer.writerow({
                    "source_id": "S1", "path_or_url": "https://example.org/record", "cached_status": "cached",
                    "cache_reason": "Stable URL only", "access_date": "2026-01-01", "centrality": "central",
                    "copyright_limitations": "None stated",
                })

            before = (source / "sources.csv").read_bytes()
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "migrate_v1_project.py"), str(source), str(output)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertEqual(before, (source / "sources.csv").read_bytes())
            metadata = json.loads((output / "project.json").read_text(encoding="utf-8"))
            migration = json.loads((output / "migration-report.json").read_text(encoding="utf-8"))
            self.assertEqual("migrating", metadata["status"])
            self.assertFalse(migration["automatic_completion_certified"])
            with (output / "source-cache" / "manifest.csv").open(encoding="utf-8") as handle:
                migrated_manifest = next(csv.DictReader(handle))
            self.assertEqual("url_only", migrated_manifest["capture_state"])

    def test_follow_up_uses_question_slug_and_preserves_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / "project"
            initialize_project(project, "What does the original record establish?", "The original bounded assignment and its available record.")
            original = (project / "project.json").read_bytes()
            bad = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "init_update_pass.py"),
                    str(project),
                    "--slug",
                    "second-pass",
                    "--question",
                    "Do more research",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, bad.returncode)
            good = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "init_update_pass.py"),
                    str(project),
                    "--slug",
                    "financial-angle",
                    "--question",
                    "Now investigate the financing mechanism",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, good.returncode, good.stderr)
            updates = list((project / "updates").glob("*-financial-angle/project.json"))
            self.assertEqual(1, len(updates))
            update_metadata = json.loads(updates[0].read_text(encoding="utf-8"))
            self.assertEqual("user_follow_up", update_metadata["assignment_type"])
            self.assertEqual(original, (project / "project.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
