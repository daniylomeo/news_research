from __future__ import annotations

import csv
import tempfile
import textwrap
import unittest
from pathlib import Path

from test_research_gate import ProjectFixture, cold_reader_text, packet_text

from research_gate.reader_checks import (
    markdown_table_rows,
    narrative_paragraphs,
    rendered_visible_text,
)
from research_gate.runner import evaluate_project
from research_gate.schema import READER_EDUCATION_HEADERS


class ReaderEducationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.fixture = ProjectFixture(self.project)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self) -> set[str]:
        return {
            item["code"]
            for item in evaluate_project(self.project)["findings"]
            if item["severity"] == "FAIL"
        }

    def packet(self) -> str:
        return (self.project / "writer-research-packet.md").read_text(encoding="utf-8")

    def write_packet(self, value: str) -> None:
        (self.project / "writer-research-packet.md").write_text(value, encoding="utf-8")

    def write_cold(self, value: str) -> None:
        (self.project / "cold-reader-evaluation.md").write_text(value, encoding="utf-8")

    def reader_rows(self) -> list[dict[str, str]]:
        with (self.project / "reader-education.csv").open(encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

    def write_reader_rows(self, rows: list[dict[str, str]]) -> None:
        with (self.project / "reader-education.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=READER_EDUCATION_HEADERS)
            writer.writeheader()
            writer.writerows(rows)

    def test_complete_packet_only_education_contract_passes(self) -> None:
        report = evaluate_project(self.project)
        self.assertEqual("pass", report["status"], report["findings"])

    def test_table_and_bullet_content_do_not_count_as_teaching_prose(self) -> None:
        table = """Field | Explanation
--- | ---
Reader orientation | This table cell contains many words about actors, records, institutions, evidence, uncertainty, mechanisms, and consequences, but it remains compressed tabular content rather than connected teaching prose.
"""
        self.assertEqual([], narrative_paragraphs(table))
        packet = self.packet().replace(
            "Participating jurisdictions submit completed local records to an independent producer, which publishes a row-level series. The important stakes are the defined population, stable identifiers, annual cutoff, and denominator used to compare the two reported periods.",
            table,
        )
        self.write_packet(packet)
        self.assertTrue({"education_field_missing", "education_field_thin", "education_module_prose"} & self.codes())

    def test_fenced_indented_and_commented_modules_are_invisible(self) -> None:
        packet = self.packet()
        start = packet.index("**Reader orientation.**")
        end = packet.index("\n## Evidence By Claim")
        module = packet[start:end]
        for hidden in (f"```markdown\n{module}\n```", textwrap.indent(module, "    "), f"<!--\n{module}\n-->"):
            with self.subTest(container=hidden[:8]):
                self.write_packet(packet[:start] + hidden + packet[end:])
                self.assertIn("education_module_missing", self.codes())

    def test_hidden_url_and_comment_ids_do_not_satisfy_extraction_pair(self) -> None:
        packet = self.packet()
        for hidden in (
            "[verification target](https://example.org/C1,S1)",
            "[verification target](https://example.org/path_(audit)/C1,S1)",
            "<!-- (C1, S1) -->",
        ):
            with self.subTest(hidden=hidden):
                self.write_packet(packet.replace("(C1, S1)", hidden))
                self.assertIn("education_evidence_pair", self.codes())

    def test_visible_link_label_may_carry_extraction_pair(self) -> None:
        self.write_packet(self.packet().replace("(C1, S1)", "[(C1, S1)](https://example.org/audit)"))
        self.assertNotIn("education_evidence_pair", self.codes())
        self.assertIn("C1, S1", rendered_visible_text("[(C1, S1)](https://example.org/audit)"))

    def test_crossed_citations_do_not_create_a_pair(self) -> None:
        self.write_packet(self.packet().replace("(C1, S1)", "(C1, S2); (C2, S1)"))
        self.assertIn("education_extraction_pair", self.codes())

    def test_zero_knowledge_reversals_fail(self) -> None:
        packet = self.packet()
        replacements = (
            ("Reader baseline: intelligent non-specialist", "Reader baseline: not an intelligent non-specialist; experts only"),
            ("Assumed prior knowledge: none", "Assumed prior knowledge: none except doctoral expertise"),
            ("Assumed prior knowledge: none", "Assumed prior knowledge: no restriction; extensive specialist expertise required"),
        )
        for old, new in replacements:
            with self.subTest(new=new):
                self.write_packet(packet.replace(old, new))
                self.assertIn("reader_baseline", self.codes())

    def test_plus_commonmark_and_semantic_zero_knowledge_wording_pass(self) -> None:
        packet = self.packet()
        packet = packet.replace("- Reader baseline: intelligent non-specialist", "+ **Reader baseline**: an intelligent general reader who may know nothing about the subject")
        packet = packet.replace("- Assumed prior knowledge: none", "+ **Assumed prior knowledge**: no prior subject familiarity is expected")
        packet = packet.replace("- Knowledge-transfer goal:", "+ **Knowledge-transfer goal**:")
        self.write_packet(packet)
        self.assertNotIn("reader_baseline", self.codes())

    def test_load_bearing_claim_requires_central_module_coverage(self) -> None:
        rows = self.reader_rows()
        rows[0]["claim_ids"] = ""
        self.write_reader_rows(rows)
        self.assertTrue({"education_claim_mapping", "education_claim_coverage"}.issubset(self.codes()))

    def test_heading_prefix_cannot_reuse_another_module(self) -> None:
        self.write_packet(self.packet().replace("### M1 —", "### M10 —", 1))
        self.assertIn("education_module_missing", self.codes())

    def test_case_comparison_requires_registered_module_column(self) -> None:
        comparison = """
### Historical parallels

Jurisdiction | Route | Consequence
--- | --- | ---
Xylophonia | Petition | Capture
"""
        self.write_packet(self.packet() + comparison)
        self.assertIn("comparison_module_column", self.codes())

    def test_cross_country_measure_table_is_not_case_comparison(self) -> None:
        comparison = """
### Cross-country comparability result

Jurisdiction | Official measure | Illustrative official figure | Why a ratio would mislead
--- | --- | --- | ---
United States | Registered representatives | 527 | The measure includes lawful activity
"""
        self.write_packet(self.packet() + comparison)
        self.assertNotIn("comparison_module_column", self.codes())

    def test_module_id_must_be_exact_and_in_designated_column(self) -> None:
        for bad in (" | Independent row-level series | M1", "<!-- M1 --> | Independent row-level series | Descriptive", "M1-ish | Independent row-level series | Descriptive"):
            with self.subTest(row=bad):
                comparison = f"""
### Historical comparison

Module ID | Case | Outcome
--- | --- | ---
{bad}
"""
                self.write_packet(self.packet() + comparison)
                self.assertIn("comparison_module_id", self.codes())

    def test_cold_reader_external_artifact_admissions_fail(self) -> None:
        admissions = (
            "Sources.csv was consulted afterward to confirm a detail.",
            "The evaluator opened\nsources.csv on the next line.",
            "The evaluator relied upon sources.csv.",
            "The evaluation was informed by sources.csv.",
            "The evaluator drew on an auxiliary evidence ledger before writing the result.",
        )
        for admission in admissions:
            with self.subTest(admission=admission):
                self.write_cold(cold_reader_text() + "\n" + admission + "\n")
                self.assertIn("cold_reader_external_artifact", self.codes())

    def test_cold_reader_copied_terms_diluted_by_filler_fail(self) -> None:
        original = "local records enter the series, stable identifiers permit deduplication, and the annual cutoff produces totals for comparison across the two periods."
        replacements = (
            "records, identifiers, and cutoff are repeated while polished wording supplies generic confident assurance without reconstructing the mechanism.",
            "records, identifiers, cutoff, and totals appear inside abstract commentary whose fluent style offers vague confidence and empty certainty.",
            "records, identifiers, cutoff, totals, and periods sit inside elegant but empty rhetoric full of vague confidence, smooth cadence, decorative abstraction, and hollow enthusiasm.",
        )
        for replacement in replacements:
            with self.subTest(replacement=replacement):
                self.write_cold(cold_reader_text().replace(original, replacement))
                self.assertIn("cold_reader_generic", self.codes())

    def test_qualified_yes_and_none_cannot_hide_failures(self) -> None:
        variants = (
            cold_reader_text().replace("Case comprehension failures: none", "Case comprehension failures: none except M1 remains weak"),
            cold_reader_text().replace("Required revisions: none", "Required revisions: none except rewrite the mechanism"),
            cold_reader_text().replace("Are tables used as recaps rather than substitutes for explanation? yes", "Are tables used as recaps rather than substitutes for explanation? yes, except one table"),
        )
        for value in variants:
            with self.subTest(last=value.splitlines()[-1]):
                self.write_cold(value)
                self.assertTrue({"cold_reader_clearance", "cold_reader_summary"} & self.codes())

    def test_cold_reader_must_cover_each_central_module_once(self) -> None:
        value = cold_reader_text()
        table = markdown_table_rows(value)
        self.assertTrue(table)
        self.write_cold(value.replace("| M1 |", "| M10 |", 1))
        self.assertIn("cold_reader_module_row", self.codes())


if __name__ == "__main__":
    unittest.main()
