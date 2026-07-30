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
