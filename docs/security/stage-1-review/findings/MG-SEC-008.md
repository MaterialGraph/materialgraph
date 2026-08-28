# MG-SEC-008 — Unbounded Research-Objective Collections Permit CPU Amplification

## Status

Open.

## Assessment

- Severity: **High**
- Confidence: **High**
- Affected component: public research-objective chain, exploration, and
  scientific-pathway requests
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

- `ResearchObjective` defines `avoid_elements`, `prefer_elements`, and
  `preserve_elements` without item-count, item-length, uniqueness, or canonical
  element-symbol validation.
- A database-free model probe accepted 10,000-entry collections unchanged.
- Research-objective exploration iterates preferred and avoided entries during
  scoring, then iterates them again during reason and warning construction for
  each candidate.
- `contains_element()` reparses the candidate formula on every iteration.
- Duplicate objective values are not normalized before this work.
- A local database-free benchmark evaluated 20 candidates with 10,000 repeated
  avoided and 10,000 repeated preferred elements. The 100,173-byte serialized
  objective took 2.825286 seconds versus 0.000759 seconds for one avoided and
  one preferred element, a measured 3,722.38-times time amplification. Measured
  peak allocation was 937,943 bytes.

No extreme payload was sent to the deployed prototype.

## Threat scenario

An unauthenticated client submits research-objective requests containing large
or duplicate element collections. One syntactically valid request causes
repeated formula parsing and collection traversal across the bounded candidate
pool before a response is produced. Repeated or concurrent requests can consume
worker CPU and memory and reduce availability even before database and graph
work are considered.

## Current safeguards

- Research objective `max_hops` is limited to three.
- Result limits are bounded to 20.
- Chain expansion and search-state budgets bound graph work.
- Nginx applies its effective request-handling defaults.
- Aggregate absence of rate and concurrency limiting is separately tracked by
  `MG-SEC-001`.

## Missing safeguards

- Maximum collection cardinality and per-item length.
- Canonical element-symbol validation for every objective entry.
- Duplicate normalization before service work.
- Explicit request-body policy aligned with application validation.
- Validation and performance regression tests for large and duplicate
  objectives.

## Recommended remediation

Define scientifically meaningful element-list cardinality limits, canonicalize
and deduplicate entries at the request boundary, reject unknown symbols, and
set an explicit proxy body-size policy. Preserve declared soft-preference and
hard-constraint semantics after normalization.

## Verification requirements

- Oversized collections and overlong entries receive a documented `422` or
  proxy rejection without entering scientific services.
- Duplicate and differently cased valid symbols normalize deterministically.
- Unknown symbols are rejected consistently across objective endpoints.
- Maximum valid requests complete within a documented performance budget.
- Normal scientific outputs, scores, and deterministic ordering remain
  unchanged for semantically equivalent objectives.
