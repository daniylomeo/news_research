from __future__ import annotations

from dataclasses import asdict, dataclass


SCHEMA_VERSION = "2.0"
GATE_VERSION = "2.1.0"

REQUIRED_FILES = (
    "project.json",
    "writer-research-packet.md",
    "claims.csv",
    "sources.csv",
    "extractions.csv",
    "reader-education.csv",
    "cold-reader-evaluation.md",
    "work-state.json",
    "source-cache/manifest.csv",
)

CLAIM_HEADERS = (
    "claim_id",
    "claim_text",
    "claim_type",
    "load_bearing",
    "evidence_needed",
    "status",
    "confidence",
    "confidence_basis",
    "counterevidence_status",
    "what_would_change",
    "notes",
)

SOURCE_HEADERS = (
    "source_id",
    "title",
    "author_or_org",
    "date",
    "url_or_citation",
    "document_type",
    "source_role",
    "access_depth",
    "audit_scope",
    "provenance",
    "underlying_data_access",
    "method_transparency",
    "reproducibility",
    "incentives_funding",
    "limitations",
    "freshness_as_of",
    "centrality",
    "eligible_for_claims",
    "notes",
)

EXTRACTION_HEADERS = (
    "evidence_id",
    "claim_id",
    "source_id",
    "proposition",
    "evidence_locator",
    "raw_evidence",
    "provenance_notes",
    "measurement_definition",
    "method_notes",
    "reproduction_status",
    "reproduction_notes",
    "assumptions_or_exclusions",
    "missingness",
    "alternative_explanations",
    "counterevidence",
    "claim_fit",
    "status",
    "confidence",
    "what_would_change",
)

MANIFEST_HEADERS = (
    "source_id",
    "original_url",
    "capture_state",
    "local_path",
    "archive_url",
    "captured_at",
    "sha256",
    "mime_type",
    "reason_not_captured",
    "copyright_notes",
)

READER_EDUCATION_HEADERS = (
    "module_id",
    "topic_or_case",
    "claim_ids",
    "central",
    "reader_questions",
    "required_background",
    "required_sequence_or_mechanism",
    "required_evidence_explanation",
    "required_dispute_or_limit",
    "required_article_relevance",
    "packet_heading",
    "status",
    "cold_reader_status",
    "cold_reader_notes",
)

REQUIRED_PACKET_SECTIONS = (
    "Assignment And Boundary",
    "Bottom Line",
    "How The System Works",
    "Education Brief",
    "Evidence By Claim",
    "Method And Data Audits",
    "Contradictions And Competing Explanations",
    "What Cannot Be Established",
    "Article Directions",
    "Claims To Avoid",
    "Optional Original Reporting",
    "Completion Statement",
)

CLAIM_STATUSES = {
    "supported",
    "mostly_supported",
    "mixed",
    "weakened",
    "contradicted",
    "indeterminate",
    "unauditable",
    "context",
    "pending",
}

EXTRACTION_STATUSES = {
    "supports",
    "weakens",
    "mixed",
    "contradicts",
    "context",
    "indeterminate",
    "unauditable",
    "pending",
}

CONFIDENCE_VALUES = {"high", "moderate", "low", "indeterminate", "pending"}
COUNTEREVIDENCE_VALUES = {"searched", "found", "none_found", "not_applicable", "pending"}
REPRODUCTION_VALUES = {
    "reproduced",
    "partially_reproduced",
    "checked_not_reproduced",
    "not_possible",
    "not_applicable",
    "pending",
}
ACCESS_DEPTH_VALUES = {
    "full_document",
    "relevant_sections",
    "dataset_inspected",
    "filing_inspected",
    "docket_inspected",
    "transcript_inspected",
    "audio_video_inspected",
    "partial_document",
    "abstract_only",
    "snippet_only",
    "metadata_only",
    "unavailable",
}
CAPTURE_STATES = {"local", "external_archive", "url_only", "metadata_only", "unavailable"}

METHOD_DOCUMENT_TYPES = {
    "scientific_study",
    "quantitative_study",
    "dataset",
    "poll",
    "model",
    "index",
    "government_report",
    "institutional_report",
    "advocacy_report",
    "industry_report",
    "financial_filing",
    "independent_analysis",
}

REPRODUCTION_DOCUMENT_TYPES = {
    "scientific_study",
    "quantitative_study",
    "dataset",
    "poll",
    "model",
    "index",
    "independent_analysis",
}

OPTIONAL_REPORTING_TYPES = {
    "interview",
    "foia_or_records_request",
    "site_visit",
    "proprietary_data",
    "expert_consultation",
    "original_analysis",
    "future_event",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    location: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
