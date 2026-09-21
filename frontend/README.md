# Material Explorer (read-only milestone)

Run the FastAPI backend locally at `http://127.0.0.1:8000`, then from this directory run `npm ci` and `npm run dev`. Vite proxies `/api` to the local backend. For another API origin set `VITE_API_BASE_URL` at build time; that origin must explicitly allow browser requests. No write endpoints are called.

Run `npm run build` to check strict TypeScript and produce the static bundle. This milestone displays the first 100 materials and allows paging and direct lookup by **local numeric ID**. Filtering applies only to loaded pages; the backend has no search endpoint. URL `?material=<id>` opens a material directly.

The candidates endpoint uses its existing soft avoid/prefer semantics and existing backend ordering. Score numbers are internal rule scores. The material detail response includes a source label but no per-property provenance or evidence quality; the UI says so. Neither endpoint supplies dataset or methodology versions, rank groups, coverage, completeness status, or saved investigation identity. The UI does not fabricate those fields or claim a scientific tie. No domain-specific objective defaults are applied.
