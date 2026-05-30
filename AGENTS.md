# Repository Instructions

This repository contains Codex research skills. When working in this repository, treat research-quality failures as workflow failures, not style issues.

For broad, controversial, historical, scientific, economic, policy, or current-events research questions:

1. Use the installed `world-research` skill.
2. Create or update an Evidence Audit Project under `research/<topic-slug>/` unless the user explicitly asks for a quick chat-only answer.
3. Use `skills/world-research/scripts/init_evidence_audit.py research/<topic-slug> --question "<question>"` for new projects.
4. Center the work in `writer-research-packet.md`, with `sources.csv`, `extractions.csv`, `source-cache/manifest.csv`, and `adversarial-evaluation.md` as the default supporting machinery. Use `appendices/` only for genuinely long legal, data, source, or case readouts.
5. Do not synthesize before extraction. Load-bearing claims must have evidence rows or be explicitly marked unauditable/incomplete.
6. Judge sources by data, methods, reproducibility, and fit-to-claim before prestige or stigma. A dissident source with better evidence beats a prestigious source with weak evidence.
7. For follow-ups, keep the same project folder but create distinct update-scoped files so readers do not need to parse changed originals. Add a dated update file under `updates/` plus slugged artifacts such as `<follow-up-slug>-writer-research-packet.md`, `<follow-up-slug>-sources.csv`, `<follow-up-slug>-extractions.csv`, `<follow-up-slug>-source-cache-manifest.csv`, and `<follow-up-slug>-adversarial-evaluation.md` when substantial. Do not append free-floating essay chapters or silently mutate earlier analysis unless the user explicitly asks for a consolidated revision.
8. Run `skills/world-research/scripts/research_quality_gate.py <project-dir>` before final delivery.
9. Revise until the quality gate passes. If it fails, do not summarize the project as complete.
10. Do not use "first-pass" disclaimers for central evidence. Complete the central audit inside a narrowed boundary or mark the project incomplete.
11. A project without retraceable links to documents, datasets, filings, reports, source pages, extraction rows, and source-cache manifest entries is a failed draft.
12. Treat article angles as conclusions that require evidence. The packet must include research readiness, writing readiness, live viewpoints, angle readiness, claims to avoid, So What, reporting plan, and hostile editor review before delivery.

The user should only need to name the topic. The research workflow is automatic.
