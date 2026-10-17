# MaterialGraph Release 1 — Pilot Dataset Fact Sheet

**Revision:** rev1, 2026-10-17 (public version). Evidence originally checked 28 September 2026 against the four repository documents named below and the accepted integrated walkthrough; **re-confirmed:** 1,727 materials in production (Stage 5 Gate 2, 2026-10-16); local ID 5 = `mp-19017` LiFePO4 on the live pilot site (2026-10-17).

**Manifest statistics describe the acquired 1,727 source identities.** The imported database contains 1,699 newly inserted identities and 28 unchanged curated records with protected conflicts. Do not silently attribute every manifest field or distribution to those 28 curated database records.

| Claim | Authoritative source | Verified value or wording | Use in briefing | Notes/limitations |
|---|---|---|---|---|
| Final database total | `MG-DE_PRODUCTION_ROLLOUT_REPORT.md`, Import execution and post-import observation; Stage 5 Gate 2 (2026-10-16) | 1,727 distinct material `mp_id` identities; 1,699 inserted, 28 preserved protected conflicts. | 1,727 may be stated. | Not 1,727 new imports or unique formulas. |
| Pilot source | Live pilot site, `/materials/5/detail` (2026-10-17) | Local ID 5 = `mp-19017`, LiFePO4. | Yes. | Recheck in each pre-session environment freeze. |
| Acquisition scope | `MG-DE_SCIENTIFIC_COHORT_REPORT.md`, Scope; `MG-DE_SOURCE_CONTRACT.md`, Inclusion and exclusion | 48 selected chemical systems requested, 46 represented in the acquired manifest. Focused battery-relevant research cohort, not all Materials Project or battery materials. | General boundary yes; counts optional. | Two zero-result systems are source-query outcomes, not proof of absence of those materials. |
| Source release, selection | `MG-DE_QUALIFIED_MANIFEST_REPORT.md`, header and outcome; source contract | Materials Project release `2026.04.13`, selection contract `materials-project-selection-v3`, retrieved 2026-09-17 UTC. Deprecated and GNoME records excluded. | Source attribution as shown in product. | A release identifier is not field-level methodology. |
| Family composition | `MG-DE_SCIENTIFIC_COHORT_REPORT.md`, Scope and chemistry balance | Acquired source manifest: 920 oxides, 618 phosphates, 174 silicates, 15 sulfides; sum 1,727. | No need in the opening briefing. | Report categories characterize the manifest; the 28 unchanged curated records were not recounted. |
| Lithium and sulfide representation | Same, Scope and accepted limitations | Acquired manifest: 1,213 Li-containing identities (70.24%); 15 sulfides (0.87%). | General limited-coverage statement yes; counts unnecessary. | No domain-wide prevalence inference. `Li-Fe-S` and `Na-Ni-S` yielded zero at the approved release/query/energy bound. |
| Formula-sharing identities | Same, Formula and polymorph representation; source contract, Identity rules | 651 formulas; 234 have multiple source identities comprising 1,310 records in acquired manifest. | No need in opening briefing. | Distinct Materials Project IDs remain separate; formula equality does not establish the same structure or a duplicate record. |
| Stability distribution | Scientific cohort report, Stability distribution; qualified manifest report, Outcome | Acquired manifest: 141 source-stable/exact-zero; 622 above zero through 0.025; 964 above 0.025 through 0.05 eV/atom. Thus 1,586 above zero. | Not needed in the opening briefing. | Source-manifest measurements, not a recomputation of final database classifications. |
| Near-stability acquisition policy | Source contract, Inclusion and exclusion; qualified manifest report, Revision evidence | The reviewed acquisition selected records with `0 <= energy_above_hull <= 0.05 eV/atom`; no unbounded unstable-material query. | General research boundary only in initial briefing; exact policy during debrief if relevant. | The ceiling bounds a source query; it is not proof of experimental stability, synthesis feasibility, electrochemical performance, comparable methods, or exhaustive coverage. The Objective stored-stable control is a separate request behavior. |

The accepted walkthrough establishes the assembled workflow and current source identity. The source and manifest reports establish acquisition facts; the production rollout establishes the final identity count and preserved-curated split. Neither a source-stable flag nor an acquisition threshold establishes experimental stability. Discovery and Objective Investigation additionally apply bounded search and ranking; their returned lists are not global candidate rankings, and objective-coverage counts describe returned results only.

**Verification gaps excluded from participant materials:** exact family/stability/element distributions *recomputed over the final database*; per-field methods and conditions for comparison; physical synthesis or reaction validation. No numerical acquisition claim depends on these gaps.

## Known product limitations

Status verified 2026-10-17: all listed issues open; no application code change since the pilot baseline (backend runtime = `51b618e` code + Mako 1.4.2). Re-verify status before each session; remove an item only when its issue is closed **and** the fix is deployed.

| Issue | Limitation | Relevance to pilot tasks |
|---|---|---|
| #49 | Objective Chains API and Scientific Pathway Analysis use objective-blind bounded admission (only Objective Explore has the objective-aware policy). | Not used by the web UI. Relevant only if a participant uses the API directly. |
| #50 | Q6 (LiMnO2, Avoid Li + Prefer Na) still returns only Li-containing candidates; cause lies downstream of admission and is undiagnosed. | Relevant if a participant runs Objective Investigation from a source other than LiFePO4: results for other sources are not qualified. |
| #51 | Search metadata does not expose per-step expansion truncation (per-material expansion limit; `search_truncated` reflects only the global budget). | Search-scope text may understate how much of a neighbourhood was not examined. |
| #53 | Reserved preferred slots that dead-end are not backfilled, which can narrow the search. | Affects the "N of M generated chains" figure; not the returned results' validity. |

#54 (journal rate limiting) is operational only and not listed.
