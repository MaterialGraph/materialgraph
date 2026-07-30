# MaterialGraph Frontend Architecture

**Version:** 0.1  
**Status:** Initial Technical Direction

## 1. Proposed Stack

- React
- TypeScript
- Vite
- React Router
- TanStack Query for server state
- Zod for runtime response validation where useful
- Vitest and React Testing Library
- Playwright for end-to-end workflows

Graph library remains an open decision pending interaction and performance validation.

## 2. State Ownership

### Server state

Managed through TanStack Query:

- material identity;
- candidates;
- pathways;
- graph data;
- investigations;
- methodology metadata.

### URL state

Use for reproducible navigation:

- selected investigation version;
- selected material;
- active investigation stage;
- comparison candidate IDs;
- selected pathway where shareable.

### Local component state

Use for temporary interface behavior:

- open drawer;
- expanded provenance item;
- hover and keyboard focus;
- unsaved display preferences.

### Persistent client state

Add a dedicated store only when requirements exceed URL, server, and local state. Avoid premature global state.

## 3. Suggested Folder Structure

```text
src/
├── app/
├── routes/
├── features/
│   ├── materials/
│   ├── objectives/
│   ├── candidates/
│   ├── evidence/
│   ├── pathways/
│   ├── investigations/
│   └── methodology/
├── components/
│   ├── scientific/
│   ├── layout/
│   └── feedback/
├── api/
├── schemas/
├── hooks/
├── utils/
├── styles/
└── tests/
```

## 4. API Client Rules

- centralize base URL and authentication;
- validate status and reason fields;
- preserve request IDs;
- never reinterpret scientific rank in the client;
- map transport failures separately from computation statuses;
- include dataset and methodology version in query keys.

### 4.1 TanStack Query freshness policy

Cache policy must reflect the scientific mutability of the resource rather than applying one global default.

#### Active drafts and open exploration

Use a standard five-minute freshness window for mutable or actively recomputed resources:

```ts
const ACTIVE_EXPLORATION_STALE_TIME = 5 * 60 * 1000;
```

Typical resources include:

- active investigation drafts;
- current material workspaces;
- unsaved objective execution;
- open candidate and pathway exploration;
- current dataset-backed material details.

Background refetching is permitted only when it cannot silently change a historical scientific artifact.

#### Historical investigation versions

Saved investigation versions at routes such as `/investigations/:id/versions/:versionId` are immutable scientific artifacts and must use:

```ts
const historicalVersionQueryOptions = {
  staleTime: Infinity,
  gcTime: Infinity,
} as const;
```

The client must not background-refetch, revalidate, or silently replace a closed historical version. A user-requested refresh may verify availability or integrity, but it must not mutate the version's dataset snapshot, methodology version, objective hash, generated timestamp, computation status, or stored result payload.

A rerun against newer data or methodology creates a new investigation version with a new query key. It never invalidates or overwrites the historical version cache entry.

Query keys for saved versions must include at minimum:

```ts
[
  "investigation-version",
  investigationId,
  versionId,
  datasetVersion,
  methodologyVersion,
  objectiveHash,
]
```

## 5. Testing Strategy

### Unit

- status-to-banner mapping;
- tie-group rendering;
- coverage labels;
- evidence-state formatting;
- provenance chain rendering.

### Integration

- objective builder to candidate results;
- partial computation response handling;
- comparison selection;
- pathway edge inspection;
- investigation version switching.

### End-to-end

- canonical LiFePO4 investigation;
- tied candidate comparison;
- max-depth partial pathway search;
- save and reopen investigation;
- rerun against a newer version.

## 6. Non-negotiable Engineering Rules

- strict TypeScript mode;
- no client-side scientific re-ranking;
- no silent fallback from unknown to zero;
- no unlabelled visual encoding;
- accessible fallback for graph-only content;
- every major result state covered by tests.
