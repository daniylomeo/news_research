# News Research Skills

Codex skills for high-quality research into current events, history, politics, policy, science-in-policy disputes, institutions, and public controversies.

The goal of this repo is to make serious research behavior automatic: source discipline, named viewpoints, method checks, funder disclosure, contradiction searches, and a fail-closed quality gate before delivery.

## Skills

### `world-research`

Use for broad research briefings and dossiers. It requires:

- holistic issue models, not narrow answer-only summaries;
- mechanism explanations for systems, institutions, money flows, incentives, and tradeoffs;
- historical context with real depth when history matters;
- primary and official sources where available;
- source cards for major evidence;
- NGO, nonprofit, think-tank, advocacy, rating, and index audits;
- named debate/commentary maps, not generic "both sides" placeholders;
- hard counterexamples and adversarial self-review;
- automatic dossier mode and preflight quality gate for broad or controversial topics.

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

`skills/world-research/scripts/research_quality_gate.py` checks dossiers for common failure modes:

- deferred central research;
- weak third-party aggregators used for central claims;
- generic viewpoint camps;
- vague funder summaries;
- unsupported rubrics;
- bullet-heavy uncited sections;
- missing core sections.

Run it with:

```powershell
python .\skills\world-research\scripts\research_quality_gate.py .\research\example-dossier.md
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

The user should only need to name the topic. For broad, controversial, historical, scientific, policy, or current-events research, the skills should automatically choose the appropriate depth, build the dossier when needed, audit sources, map real viewpoints, and run the preflight gate before delivery.
