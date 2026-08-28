# MG-SEC-009 — Screening Logs Unbounded Request Collections Verbatim

## Status

Open.

## Assessment

- Severity: **Medium**
- Confidence: **High**
- Affected component: public screening service, Loguru stdout sink, system
  journal, and operational logging boundary
- Application evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Deployment evidence checkpoint:
  `60c06651c75aaf839a90ded90bf3ce3aad6e8e8d`
- Resolution version or commit: **Not resolved**

## Exact evidence

- `CandidateScreeningRequest` accepts unbounded `scarce_elements` and
  `avoid_elements` collections.
- `CandidateScreeningService.screen_candidates()` logs both complete
  collections at `INFO` after screening work completes.
- Application logging writes to stdout; deployed systemd routes stdout to the
  system journal and stderr inherits that destination.
- Active and archived journals occupied 167.1 MB when inspected.
- No project-specific journal storage or rate policy was configured.
- A process-isolated local probe supplied 10,000 scarce and 10,000 avoided
  entries. The 157,871-byte serialized request produced a 177,850-byte log
  entry. The probe captured only the byte count and did not print the entry or
  call the deployed API.

## Threat scenario

An unauthenticated client repeatedly submits large screening requests. Each
request performs the complete screening workload and then writes a log entry
larger than the request body. Repetition increases journal storage and disk I/O,
can displace or rate-suppress useful operational evidence, and can contribute
to host resource pressure.

## Current safeguards

- Screening converts the element collections to sets before per-material
  scoring.
- systemd-journald applies its platform storage and rate-management behavior.
- Nginx is the public proxy rather than direct Uvicorn exposure.
- Aggregate request limiting is separately tracked by `MG-SEC-001`.

## Missing safeguards

- Structured logging of collection counts rather than complete values.
- Explicit truncation or maximum logged-field length.
- Request collection and item validation.
- Documented journal retention, storage, and alerting policy.
- Regression tests preventing high-cardinality input from producing
  proportional log entries.

## Recommended remediation

Log bounded metadata such as normalized collection counts and request outcome,
not complete user-controlled collections. Align request validation with
scientifically meaningful bounds and define operational journal retention and
disk monitoring.

## Verification requirements

- Maximum valid and rejected requests produce bounded log entries.
- Logs contain counts and safe outcome metadata but not full objective lists.
- Repeated validation failures do not cause proportional journal growth.
- Journal retention and disk thresholds are documented and monitored.
- Normal screening results and deterministic ordering remain unchanged.
