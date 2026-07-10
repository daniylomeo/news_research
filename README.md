# Evidence-Driven Writer Research Skills

Codex skills for article research into current events, history, politics, policy, economics, institutions, scientific disputes, and public controversies.

The central rule is source-neutral skepticism: every source is a claim container, never an authority. Peer review, official status, institutional prestige, ideology, and outsider status may identify failure modes to inspect but never determine the conclusion. Verdicts come from provenance, raw evidence, measurement, method, reproducibility, uncertainty, counterevidence, and fit between evidence and claim.

## One-Assignment Contract

One user assignment produces one completed writer research packet. Codex performs source acquisition, extraction, methodology review, contradiction search, adversarial review, and revision internally until the project passes. A new update is created only for a user-requested follow-up, genuinely new evidence, or a changed research boundary.

An `indeterminate` result can be complete when the necessary evidence is genuinely unavailable. Ordinary obtainable desk research cannot be deferred to another pass.

## Skills

- `world-research`: full Evidence Audit Projects and writer research packets.
- `fact-check-ledger`: atomic claim verification with claim-specific evidence and method audits.
- `viewpoint-map`: evidence-tested maps of real debates, narratives, incentives, and policy theories.

## Version 2 Project

Create a project:

```powershell
python .\skills\world-research\scripts\init_evidence_audit.py .\research\example-topic --question "Does X cause Y?"
```

Core artifacts:

- `project.json`: schema version, assignment, boundary, timestamps, and status.
- `writer-research-packet.md`: coherent writer-facing investigation.
- `claims.csv`: load-bearing claims, verdicts, confidence bases, contradiction status, and revision conditions.
- `sources.csv`: claim-specific provenance, access, data, method, incentives, and limitations.
- `extractions.csv`: raw evidence and the full claim-evidence-method chain.
- `work-state.json`: internal research, contradiction, method-audit, and adversarial-review state.
- `source-cache/manifest.csv`: truthful preservation state and hashes for local files.
- `gate-report.json`: generated gate result.

Run the gate:

```powershell
python .\skills\world-research\scripts\research_quality_gate.py .\research\example-topic
```

The gate separates deterministic structural integrity from evidence-integrity heuristics. It verifies references, IDs, schema, URLs, cache files and hashes, central-source depth, method and reproduction fields, contradiction completion, and one-assignment completion. It does not pretend that code can prove a substantive conclusion true.

## Follow-Ups

Create an update only after a genuinely new user question:

```powershell
python .\skills\world-research\scripts\init_update_pass.py .\research\example-topic --slug financial-angle --question "Now investigate the financing mechanism"
```

Updates live under `updates/<date>-<topic>/`. Numbered `second-pass` naming is rejected.

## Preserving Version 1 Projects

Existing projects are historical records and should not be silently rewritten. Migrate a copy for review:

```powershell
python .\skills\world-research\scripts\migrate_v1_project.py .\research\old-topic $env:TEMP\old-topic-v2
python .\skills\world-research\scripts\research_quality_gate.py $env:TEMP\old-topic-v2
```

Migration transfers source and extraction material but deliberately leaves completion uncertified until v2 methodology, contradiction, provenance, and reproduction gaps are resolved.

## Tests

The gate uses the Python standard library. Run its adversarial regression suite with:

```powershell
python -m unittest discover -s .\skills\world-research\tests -v
```

The tests cover invalid citations, meaningless filler, false URL caches, hash verification, citation ranges, shallow peer-reviewed evidence, press-release implementation claims, low-prestige reproducible evidence, and completed indeterminate findings.

## Skill Validation

Codex's external skill validator requires PyYAML. Install the optional development dependency, then validate:

```powershell
python -m pip install -r .\requirements-dev.txt
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\world-research
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\fact-check-ledger
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\viewpoint-map
```

## Installation

Copy the skill folders into the Codex skills directory so new tasks can discover them:

```powershell
$dest = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item .\skills\world-research "$dest\world-research" -Recurse -Force
Copy-Item .\skills\fact-check-ledger "$dest\fact-check-ledger" -Recurse -Force
Copy-Item .\skills\viewpoint-map "$dest\viewpoint-map" -Recurse -Force
```
