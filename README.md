# News Research Skills

Codex skills for high-quality research into current events, history, politics, policy, science-in-policy disputes, institutions, and public controversies.

The goal of this repo is to make serious research behavior automatic: Evidence Audit Project creation for broad topics, source-neutral claim mapping, extraction before synthesis, method and data checks, funder/incentive disclosure, contradiction searches, and a fail-closed quality gate before delivery.

## Skills

### `world-research`

Use for broad research briefings and Evidence Audit Projects. It requires:

- holistic issue models, not narrow answer-only summaries;
- broad claim intake before conclusions;
- source-neutral evidence evaluation, where prestige and stigma affect scrutiny but not truth;
- extraction tables for load-bearing claims before synthesis;
- one coherent `research-brief.md` as the main reader-facing dossier, with small supporting tables rather than file sprawl;
- mechanism explanations for systems, institutions, money flows, incentives, and tradeoffs;
- historical context with real depth when history matters;
- primary and official sources where available;
- source intake and evidence extraction for major evidence;
- source-cache manifest records for load-bearing sources;
- NGO, nonprofit, think-tank, advocacy, rating, and index audits;
- economic and ideological lens checks for policy/economic questions;
- current, issue-specific economists or active institutions for economic lens claims rather than school summaries from model memory;
- named debate/commentary maps, not generic "both sides" placeholders;
- case/data audits and sensitivity tests where implementation or coding matters;
- hard counterexamples and adversarial self-review;
- automatic Evidence Audit Project creation and preflight quality gate for broad or controversial topics.

### `fact-check-ledger`

Use for claim-by-claim verification. It requires:

- atomic claim extraction;
- primary-source-first verification;
- study/data methodology readouts;
- document/product readouts for central reports and filings;
- funding/conflict notes for NGOs, nonprofits, think tanks, advocacy groups, and scientific studies;
- symmetric standards for contested labels;
- clear confidence levels and audit trails.

### `viewpoint-map`

Use for mapping debates, narratives, ideologies, and commentary. It requires:

- real named actors, institutions, texts, movements, or schools of thought;
- steelmanning before critique;
- source/funding/incentive notes;
- claim checks for major factual assertions;
- non-mainstream and dissident views where relevant;
- serious policy tradeoff analysis instead of toy proposals.

## Quality Gate

`skills/world-research/scripts/research_quality_gate.py` checks Evidence Audit Projects, and still supports legacy markdown dossiers, for common failure modes:

- deferred central research;
- synthesis before extraction;
- missing unified brief, source table, extraction table, source-cache manifest, or adversarial evaluation;
- load-bearing claims without extraction rows;
- source prestige or stigma used as a substitute for data/methods;
- weak third-party aggregators used for central claims;
- generic viewpoint camps;
- vague funder summaries;
- unsupported rubrics;
- bullet-heavy uncited sections;
- missing core sections.

Run it with:

```powershell
python .\skills\world-research\scripts\init_evidence_audit.py .\research\example-topic --question "Does X outweigh Y?"
python .\skills\world-research\scripts\research_quality_gate.py .\research\example-topic
```

The gate is heuristic, not a substitute for judgment, but failures should block delivery unless the work is explicitly marked incomplete.

## Validation

Each skill should validate with Codex's skill validator:

```powershell
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\world-research
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\fact-check-ledger
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .\skills\viewpoint-map
```

## Installation

Codex does not automatically discover skills just because they exist inside a repository. To make these available in brand-new chats, install them into your Codex skills directory:

```powershell
$dest = "$env:USERPROFILE\.codex\skills"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item .\skills\world-research "$dest\world-research" -Recurse -Force
Copy-Item .\skills\fact-check-ledger "$dest\fact-check-ledger" -Recurse -Force
Copy-Item .\skills\viewpoint-map "$dest\viewpoint-map" -Recurse -Force
```

After installation, start a new Codex chat. The skills should appear in the available skills list and trigger automatically for matching research tasks.

## Design Principle

The user should only need to name the topic. For broad, controversial, historical, scientific, economic, policy, or current-events research, the skills should automatically create an Evidence Audit Project when a writable workspace exists, build a coherent `research-brief.md`, map claims from every relevant viewpoint, extract evidence before synthesis, audit sources by data and method rather than prestige, preserve source access in `source-cache/manifest.csv`, run the preflight gate before delivery, then summarize and link the project artifacts. If no project folder is created, the agent should explain why.

This repo also includes `AGENTS.md` so new Codex chats opened inside the repository receive the same high-level research workflow instruction even before a skill body is loaded.
