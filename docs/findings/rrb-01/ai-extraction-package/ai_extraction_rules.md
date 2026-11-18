<!-- Copied verbatim from rrb-01-protocol-v0.3.md (SHA-256 0ED2C4705ECF635F728FE9F3366A03090BBBAC109096544C2F22B759B5227CA9); blocks: Order of operations., Explicit-pair requirement., Relationship characterization., Qualifying relationship types, Composition rules, Spatially heterogeneous materials., Morphology and surface modifications., Directed pairs only., Evidence-source record., Extraction output schema, Frozen source snapshots., What creates a record., Duplicates. -->

**Order of operations.** First enumerate every literature pair in the sources (the source cohort). Only then classify each pair against the dataset. Dataset membership is never an extraction criterion, so Q4's denominator is unbiased.

**Explicit-pair requirement.** A pair is extracted only when the source text, a table or a caption explicitly relates the target composition to a named parent composition as its substitute or analog. A material presented only as a broad technology alternative, for example a cobalt-free cathode discussed alongside cobalt-containing cathodes in general, does not form a pair. The extractor never supplies a parent the source does not name.

**Relationship characterization.** Each extracted pair records how the source itself characterizes the relationship, as one of: formula or structural analog; proposed replacement; experimentally evaluated substitute. The label is taken from the source's wording, with the supporting location recorded. Labels are never merged into a single validity claim, and a named formula analog is not treated as a demonstrated functional substitute. The label is reported as a descriptive stratum and does not change eligibility or the primary denominator.

**Qualifying relationship types (provisional).** Two types qualify, each recorded and reported as its own stratum:

1. Cross-chemistry analog: the source names a parent and a target in different chemistries (for example, a Li compound and its Na analog) and states the analog or substitution relationship.
2. Within-family composition substitution: the source names a parent composition and a target in which one or more elements are explicitly replaced, partially or fully.

A synthesis route alone, such as a material obtained by ion exchange from a precursor, does not qualify unless the source independently describes a substitution or analog relationship. Direction follows the source's explicit parent-to-target description.

**Composition rules (provisional).**

| Composition type | Rule |
| --- | --- |
| Fixed integer formula | Include |
| Fixed fractional formula | Include; keep the published formula in the audit record and normalize with exact rational arithmetic, never floating point |
| Fixed doped composition | Include if both parent and target compositions are explicitly named |
| Formula with an unresolved variable | Exclude from scored cases; count in the source cohort |
| Variable formula with a stated value | Include only if that value is explicitly tied to the documented relationship |
| Material family without a specific composition | Exclude from scored cases; count in the source cohort |

**Spatially heterogeneous materials.** Core–shell, concentration-gradient and other spatially heterogeneous materials are excluded as benchmark endpoints when their defining composition cannot be represented by a single homogeneous formula. The exclusion applies to the material, not the study: a separate, explicit substitution between two homogeneous compositions documented in the same study can qualify on its own.

**Morphology and surface modifications.** Comparisons involving only coatings, particle size, crystallinity, single-crystal versus polycrystalline structure or synthesis method, with the underlying composition unchanged, do not form pairs. A composition substitution accompanied by a morphology change can qualify if the source explicitly identifies the compositional relationship; the morphology change is recorded as a confounding characteristic and is never read as evidence that the substitution caused a reported performance difference.

**Directed pairs only.** A comparison among alternative dopants or compositions does not establish a pair unless the source identifies which composition replaces or modifies which parent.

**Evidence-source record.** For each extracted pair, the audit trail records the cited primary-study identifier (DOI or reference number in the source) where the review relays another study's result.

### Extraction output schema (draft, to be fixed at protocol lock)

Both the founder and the AI extraction write one JSON Lines file each, UTF-8, one record per line, with the same schema version. Extractors record compositions exactly as published; a deterministic script, not the extractor, performs normalization.

**Frozen source snapshots.** Extraction uses the publisher PDF of each source, saved with its SHA-256 recorded. Locations refer to these files only.

| Source | File | SHA-256 |
| --- | --- | --- |
| Hwang 2017 | Sodium-ion batteries\_ present and future - c6cs00776g.pdf | 6832B1BCFF445AED9CD7AC31E955CE9473EB8EF7A0ECD63FCBD874DB91799243 |
| Noerochim 2021 | batteries-07-00084-v2.pdf | 8D8991D441AD6AA43AFA98602411A685F40974980921E30BCD96D394F16B3292 |

**What creates a record.** A record is created for every statement, table row or caption that does either of the following: (a) places two specific compositions, or a composition and a material family, in a substitution, replacement, analog, doping or comparison context; or (b) presents a single specific composition as replacing, substituting for or serving as an analog of an unnamed parent or a general class (for example, "cobalt-containing cathodes"). Type (b) records are always `exclude` with reason `no_named_parent`. Included and excluded candidates are both recorded, so exclusions can be compared between extractions.

| Field | Content | Filled by |
| --- | --- | --- |
| schema\_version | Fixed string, e.g. `rrb01-extract-1` | Extractor |
| extractor | `founder` or `ai` | Extractor |
| record\_id | `<source>-<page>-<n>`, n counting records on that page in reading order | Extractor |
| source | `HWA17` or `NOE21` | Extractor |
| location | Page, section number, and paragraph ordinal within the page, or table/figure number and row | Extractor |
| evidence | The relating sentence or row, quoted, at most 40 words | Extractor |
| cited\_primary\_study | Reference number and DOI the source cites for the statement, or `none` if the review's own statement | Extractor |
| parent\_as\_published | Parent composition exactly as printed, or `null` if the source names none | Extractor |
| target\_as\_published | Target composition exactly as printed | Extractor |
| composition\_type | One of: `fixed_integer`, `fixed_fractional`, `fixed_doped`, `unresolved_variable`, `variable_with_stated_value`, `family_no_composition`, `spatially_heterogeneous` (for parent and target separately) | Extractor |
| direction\_basis | The words establishing which composition replaces or modifies which | Extractor |
| relationship\_type | `cross_chemistry_analog` or `within_family_substitution` | Extractor |
| characterization | `formula_or_structural_analog`, `proposed_replacement` or `experimentally_evaluated_substitute` | Extractor |
| confounders | List, e.g. `morphology_change`, `coating`; empty if none | Extractor |
| decision | `include`, `exclude` or `ambiguous` | Extractor |
| exclusion\_reason | One of: `no_named_parent`, `not_directed`, `synthesis_route_only`, `morphology_or_surface_only`, `spatially_heterogeneous`, `unresolved_variable`, `family_no_composition`; `null` unless decision is `exclude` | Extractor |
| ambiguity\_note | Which rule could not decide the record, and why; `null` unless decision is `ambiguous` | Extractor |
| parent\_normalized, target\_normalized | Reduced formulas by exact rational arithmetic | Script |

**Duplicates.** Each occurrence keeps its own record and its own decision. Occurrences of the same normalized directed pair, at several locations or in both sources, collapse into one benchmark case, which qualifies if at least one occurrence is `include`. An occurrence that does not itself meet the rules (for example a mutual comparison without direction, recorded as `exclude`, `not_directed`) never becomes qualifying evidence because another occurrence qualifies; the case's audit trail lists every occurrence with its decision.
