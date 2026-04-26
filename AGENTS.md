# Repository Instructions

This repository contains Codex research skills. When working in this repository, treat research-quality failures as workflow failures, not style issues.

For broad, controversial, historical, scientific, policy, or current-events research questions:

1. Use the installed `world-research` skill.
2. Create or update a markdown dossier under `research/<topic-slug>.md` unless the user explicitly asks for a quick chat-only answer.
3. Include source cards, study/data readouts, concrete case/project audits when implementation matters, named viewpoint analysis, a claim ledger, policy counterarguments where relevant, audit trail, adversarial self-review, and a `Quality Gate Result` section.
4. Run `skills/world-research/scripts/research_quality_gate.py <dossier-path>` before final delivery.
5. Revise until the quality gate passes. If it fails, do not summarize the dossier as complete.
6. Do not use "first-pass" disclaimers for central evidence. Complete the central research inside a narrowed boundary or mark the dossier incomplete.
7. A dossier without retraceable links to documents, datasets, filings, reports, and source pages is a failed draft.

The user should only need to name the topic. The research workflow is automatic.
