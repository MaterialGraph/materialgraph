# Initial Completed-Audit Register Comparison

## Sources

- Frozen independent baseline: commit
  `a1605e61f72035890692ab4df63ebd2f7b859069`.
- Completed-audit README supplied 2026-08-24.
- Completed `AUDIT_REGISTER.md`, last updated 2026-08-21.

## Authority and count verification

The completed-audit README designates `AUDIT_REGISTER.md` as the sole
authoritative source of status and totals. Its definition of `Remediated`
requires recorded remediation and regression evidence but explicitly limits
closure to documented engineering scope; it does not claim independent
scientific validation.

The register contains 94 table rows with unique, uninterrupted identifiers from
`MG-AUD-001` through `MG-AUD-094`:

| Status | Declared | Mechanically counted |
|---|---:|---:|
| Remediated | 92 | 92 |
| Accepted behavior | 2 | 2 |
| Open | 0 | 0 |
| Total | 94 | 94 |

The two accepted-behavior records are `MG-AUD-010` and `MG-AUD-026`.

## High-confidence title-level mapping candidates

These mappings are narrow enough to record before reading the detailed earlier
finding and remediation evidence. They are not yet remediation-effectiveness
conclusions.

| Independent finding | Earlier finding candidate | Basis | Current reconciliation state |
|---|---|---|---|
| `MG-IA-011` — Neighborhood limit does not bound graph expansion | `MG-AUD-072` — Neighborhood response limits do not bound traversal work | Same component, limit location, and unbounded traversal behavior | Candidate correspondence; detailed scope and remediation evidence required |
| `MG-IA-013` — Multiple scientific APIs accept nonexistent element symbols | `MG-AUD-093` — Public validation accepts nonexistent chemical symbols | Same public-input validation invariant; independent finding may have broader route scope | Candidate correspondence; route-by-route remediation scope required |
| `MG-IA-015` — Weighted shortest path silently searches only one hop | `MG-AUD-084` — Discovery path lookup ignores `max_hops` and searches direct paths only | Same path endpoint and direct-only behavior despite hop parameter | Candidate correspondence; algorithm and regression evidence required |
| `MG-IA-019` — Scenario ranking accepts negative and unbounded result limits | `MG-AUD-094` — Analytical endpoints accept negative or unbounded result limits | Exact boundary defect within one analytical endpoint; earlier scope may be broader | Candidate correspondence; schema/route remediation scope required |
| `MG-IA-025` — Vision document says objectives execute only first avoid/prefer elements | `MG-AUD-009` — Multi-element objectives were reduced to single-element evaluation | Documentation describes the earlier runtime defect as current although reviewed runtime now handles full collections | Candidate correspondence; likely stale documentation, but resolution/change-impact evidence required |

## Plausible relationships intentionally deferred

Several titles indicate related subject matter but do not yet establish the same
defect:

- `MG-IA-004` and `MG-IA-012` versus earlier tie/ordering findings;
- `MG-IA-007` versus risk/criticality evidence and provenance findings;
- `MG-IA-009` versus composition weighting and explicitly empty composition
  semantics;
- `MG-IA-010` versus earlier scenario/sensitivity findings;
- `MG-IA-014` versus canonical stability-evidence reuse;
- `MG-IA-016` and `MG-IA-018` versus strict objective, bounded-search, and API
  contract findings;
- `MG-IA-017` versus endpoint risk-coverage propagation;
- `MG-IA-023` versus graph-job authorization remediation and route disabling;
- `MG-IA-024` versus earlier setup/dependency documentation findings.

These are deliberately not mapped until the detailed range files and resolution
ledgers establish scope, expected behavior, remediation mechanism, and tests.

## Independent items with no clear title-level counterpart yet

No clear register-title match is currently established for:

- `MG-IA-003` populated-predecessor migration failure;
- `MG-IA-008` failed import batch leaving pending session changes;
- `MG-IA-020` missing-root chain APIs returning successful empty results;
- `MG-IA-021` advertised Materials Project API URL being ignored;
- `MG-IA-026` deployment guide omitting systemd unit creation.

This is provisional. “No clear title-level counterpart” does not yet mean
genuinely new; detailed earlier findings may contain broader scopes than their
register titles.

## Evidence required next

1. The four detailed finding-range documents.
2. July and August resolution ledgers linked from the register.
3. July and August change-impact histories where behavior changed externally.
4. Any separate regression-test or deployment-verification records referenced
   by those ledgers.
