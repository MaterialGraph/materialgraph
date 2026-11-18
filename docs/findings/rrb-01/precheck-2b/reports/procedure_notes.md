# RRB-01 pre-check 2b - procedure notes (2026-11-06)

Frozen system: release-4 = 50dd3eda31bbb1930dcc2782e3ec777af3c35244 (local tag `release-4` resolves to it).
The API exposes no commit identifier, so the server commit was not independently confirmed in this run.
Access: user-opened SSH tunnel, http://127.0.0.1:18000 -> server 127.0.0.1:8000. No credentials used by the agent.
Nothing was written to the production server.

## Procedural deviation
Before the matrix was run, one unapproved `GET /health` was sent to 127.0.0.1:18000 to probe the tunnel.
The connection was reset (curl exit 56); no HTTP response was received. It was not part of the approved matrix.
Afterwards exactly the approved requests were sent: 1 DC2 lookup GET, then 18 explore POSTs. No retries were needed.

## Correction to the brief (user instruction)
- DC1 historical: captured Case Study 01 field set (preserve ["Fe","P","O"], target_family "phosphate"),
  body = docs/findings/srq-01/release-4/evidence/cs01_l5.json (= docs/findings/srq-01/request.json), (5,5) x2,
  compared only against docs/findings/srq-01/release-4/evidence/post_cs01_l5.json.
- DC1 pinned and DC2 pinned: benchmark pinned field set (preserve [], target_family null).
- Historical and pinned results are reported separately and never compared with each other.
- Approved change: the formerly unassigned fields are an EXACT limit-equivalence rule.

## DC2 parent resolution
GET /api/v1/materials/search?mode=formula&q=Li3Fe2(PO4)3&limit=100 -> 14 matches (total_matches 14), all Li3Fe2(PO4)3:
mp-19430 (690), mp-25993 (751), mp-26069 (770), mp-26677 (835), mp-26825 (847), mp-504385 (941),
mp-585226 (1032), mp-6373 (1038), mp-705329 (1075), mp-758654 (1322), mp-759282 (1356), mp-772738 (1567),
mp-775523 (1596), mp-849395 (1671). Lowest numeric MP-ID: mp-6373 -> material_id 1038.
