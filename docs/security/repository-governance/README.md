# Repository Governance

This directory records repository-hosting controls separately from application,
infrastructure, and dataset-expansion work.

| Work item | Purpose | Status |
| --- | --- | --- |
| [`MG-GOV-001`](MG-GOV-001.md) | Protect `main`, require pull requests and security checks, enable GitHub security services, and establish public policy files | Closed; PR #5 merged as `3db99d96abc26b2810cd107590cacd8e2c0f10fd` |

The `MG-GOV-*` namespace does not reopen or extend `MG-DE-009`. Repository
governance work does not authorize a production deployment, restore, restart,
database connection, or database write.
