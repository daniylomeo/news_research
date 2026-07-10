---
name: fact-check-ledger
description: Verify claims, statistics, quotations, speeches, articles, social posts, disputed history, causal assertions, classifications, and institutional statements. Use when Codex should decompose claims, inspect primary and underlying evidence, audit methodology without trusting source prestige, search for contradictions, and return claim-specific verdicts with retraceable evidence and completed evidentiary limits.
---

# Fact Check Ledger

Verify claims through audited evidence, not source reputation.

## Rules

- Treat every source as a claim container. Do not accept or reject evidence because it is peer reviewed, official, mainstream, partisan, ideological, dissident, nonprofit, or prestigious.
- Evaluate a source only for the claim and scope under review. A record may establish a date while failing to establish motive or causation.
- Break compound assertions into atomic factual, causal, classificatory, legal, quantitative, and opinion components.
- Inspect primary or underlying material when reasonably available: original documents, data, codebooks, filings, transcripts, recordings, full studies, and implementation records.
- Read central studies beyond abstracts. Audit sample, unit, measurement, model or design, effect size, uncertainty, missingness, confounders, robustness, conflicts, replication, and claim fit.
- Reconstruct important numerical claims: denominator, time window, jurisdiction, classification rule, exclusions, and sensitivity.
- Trace important quotations to the original recording, transcript, or document and inspect context.
- Search for the strongest contradiction, narrowing context, and plausible alternative explanation before ruling.
- Apply classification standards symmetrically. Define labels such as fraud, coup, genocide, fascist, recession, or corruption before applying them.
- Finish the check in the current task. If decisive evidence is genuinely unavailable, return a completed `indeterminate` or `unauditable` verdict with the evidentiary consequence; do not request another Codex pass.

## Verdicts

- `supported`: evidence supports the claim as stated.
- `mostly_supported`: the core survives but scope, magnitude, wording, or certainty needs qualification.
- `mixed`: material parts or evidence receive different verdicts.
- `weakened`: evidence materially reduces plausibility without fully contradicting the claim.
- `contradicted`: audited evidence is inconsistent with the claim as stated.
- `indeterminate`: the available record cannot distinguish the important alternatives.
- `unauditable`: necessary evidence is unavailable or the claim cannot be operationalized.
- `opinion`: not directly fact-checkable; check its factual premises separately.

Use high, moderate, low, or indeterminate confidence. Explain confidence through evidence proximity, method, reproducibility, convergence, uncertainty, and counterevidence—not prestige.

## Workflow

1. Preserve the claim's exact wording, source, time, geography, and implied standard.
2. Decompose it into atomic claims.
3. Define what evidence could support, weaken, contradict, or leave each claim indeterminate.
4. Acquire the best reasonably available underlying evidence.
5. Record source identity, provenance, audit scope, access depth, incentives, limitations, and whether underlying data or records were inspected.
6. Extract raw evidence with a pinpoint locator.
7. Audit measurement, method, reproduction, assumptions, exclusions, missingness, uncertainty, alternatives, and claim fit where applicable.
8. Search for contradiction and relevant context.
9. Assign a verdict and evidence-based confidence.
10. Explain the ruling in plain language, including what it does not establish and what would change it.

For broad Evidence Audit Projects, use the `world-research` project schemas and gate.

## Evidence row

For each atomic claim include:

- Claim and checkable scope.
- Context and definitions.
- Raw evidence and pinpoint location.
- Provenance and access depth.
- Measurement and method.
- Reproduction or verification performed.
- Assumptions, exclusions, missingness, and uncertainty.
- Strongest counterevidence and alternatives.
- Source incentives and limitations.
- Claim fit.
- Verdict, confidence basis, and what would change it.
