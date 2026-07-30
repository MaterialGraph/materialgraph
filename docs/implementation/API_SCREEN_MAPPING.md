# MaterialGraph API-to-Screen Mapping

**Version:** 0.1  
**Status:** Initial Mapping Specification

## 1. Purpose

This document maps MaterialGraph backend capabilities to researcher-facing screens and defines transport, computation, partial-result, and failure behavior.

## 2. Global Response Rules

- HTTP status communicates transport and request handling.
- Application `status` communicates computation outcome.
- The frontend must not infer completeness from HTTP `200` alone.
- Partial scientific results remain valid within their declared boundary.
- Every computational response should eventually include dataset, methodology, and request metadata.

## 3. Canonical Status Mapping

| Status | HTTP | UI treatment |
|---|---:|---|
| `COMPLETED` | 200 | Standard result |
| `COMPLETED_PARTIAL` | 200 | Result plus top-level boundary notice |
| `COMPLETED_NO_RESULTS` | 200 | Scientific empty state |
| `REJECTED_INVALID_OBJECTIVE` | 422 | Inline correction flow |
| `FAILED_DEPENDENCY` | 503 | Recoverable service failure |
| `FAILED_INTERNAL` | 500 | Unexpected failure |

## 4. Initial Endpoint Mapping

| Backend capability | Screen | Primary components | Notes |
|---|---|---|---|
| Material detail | Material workspace | MaterialIdentityHeader, PropertyTable, CoverageBadge | Preserve missing values and provenance |
| Similar materials | Material workspace | RelationshipList, MaterialCard | Do not imply substitutions unless backend says so |
| Discovery candidates | Candidate results | TiedRankBlock, CandidateCard, ScoreBreakdown | Preserve rank groups |
| Discovery chains | Pathway explorer | PathCard, TransitionCard | Show boundary and path completeness |
| Objective chains | Pathway explorer | ObjectiveSummary, PathCard | Preserve objective satisfaction semantics |
| Discovery graph | Graph explorer | GraphNode, GraphEdge, GraphLegend | Every visual encoding documented |
| Discovery path | Pathway detail | OrderedPath, TransitionEvidenceDrawer | Explain each transition |
| Discovery analyze | Investigation workspace | ObjectiveSummary, CandidateResults, EvidencePanel | Canonical end-to-end computation |
| Communities | Material workspace / graph explorer | CommunitySummary, GraphFilter | Avoid implying scientific causality from clustering |

## 5. Partial Computation Example

```json
{
  "status": "COMPLETED_PARTIAL",
  "reason": "PATHWAY_TRUNCATED_MAX_DEPTH",
  "search_boundary": {
    "max_hops": 2,
    "max_hops_reached": 2
  },
  "result_metadata": {
    "is_complete": false
  },
  "candidates": []
}
```

Required banner:

> **Search boundary reached**  
> Search space was bounded at a maximum depth of 2. Valid pathways are shown, but additional pathways may exist beyond this search boundary.

## 6. Reason-Code Rendering

| Reason code | UI title | Required explanation |
|---|---|---|
| `PATHWAY_TRUNCATED_MAX_DEPTH` | Search boundary reached | Additional paths may exist beyond max depth |
| `SEARCH_SPACE_LIMIT_REACHED` | Search-space limit reached | Results are valid but graph coverage is incomplete |
| `CANDIDATE_LIMIT_REACHED` | Candidate display limit reached | More valid candidates may exist |
| `COMPUTATION_TIME_BUDGET_REACHED` | Computation time boundary reached | Search stopped at configured execution budget |
| `INSUFFICIENT_GRAPH_CONNECTIVITY` | Limited graph connectivity | No additional supported relationships were available |
| `PARTIAL_EVIDENCE_COVERAGE` | Partial evidence coverage | Candidate comparison requires caution |
| `UPSTREAM_DATA_UNAVAILABLE` | Supporting data unavailable | Some properties or evidence could not be retrieved |

## 7. Retry Rules

- Do not retry deterministic validation errors.
- Permit user retry for dependency and internal failures.
- Preserve objective state across failures.
- Automatic retries must be bounded and visible in technical details.
- Do not silently broaden scientific constraints during retry.

## 8. Cache Rules

- Material identity: cache by material ID and dataset version.
- Candidate results: cache by objective hash, dataset version, and methodology version.
- Paths: cache by source, target, objective, boundary, dataset version, and methodology version.
- Saved investigation versions are immutable.
- A newer dataset must not silently replace historical results.

## 9. Required Future Backend Metadata

Every computational response should converge on:

```json
{
  "status": "COMPLETED",
  "reason": null,
  "dataset_version": "2026.07",
  "methodology_version": "discovery-ranking-v1.4",
  "objective_hash": "...",
  "generated_at": "...",
  "request_id": "...",
  "result_metadata": {
    "is_complete": true
  }
}
```
