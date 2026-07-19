# Version 2 Project Schema

Use the initializer-generated headers exactly. Schema and gate version are `2.0` and `2.1.0`.

## project.json

Required fields:

- `schema_version`, `skill_version`, `gate_version`, and `project_id`.
- `assignment_type`: `original` or `user_follow_up`.
- `parent_project`: null for original work; parent path for a follow-up.
- `question` and substantive `boundary`.
- `created_at`, `as_of`, and `completed_at`.
- `status`: `researching`, `migrating`, or `complete`.
- `research_readiness`: `incomplete`, `usable`, or `strong`.
- `writing_readiness`: `weak`, `explanatory_only`, `promising`, or `ready`.

Set `status=complete` only after all central evidence work is complete. A final gate rejects any other status.

## work-state.json

- `source_universe_complete`: Boolean.
- `central_tasks`: list of research tasks required by the assignment.
- `unresolved_central_tasks`: must be empty at completion.
- `contradiction_searches`: claim-specific search records.
- `method_audits_complete`: Boolean.
- `adversarial_review.status`: `pending`, `revise`, or `pass`.
- `adversarial_review.blocking_issues`: must be empty at completion.
- `adversarial_review.resolved_issues`: repaired criticisms and affected artifacts.
- `optional_original_reporting`: objects containing `type`, `description`, `why_it_matters`, `how_it_could_change`, and `beyond_desk_research: true`.

Allowed optional-reporting types: `interview`, `foia_or_records_request`, `site_visit`, `proprietary_data`, `expert_consultation`, `original_analysis`, and `future_event`.

## claims.csv

Each row represents one stable claim:

- `claim_id`: unique `C` plus integer.
- `claim_text`, `claim_type`, and `load_bearing`.
- `evidence_needed`.
- `status`: `supported`, `mostly_supported`, `mixed`, `weakened`, `contradicted`, `indeterminate`, `unauditable`, `context`, or `pending`.
- `confidence`: `high`, `moderate`, `low`, `indeterminate`, or `pending`.
- `confidence_basis`: evidence-based explanation; never prestige-based.
- `counterevidence_status`: `searched`, `found`, `none_found`, `not_applicable`, or `pending`.
- `what_would_change` and `notes`.

Every load-bearing claim needs extraction rows. A complete project cannot contain pending load-bearing claims or contradiction searches.

## sources.csv

Each row identifies a source and the exact scope audited:

- `source_id`: unique `S` plus integer.
- `title`, `author_or_org`, `date`, and `url_or_citation`.
- `document_type` and `source_role`.
- `access_depth`: `full_document`, `relevant_sections`, `dataset_inspected`, `filing_inspected`, `docket_inspected`, `transcript_inspected`, `audio_video_inspected`, `partial_document`, `abstract_only`, `snippet_only`, `metadata_only`, or `unavailable`.
- `audit_scope`, `provenance`, and `underlying_data_access`.
- `method_transparency` and `reproducibility`.
- `incentives_funding` and `limitations`.
- `freshness_as_of`, `centrality`, `eligible_for_claims`, and `notes`.

A source used by a load-bearing claim is treated as central regardless of how its row is labeled. Shallow access cannot carry a central verdict. `unavailable` is permitted only for a completed indeterminate or unauditable finding.

## extractions.csv

Each row connects one claim to one inspected evidence item:

- `evidence_id`: unique `E` plus integer.
- `claim_id` and `source_id`.
- `proposition`, `evidence_locator`, and `raw_evidence`.
- `provenance_notes` and `measurement_definition`.
- `method_notes`.
- `reproduction_status`: `reproduced`, `partially_reproduced`, `checked_not_reproduced`, `not_possible`, `not_applicable`, or `pending`.
- `reproduction_notes`.
- `assumptions_or_exclusions`, `missingness`, `alternative_explanations`, and `counterevidence`.
- `claim_fit`.
- `status`: `supports`, `weakens`, `mixed`, `contradicts`, `context`, `indeterminate`, `unauditable`, or `pending`.
- `confidence` and `what_would_change`.

Use raw evidence and pinpoint locations, not generic source summaries. Quantitative and classification evidence requires a reproduction attempt or a concrete explanation of why reproduction was impossible.

## source-cache/manifest.csv

- `source_id` and `original_url`.
- `capture_state`: `local`, `external_archive`, `url_only`, `metadata_only`, or `unavailable`.
- `local_path`, `archive_url`, and `captured_at`.
- `sha256` and `mime_type` for local files.
- `reason_not_captured` for non-local states.
- `copyright_notes`.

A URL is never a local cache. Local paths must resolve inside the project and hashes must match.

## reader-education.csv

Each row registers one teaching module with a unique `module_id`, exact `packet_heading`, `topic_or_case`, mapped `claim_ids`, centrality, reader questions, required background, sequence or mechanism, evidence explanation, dispute or limit, article relevance, completion status, cold-reader status, and substantive cold-reader notes. Every load-bearing claim must be covered by at least one central module. Split modules when several subjects would otherwise be compressed into one row.

## cold-reader-evaluation.md

This is a packet-only comprehension test. It must disclose `Other artifacts consulted: no`, contain exactly one substantive result row for every central module, clear all five comprehension dimensions, report no failures or revisions, and end with one unambiguous `VERDICT: pass`. The evaluator may not consult claims, sources, extractions, cache files, notes, or another evaluation.

## Completion order

1. Finish claim, source, extraction, contradiction, method, and adversarial work.
2. Empty `unresolved_central_tasks` and mark the source universe and method audits complete.
3. Set adversarial review to pass with no blockers.
4. Write the final packet and completion sentence.
5. Run the packet-only cold-reader test and revise the packet until every central module passes.
6. Set project readiness, `completed_at`, and `status=complete`.
7. Run the gate and use the generated `gate-report.json`.
