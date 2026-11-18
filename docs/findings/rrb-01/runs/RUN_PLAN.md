# RRB-01 run plan (AMD-001)

Recorded: 11/11/2026, before either run.
Amendment: rrb-01-amd-001 (commit 5f180a07)
Byte-exact package protection: commit 2985f722

## Assignment
| Run | Provider | Interface | Exact model identifier (as shown in the interface) |
| --- | --- | --- | --- |
| run_a | Google | Google AI Studio | [fill in before committing] |
| run_b | DeepSeek | DeepSeek web chat | [fill in before committing; if no version is shown, write what is shown and "version not displayed by the interface"] |

Models are not swapped after any result is seen. Any change is recorded here, with a
reason, before the affected run starts.

## Inputs (identical for both runs)
| File | SHA-256 |
| --- | --- |
| ai_extraction_rules.md | 56BCD2164B5E2A288F616497CE9F66973390A5DC0346DB308D508E1F59C94B05 |
| ai_extraction_prompt.md | F78AA9523EDDEA467A753DBB1CD4091B28C7B96D372564DEC50BF44108C4C7A5 |
| Sodium-ion batteries_ present and future - c6cs00776g.pdf | 6832B1BCFF445AED9CD7AC31E955CE9473EB8EF7A0ECD63FCBD874DB91799243 |
| batteries-07-00084-v2.pdf | 8D8991D441AD6AA43AFA98602411A685F40974980921E30BCD96D394F16B3292 |

## Pre-run checks
- Upload test: both interfaces accepted the 40 MB Hwang PDF unchanged ([date]); test
  chats deleted; no output used. Upload acceptance is not coverage evidence.
- Transcript and raw-output preservation verified for both interfaces: [fill in, see below]

## Coverage
The fixed coverage question and the per-page diagnostic are mandatory for both runs.
A model's report that it processed every page does not establish complete coverage.