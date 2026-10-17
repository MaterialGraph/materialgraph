# MaterialGraph Release 1 — Post-Pilot Findings and Decision Template

**Revision:** rev1, 2026-10-17 (public version).

Aggregate only after all sessions. Record denominator and exposure: `Observed across 1/3 participants; 2 were exposed, 1 not exposed` where applicable. Frequency alone does not decide severity.

## Finding MG-R1-PILOT-___

Stage: ___  Type (scientific interpretation / coverage interpretation / missing evidence / workflow clarity / functional defect / performance / dataset limitation / provenance limitation / facilitation or protocol / enhancement): ___

Observed across: ___ / ___ participants; exposed: ___ / ___; access or intervention differences: ___

Severity: **A** material scientific misdirection or blocked intended investigation; **B** important usefulness or interpretation issue before wider exposure; **C** minor clarity improvement; **D** future capability beyond Release 1.

Evidence (participant codes, task, quotes, screenshots where authorized): ___

Observed behavior: ___  Research consequence: ___  Alternative explanations or confounds (including facilitator wording, intervention, response time, environment change): ___

Possible response and evidence needed to decide: ___  Owner decision/date: ___

## Decision framework

Choose a disposition per finding with a reason: **No change; Briefing/documentation; Frontend wording/presentation; Backend/search investigation; Data/provenance work; Performance investigation; Release 1 correction; Future capability.** A scientifically serious misinterpretation once can outweigh a repeated cosmetic preference. Feature requests are recorded as needs first; do not create a Release 2 backlog automatically.

## Session synthesis

Participants/exposure: ___  Recurrent comprehension patterns: ___  Coverage and objective interpretation (aggregated): ___  Useful signals: ___  Scientific risks: ___  Workflow failures: ___  Objective response times (range): ___  Evidence required next: ___  Environment differences or changes during the pilot: ___  Accessibility context: ___  Decision on next bounded slice: ___

Known boundaries: sessions ran on the live pilot site at the frozen baseline (backend `faab7d9`, frontend release `51b618e`, 1,727-identity dataset) unless a recorded change says otherwise. Results for sources other than LiFePO4 are not qualified (see #50). The coverage summary describes returned results only and does not evaluate elements to retain or the target family. Objective Chains API and Pathway Analysis (#49) were not part of the UI tasks. Response times are facilitator-observed samples, not benchmarks. Empty, malformed-link, API-error and missing-chain states were not systematically exercised. Same-site IDs are required for shared links. This pilot does not qualify screen readers or other assistive technology unless expressly evaluated and recorded; it does not validate chemistry, statistical market demand, or comprehensive coverage.

## Preparation gate

**Outcome A — Pilot package ready for review** requires all of:

1. Revised package (01–06, rev1) reviewed and adopted by the owner.
2. Per-participant credentials implemented under a separately approved proposal and verified: Basic Auth still enforced; each credential independently revocable; access logs attribute requests to a username without recording passwords; facilitator/administrator access works; rollback tested.
3. Internal rehearsal completed on the live pilot site at the frozen baseline, with protocol problems recorded and resolved.
4. Known-limitations list (#49–#53) status re-verified.

No deployment, recruitment, pilot execution, code, database, configuration or repository documentation change is authorized by this template.
