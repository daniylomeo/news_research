# Repository Instructions

This repository contains Codex research skills. Treat research-quality failures as workflow failures, not stylistic shortcomings.

For broad, controversial, historical, scientific, economic, policy, institutional, or current-events research:

1. Use the installed `world-research` skill and read its routed references relevant to the assignment.
2. Create a version 2 Evidence Audit Project under `research/<topic-slug>/` with `skills/world-research/scripts/init_evidence_audit.py` unless the user explicitly requests a quick chat-only answer.
3. Treat every source skeptically. Prestige, peer review, official status, mainstream acceptance, dissident status, ideology, or nonprofit status never determines the verdict. Evaluate provenance, raw evidence, measurement, method, reproducibility, uncertainty, counterevidence, and claim fit.
4. Audit evidence claim by claim. A source may be usable for a date or reported total while unusable for implementation, motive, causation, or generalization.
5. Extract load-bearing evidence before settled synthesis. Inspect underlying primary records, data, full studies, filings, transcripts, and relevant rebuttals when reasonably obtainable.
6. Complete all obtainable central desk research within the current task. Failed gates and hostile reviews trigger more internal research and revision, not delivery of a "first pass" or a request for another Codex pass.
7. Use `indeterminate` or `unauditable` only when the necessary record is genuinely unavailable, future, proprietary, sealed, destroyed, nonexistent, or incapable of distinguishing the alternatives. Explain the evidentiary consequence.
8. Keep optional original reporting limited to interviews, FOIA/public-record requests, site visits, proprietary data, expert consultation, original analysis, and future evidence beyond a complete desk-research answer.
9. Run `skills/world-research/scripts/research_quality_gate.py <project-dir>` and revise until it reports no failures. The script generates `gate-report.json`; never handwrite or self-certify a pass.
10. Return one completed `writer-research-packet.md` for one user assignment. Create an update only for a genuinely new user follow-up, new evidence, or a changed boundary. Name it for the question, not `second-pass` or similar process language.
11. Preserve all pre-v2 research artifacts. Migrate only into a new copy with `migrate_v1_project.py`; do not silently rewrite earlier work or claim that migration certifies its conclusions.

The user should only need to name the topic. Internal acquisition, extraction, contradiction, adversarial review, and revision loops are automatic.
