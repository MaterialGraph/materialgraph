# MG-IA-001 — Release identity is inconsistent across package metadata and current documentation

- Classification: confirmed defect / material reproducibility risk
- Priority: P2
- Confidence: high
- Disposition: confirmed
- Baseline: `a1605e61f72035890692ab4df63ebd2f7b859069`

## Affected files and components

- `pyproject.toml` — project version
- `materialgraph.egg-info/PKG-INFO` — tracked distribution metadata
- `app/version.py` — runtime version resolution
- `app/main.py` — OpenAPI metadata and `GET /health`
- `README.md` — documented current release/capability version
- `docs/guide/getting_started.md` — documented editable-install workflow

## Exact evidence

- `pyproject.toml` declares `version = "0.1.0"`.
- `materialgraph.egg-info/PKG-INFO` declares `Version: 0.1.0`.
- `app/version.py:get_project_version()` returns `metadata.version("materialgraph")`, or `0+unknown` when metadata is absent.
- `app/main.py` uses `PROJECT_VERSION` for FastAPI's version and the root `/health` response.
- `docs/guide/getting_started.md` instructs `pip install --no-deps -e .`.
- `README.md` labels the current capability set `v1.9.6`.

## Expected behavior

The same immutable source revision and documented installation method should expose one unambiguous release identity across package metadata, API metadata, health output, and current documentation.

## Actual behavior

The documented installation creates distribution metadata identifying the application as `0.1.0`; the application then publishes `0.1.0`, while the repository's current-capability documentation identifies it as `v1.9.6`. Without installed metadata, the same source reports `0+unknown` instead.

## Impact

Bug reports, API captures, scientific-result records, deployments, and reproducibility evidence can identify the same implementation under conflicting versions. This weakens provenance and makes it harder to determine which code and scientific rules produced an output.

## Reproducibility

Static reproduction:

1. Inspect the version in `pyproject.toml` and tracked `PKG-INFO`.
2. Trace `get_project_version()` to `PROJECT_VERSION` in `app/main.py`.
3. Compare the result with the current-version heading in `README.md`.

Runtime confirmation when a checkout is available:

1. Follow the documented editable installation.
2. Run `python -c "from app.version import PROJECT_VERSION; print(PROJECT_VERSION)"`.
3. Request `/health` and inspect FastAPI/OpenAPI version metadata.

Expected current result after the documented install: `0.1.0`, not `1.9.6`.

## Existing tests

`tests/test_health.py` exercises only `/api/v1/health`, which does not include a version field. No reviewed test establishes a canonical release identity.

## Missing regression coverage

- Assert that the canonical package version matches the intended release identifier.
- Assert that API metadata and any version-bearing health endpoint use that canonical value.
- Add a release check preventing current documentation and package metadata from drifting.

## Recommended remediation scope

Choose and document one version authority, align package and tracked metadata with it, define behavior for source checkouts without installed metadata, and add a release-consistency regression check. Do not introduce another manually maintained runtime version constant.

## Caller/cross-service trace

Confirmed direct consumers are FastAPI application metadata and root `/health`. Documentation and installed distribution metadata are external provenance consumers. A complete checkout search is still required to exclude additional `PROJECT_VERSION` consumers.
