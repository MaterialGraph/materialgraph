# MG-SA Observations Register

Every concern below has exactly one required classification. Items classified
as defects have separate finding records; other items remain observations.

| ID | Area | Observation | Classification | Disposition |
|---|---|---|---|---|
| `MG-SA-O-001` | Resource containment | Mounted graph/intelligence routes were absent from admission and deadline classification, and the documented Nginx site-wide connection cap was client-keyed | **Implementation defect** | Remediated, deployed, independently verified, and closed under `MG-SA-001` |
| `MG-SA-O-002` | CI governance | Passing workflows are not enforced by branch protection/rulesets and push checks may be skipped | **Verification defect** | Repository claims and manual deployment precondition corrected under `MG-SA-002`; acceptance verification pending |
| `MG-SA-O-003` | HTTPS redirect | Port-80 default server redirects to `https://$host$request_uri`, accepting a syntactically valid unrecognized Host | **Future hardening** | Use a canonical-name redirect and reject unknown hosts before accounts/private state or stronger anti-phishing requirements |
| `MG-SA-O-004` | Recovery identity | Backup manifest records Git `HEAD` but does not require a clean deployment worktree | **Future hardening** | Record dirty state or fail closed before recovery claims depend on code/data pairing |
| `MG-SA-O-005` | Backup privilege | Backup runs as deployment user and inherits a broad environment into child tools | **Accepted residual risk** | No public application write path to the backup unit; reconsider if operators or plugins expand |
| `MG-SA-O-006` | Database privilege | Restricted roles retain default database `TEMP` | **Accepted residual risk** | Already explicit and proportionate to the current prototype |
| `MG-SA-O-007` | Source governance | Commits are unsigned and `main` permits direct/force updates | **Accepted residual risk** | Proportionate to the solo-maintainer public prototype; live guidance explicitly does not claim protected-branch enforcement |
| `MG-SA-O-008` | Runtime network | EC2 egress is unrestricted | **Accepted residual risk** | No server-side integrations or private-data exfiltration boundary in current product; revisit with LLMs or external services |
| `MG-SA-O-009` | Documentation | Security README “Next Step” language still describes the remediation sequence as merely approved after completion | **Documentation inconsistency** | Correct in a future current-state documentation update; historical files remain unchanged during assurance |
| `MG-SA-O-010` | Documentation | Stage 1 evidence register says last updated 2026-09-12 although it includes 2026-09-13 evidence | **Documentation inconsistency** | Metadata-only correction; evidence content remains intelligible |
| `MG-SA-O-011` | Frozen record | Final inspection still lists findings open but explicitly labels itself frozen and points to current registers | **No issue** | Appropriate preservation of audit chronology |
| `MG-SA-O-012` | API contract | Substitution `top_n` accepts non-positive/extreme values but slices a finite current candidate pool | **Future hardening** | Correct API semantics before dataset growth; no current material security amplification confirmed |
| `MG-SA-O-013` | Development DB | Docker Compose publishes default local PostgreSQL credentials on all interfaces | **Future hardening** | Bind to loopback and discourage use outside isolated development environments |
| `MG-SA-O-014` | Health/docs | Public liveness, version/environment, OpenAPI, Swagger, and ReDoc remain intentional | **Accepted residual risk** | Reassess with authentication or private capabilities |
| `MG-SA-O-015` | Complete suite | The recorded `823 passed, 1 skipped` result was not independently reproduced. An isolated unseeded SQLite invocation produced `747 passed, 72 failed, 5 skipped`; failures consistently reflected missing seeded materials and relationships. | **No issue** | Historical claim remains evidence, not independently reproduced assurance; focused security suite was reproduced. Authoritative rerun requires the prepared PostgreSQL `materialgraph_test` database. |
| `MG-SA-O-016` | Deployment drift | Committed controls may differ from effective production state after the historical checkpoints | **No issue** | Explicit evidence limitation pending approved read-only live checks |

## No promoted new current findings

No concrete vulnerability outside the original Stage 1 control set met the
threshold for a new current finding. Generic enterprise measures were not
promoted without a present threat path.
