from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from research_gate.common import find_refs, safe_project_path, sha256_file  # noqa: E402
from research_gate.runner import evaluate_project  # noqa: E402
from research_gate.schema import (  # noqa: E402
    CLAIM_HEADERS,
    EXTRACTION_HEADERS,
    MANIFEST_HEADERS,
    READER_EDUCATION_HEADERS,
    SOURCE_HEADERS,
)


def write_csv(path: Path, headers: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def valid_claim() -> dict[str, str]:
    return {
        "claim_id": "C1",
        "claim_text": "The audited series shows the reported total increased during the defined period.",
        "claim_type": "factual",
        "load_bearing": "yes",
        "evidence_needed": "Underlying row-level series with definitions, denominator, and revision history.",
        "status": "supported",
        "confidence": "high",
        "confidence_basis": "The row-level calculation reproduces exactly and the documented denominator remains stable across all relevant periods.",
        "counterevidence_status": "searched",
        "what_would_change": "A corrected dataset version or documentation showing that the denominator changed materially.",
        "notes": "",
    }


def valid_source() -> dict[str, str]:
    return {
        "source_id": "S1",
        "title": "Independent Row-Level Series",
        "author_or_org": "Small Independent Researcher",
        "date": "2026-01-03",
        "url_or_citation": "https://example.org/data/series.csv",
        "document_type": "independent_analysis",
        "source_role": "load_bearing",
        "access_depth": "dataset_inspected",
        "audit_scope": "Rows, codebook, category definitions, denominator, revision notes, and published calculation were inspected.",
        "provenance": "The producer publishes the original row-level observations, collection dates, and transformation script used for the series.",
        "underlying_data_access": "Full row-level CSV and transformation script were available.",
        "method_transparency": "Collection, cleaning, classification, aggregation, and revision rules are documented and independently checkable.",
        "reproducibility": "The central total reproduced exactly from the supplied rows and script.",
        "incentives_funding": "No institutional prestige is assumed; the producer sells related consulting and discloses that commercial incentive.",
        "limitations": "Coverage excludes two jurisdictions and the conclusion is limited to the documented population and period.",
        "freshness_as_of": "2026-01-05",
        "centrality": "load_bearing",
        "eligible_for_claims": "yes",
        "notes": "Low institutional prestige does not reduce the weight of reproducible evidence.",
    }


def valid_extraction() -> dict[str, str]:
    return {
        "evidence_id": "E1",
        "claim_id": "C1",
        "source_id": "S1",
        "proposition": "The defined total increased across the audited period using a stable denominator.",
        "evidence_locator": "Table 2, rows 14 through 22, archived CSV revision dated 2026-01-03",
        "raw_evidence": "Summing the nine documented rows produces 14,218 units in 2025 versus 11,904 units in 2024.",
        "provenance_notes": "Rows derive from dated local records and retain identifiers linking each observation to its originating record.",
        "measurement_definition": "One unit equals one completed record; the denominator includes every participating jurisdiction reporting in both years.",
        "method_notes": "The producer deduplicates by record identifier, excludes withdrawn records, and sums completed records after the annual cutoff.",
        "reproduction_status": "reproduced",
        "reproduction_notes": "The published annual totals reproduced exactly from the downloaded row-level file.",
        "assumptions_or_exclusions": "Two nonparticipating jurisdictions are excluded consistently from both years and from the stated population.",
        "missingness": "No missing identifiers appeared among included records; geographic coverage remains incomplete.",
        "alternative_explanations": "Reporting compliance could increase observed totals without an equivalent increase in underlying activity.",
        "counterevidence": "Revision histories and comparison records were checked; neither showed a denominator change during the period.",
        "claim_fit": "The evidence supports the limited reported-total claim but does not establish why the underlying activity increased.",
        "status": "supports",
        "confidence": "high",
        "what_would_change": "A revised codebook, duplicate records, or newly documented changes in reporting participation would reduce confidence.",
    }


def valid_reader_module() -> dict[str, str]:
    return {
        "module_id": "M1",
        "topic_or_case": "Independent row-level series",
        "claim_ids": "C1",
        "central": "yes",
        "reader_questions": "How is the reported total produced, what does it measure, and what can it establish?",
        "required_background": "The participating jurisdictions, record system, denominator, identifiers, and annual cutoff.",
        "required_sequence_or_mechanism": "How local records become deduplicated annual totals and how the periods are compared.",
        "required_evidence_explanation": "The named dataset, codebook, row-level reproduction, and why those records support the bounded result.",
        "required_dispute_or_limit": "Incomplete geographic coverage and reporting compliance as an alternative explanation.",
        "required_article_relevance": "Why the result supports a descriptive article but not a causal claim.",
        "packet_heading": "M1 — Independent row-level series",
        "status": "complete",
        "cold_reader_status": "pass",
        "cold_reader_notes": "The reader reconstructed the record flow, evidence, limitation, and article boundary from the packet alone.",
    }


def cold_reader_text() -> str:
    return """# Cold-Reader Evaluation

VERDICT: pass

Other artifacts consulted: no

Reader education and knowledge transfer passed. Case comprehension passed. Tables used as recaps.

## Module Results

| Module ID | What happened or how it works | Actors and stakes understood | Evidence named and explained | Dispute or limit understood | Article relevance understood | Result |
|---|---|---|---|---|---|---|
| M1 | Yes — local records enter the series, stable identifiers permit deduplication, and the annual cutoff produces totals for comparison across the two periods. | Yes — participating jurisdictions supply completed records, while readers need the stable denominator and exclusions to understand the measured stakes. | Yes — the named row-level dataset and codebook document the observations, and the reproduced calculation supports the bounded reported-total account. | Yes — incomplete geographic coverage and changing reporting compliance remain alternative explanations, so the evidence does not establish why activity increased. | Yes — the module supports an article about the measured descriptive increase while warning that the thesis cannot convert it into a causal result. | pass |

## Reader Education And Knowledge Transfer Verdict

- Can the reader accurately explain every central module without consulting another artifact? yes
- Does the packet define unfamiliar people, institutions, events, laws, and mechanisms before relying on them? yes
- Are tables used as recaps rather than substitutes for explanation? yes
- Case comprehension failures: none
- Required revisions: none
"""


def packet_text(extra: str = "") -> str:
    return f"""# Writer Research Packet

## Assignment And Boundary

The assignment tests a defined factual series inside the documented population and period. This is not a full restatement of unrelated evidence.

- Reader baseline: intelligent non-specialist
- Assumed prior knowledge: none
- Knowledge-transfer goal: explain the record system, calculation, evidence, limitations, and article relevance without requiring another artifact

## Bottom Line

The row-level evidence supports the limited reported-total claim (C1, S1).

## How The System Works

Local records enter a published row-level series. Stable identifiers permit deduplication, while a documented annual cutoff determines inclusion. The result measures completed records in participating jurisdictions rather than every possible jurisdiction.

## Education Brief

### M1 — Independent row-level series

**Reader orientation.** Participating jurisdictions submit completed local records to an independent producer, which publishes a row-level series. The important stakes are the defined population, stable identifiers, annual cutoff, and denominator used to compare the two reported periods.

**What happened or how it works.** Local records enter the published series, stable identifiers allow the producer to remove duplicates, and the documented annual cutoff assigns records to a year. Summing the included rows produces comparable totals for 2024 and 2025.

**Evidence guide.** The [Independent Row-Level Series](https://example.org/data/series.csv) is the inspected dataset and codebook. Its rows document the observations, identifiers, and annual totals, while reproducing the published calculation explains why the record supports the bounded descriptive result (C1, S1).

**Dispute and limits.** Two jurisdictions do not participate, so the dataset cannot describe the entire country. Reporting compliance could also raise the observed total without an equal increase in underlying activity, leaving a serious alternative explanation for the change.

**Why it matters.** The reproduced series supports an article explaining a measured increase inside the documented population. It also places a firm guardrail around the thesis: the descriptive comparison cannot establish a behavioral cause or represent excluded jurisdictions.

## Evidence By Claim

C1 is supported by the reproduced calculation from S1. The result is descriptive and does not by itself establish the cause of the increase.

## Method And Data Audits

S1 publishes row-level observations, a codebook, and transformation rules. The calculation was independently reproduced. The principal limitation is incomplete geographic coverage, which confines the conclusion to participating jurisdictions.

## Contradictions And Competing Explanations

The audit checked revision histories, denominator changes, duplication, and reporting compliance. Greater reporting compliance remains a plausible alternative explanation for part of the observed increase.

## What Cannot Be Established

The descriptive series cannot determine why activity increased. No causal conclusion is drawn.

## Article Directions

A defensible article can explain what the series measures, reproduce the increase, and show why the result should not be converted into a causal claim.

## Claims To Avoid

Avoid claiming that the measured increase proves a behavioral cause or represents jurisdictions outside the documented population.

## Optional Original Reporting

No optional reporting is required to answer the stated desk-research question.

## Completion Statement

Research readiness: strong. Writing readiness: ready.

No further Codex research pass is required for the stated boundary.

{extra}
"""


class ProjectFixture:
    def __init__(self, root: Path):
        self.root = root
        (root / "source-cache").mkdir(parents=True)
        (root / "appendices").mkdir()
        (root / "updates").mkdir()
        (root / "project.json").write_text(json.dumps({
            "schema_version": "2.0",
            "skill_version": "2.1.0",
            "gate_version": "2.1.0",
            "project_id": "test-project",
            "assignment_type": "original",
            "parent_project": None,
            "question": "Did the defined total increase during the audited period?",
            "boundary": "The documented population, stable annual denominator, and published row-level series for 2024 through 2025.",
            "created_at": "2026-01-05",
            "as_of": "2026-01-05",
            "completed_at": "2026-01-05",
            "status": "complete",
            "research_readiness": "strong",
            "writing_readiness": "ready",
        }, indent=2), encoding="utf-8")
        (root / "work-state.json").write_text(json.dumps({
            "source_universe_complete": True,
            "central_tasks": ["Reproduce the published total and test denominator stability."],
            "unresolved_central_tasks": [],
            "contradiction_searches": [{"claim_id": "C1", "status": "complete"}],
            "method_audits_complete": True,
            "adversarial_review": {"status": "pass", "blocking_issues": [], "resolved_issues": []},
            "optional_original_reporting": [],
        }, indent=2), encoding="utf-8")
        (root / "writer-research-packet.md").write_text(packet_text(), encoding="utf-8")
        (root / "cold-reader-evaluation.md").write_text(cold_reader_text(), encoding="utf-8")
        write_csv(root / "claims.csv", CLAIM_HEADERS, [valid_claim()])
        write_csv(root / "sources.csv", SOURCE_HEADERS, [valid_source()])
        write_csv(root / "extractions.csv", EXTRACTION_HEADERS, [valid_extraction()])
        write_csv(root / "reader-education.csv", READER_EDUCATION_HEADERS, [valid_reader_module()])
        write_csv(root / "source-cache" / "manifest.csv", MANIFEST_HEADERS, [{
            "source_id": "S1",
            "original_url": "https://example.org/data/series.csv",
            "capture_state": "url_only",
            "local_path": "",
            "archive_url": "",
            "captured_at": "",
            "sha256": "",
            "mime_type": "",
            "reason_not_captured": "The remote test fixture has no distributable source bytes in this repository.",
            "copyright_notes": "Test metadata only.",
        }])

    def read_rows(self, name: str) -> list[dict[str, str]]:
        with (self.root / name).open(encoding="utf-8", newline="") as handle:
            return [dict(row) for row in csv.DictReader(handle)]

    def write_rows(self, name: str, headers: tuple[str, ...], rows: list[dict[str, str]]) -> None:
        write_csv(self.root / name, headers, rows)


class ResearchGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name) / "project"
        self.fixture = ProjectFixture(self.project)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self) -> set[str]:
        return {item["code"] for item in evaluate_project(self.project)["findings"] if item["severity"] == "FAIL"}

    def test_valid_low_prestige_reproducible_project_passes(self) -> None:
        report = evaluate_project(self.project)
        self.assertEqual("pass", report["status"], report["findings"])

    def test_cli_writes_generated_gate_report(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "research_quality_gate.py"), str(self.project)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        report = json.loads((self.project / "gate-report.json").read_text(encoding="utf-8"))
        self.assertEqual("pass", report["status"])
        self.assertEqual("2.1.0", report["gate_version"])

    def test_empty_tables_fail_directly(self) -> None:
        self.fixture.write_rows("claims.csv", CLAIM_HEADERS, [])
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, [])
        self.fixture.write_rows("extractions.csv", EXTRACTION_HEADERS, [])
        self.assertTrue({"no_claims", "no_sources", "no_extractions"}.issubset(self.codes()))

    def test_invalid_url_fails(self) -> None:
        rows = self.fixture.read_rows("sources.csv")
        rows[0]["url_or_citation"] = "not-a-valid-url"
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, rows)
        self.assertIn("invalid_source_citation", self.codes())

    def test_generic_filler_evidence_fails(self) -> None:
        rows = self.fixture.read_rows("extractions.csv")
        rows[0]["raw_evidence"] = "Generic filler words that do not preserve any actual evidence proposition for this claim."
        self.fixture.write_rows("extractions.csv", EXTRACTION_HEADERS, rows)
        self.assertIn("placeholder_evidence", self.codes())

    def test_url_cannot_masquerade_as_local_cache(self) -> None:
        rows = self.fixture.read_rows("source-cache/manifest.csv")
        rows[0]["capture_state"] = "local"
        rows[0]["local_path"] = "https://example.org/data/series.csv"
        rows[0]["sha256"] = "a" * 64
        self.fixture.write_rows("source-cache/manifest.csv", MANIFEST_HEADERS, rows)
        self.assertIn("url_not_cache", self.codes())

    def test_local_cache_hash_is_verified(self) -> None:
        cached = self.project / "source-cache" / "source.txt"
        cached.write_text("preserved evidence bytes", encoding="utf-8")
        rows = self.fixture.read_rows("source-cache/manifest.csv")
        rows[0].update({
            "capture_state": "local",
            "local_path": "source-cache/source.txt",
            "captured_at": "2026-01-05",
            "sha256": "0" * 64,
            "mime_type": "text/plain",
            "reason_not_captured": "",
        })
        self.fixture.write_rows("source-cache/manifest.csv", MANIFEST_HEADERS, rows)
        self.assertIn("cache_hash_mismatch", self.codes())
        rows[0]["sha256"] = sha256_file(cached)
        self.fixture.write_rows("source-cache/manifest.csv", MANIFEST_HEADERS, rows)
        self.assertNotIn("cache_hash_mismatch", self.codes())

    def test_honest_not_full_wording_does_not_fail(self) -> None:
        text = (self.project / "writer-research-packet.md").read_text(encoding="utf-8")
        (self.project / "writer-research-packet.md").write_text(text + "\nThis is not a full biography of the producer.\n", encoding="utf-8")
        self.assertEqual("pass", evaluate_project(self.project)["status"])

    def test_user_facing_request_for_another_pass_fails(self) -> None:
        text = (self.project / "writer-research-packet.md").read_text(encoding="utf-8")
        (self.project / "writer-research-packet.md").write_text(text + "\nAnother Codex research pass is needed to finish the evidence.\n", encoding="utf-8")
        self.assertIn("user_facing_deferral", self.codes())

    def test_citation_ranges_expand_correctly(self) -> None:
        self.assertEqual({"S1", "S2", "S3", "S4"}, find_refs("Sources S1-S4", "S"))
        self.assertEqual({"C2", "C3", "C4"}, find_refs("Claims C2–4", "C"))
        self.assertEqual({"S8", "S9"}, find_refs("S8—S9", "S"))

    def test_project_paths_cannot_escape_project_root(self) -> None:
        self.assertIsNone(safe_project_path(self.project, "../../outside.txt"))
        self.assertEqual((self.project / "source-cache" / "source.txt").resolve(), safe_project_path(self.project, "source-cache/source.txt"))

    def test_peer_reviewed_abstract_cannot_carry_central_claim(self) -> None:
        rows = self.fixture.read_rows("sources.csv")
        rows[0]["document_type"] = "scientific_study"
        rows[0]["access_depth"] = "abstract_only"
        rows[0]["centrality"] = "context"
        rows[0]["eligible_for_claims"] = "no"
        rows[0]["notes"] = "Peer reviewed in a prestigious journal."
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, rows)
        self.assertIn("shallow_central_source", self.codes())

    def test_source_used_for_load_bearing_claim_requires_manifest_even_if_mislabeled_context(self) -> None:
        sources = self.fixture.read_rows("sources.csv")
        sources[0]["centrality"] = "context"
        sources[0]["eligible_for_claims"] = "no"
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, sources)
        self.fixture.write_rows("source-cache/manifest.csv", MANIFEST_HEADERS, [])
        self.assertIn("missing_manifest", self.codes())

    def test_press_release_alone_cannot_prove_implementation(self) -> None:
        claims = self.fixture.read_rows("claims.csv")
        claims[0]["claim_type"] = "implementation"
        self.fixture.write_rows("claims.csv", CLAIM_HEADERS, claims)
        sources = self.fixture.read_rows("sources.csv")
        sources[0]["document_type"] = "press_release"
        sources[0]["access_depth"] = "full_document"
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, sources)
        self.assertIn("press_release_implementation", self.codes())

    def test_genuinely_unavailable_evidence_can_finish_indeterminate(self) -> None:
        claims = self.fixture.read_rows("claims.csv")
        claims[0].update({
            "status": "indeterminate",
            "confidence": "indeterminate",
            "confidence_basis": "The decisive record is sealed and every available collateral record leaves both competing explanations consistent with the evidence.",
            "what_would_change": "Unsealing the identified record or producing an authenticated equivalent contemporaneous record would distinguish the alternatives.",
        })
        self.fixture.write_rows("claims.csv", CLAIM_HEADERS, claims)
        sources = self.fixture.read_rows("sources.csv")
        sources[0].update({
            "document_type": "primary_record",
            "access_depth": "unavailable",
            "centrality": "context",
            "eligible_for_claims": "no",
            "audit_scope": "The public docket and collateral records were inspected for evidence identifying the sealed record's contents.",
        })
        self.fixture.write_rows("sources.csv", SOURCE_HEADERS, sources)
        extractions = self.fixture.read_rows("extractions.csv")
        extractions[0].update({
            "raw_evidence": "The public docket identifies the sealed exhibit but provides no description capable of distinguishing the competing factual accounts.",
            "status": "indeterminate",
            "confidence": "indeterminate",
            "reproduction_status": "not_applicable",
            "reproduction_notes": "No numerical or classification result exists to reproduce for this unavailable record.",
            "claim_fit": "The accessible record establishes the evidence gap, not the truth of either competing factual account.",
        })
        self.fixture.write_rows("extractions.csv", EXTRACTION_HEADERS, extractions)
        self.assertEqual("pass", evaluate_project(self.project)["status"], evaluate_project(self.project)["findings"])


if __name__ == "__main__":
    unittest.main()
