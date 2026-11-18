# RRB-01 frozen dataset export

Exported: 2026-11-16 [time] IST, read-only, from the production database of release-4 (50dd3ed).

- Method: `psql` on the server, one `SELECT id, mp_id, formula, pretty_formula, energy_above_hull FROM materials ORDER BY id` inside `BEGIN TRANSACTION READ ONLY … COMMIT`, written with `\copy` to /tmp, copied with `scp`, then deleted from the server. The database URL was read as plain text from /etc/materialgraph/runtime.env (sourcing the file with bash drops the value because of an `&` in the URL).
- Count in the database: 1727. File: 1728 lines (header + 1727 rows).
- `materials_50dd3ed.csv` SHA-256: CF49CAC2F6673BBF47C7425904458EA346743480424446C2F2B6892F3A0E4B51 (identical on the server and after copying).
- Cross-check against the import manifest (`materials-project.manifest.json`, file SHA-256 7939DCFD0FAB9A8E7E43F7395C59C874673ED19AAF49D1A942650A69595E3DAA; the documented payload digest 9021…a8b9 is computed differently and was not compared): the 1727 distinct MP IDs in the export and the 1727 distinct MP IDs mentioned in the manifest are identical (0 missing, 0 extra).
- Local `id` values are as assigned by the database at import; they are used for benchmark requests.