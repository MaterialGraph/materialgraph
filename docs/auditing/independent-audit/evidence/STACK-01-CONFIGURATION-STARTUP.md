# Stack 01 Evidence — Configuration and Startup

## Files reviewed

`pyproject.toml`, requirements files, `.env.example`, `docker-compose.yml`, package metadata, configuration, database bootstrap, logging, version resolution, application/router assembly, both health handlers, Alembic environment/configuration, shared test fixtures, health/configuration tests, README, getting-started guidance, and technical notes.

## Result

No configuration/startup defect meets the current strict confirmation threshold.

Two prematurely classified propositions were returned to observation status:

- version identity requires an explicit package/release/capability version policy;
- health-contract divergence requires intended probe semantics and deployment evidence.

## Positive checks

- Required `database_url` fails closed.
- Sessions close in `finally`.
- SQLAlchemy uses `pool_pre_ping=True`.
- Alembic uses application metadata.
- FastAPI and root health use the same resolved package version.
- Configuration tests verify installed-metadata resolution and non-release fallback.

## Limitations

No runtime startup or deployment probe was executed without the exact checkout and deployment configuration.
