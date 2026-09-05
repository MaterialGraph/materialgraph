# MaterialGraph Deployment Guide

## Overview

MaterialGraph is deployed as a production-oriented FastAPI backend using:

* AWS EC2 (Ubuntu 24.04 LTS)
* Neon PostgreSQL
* SQLAlchemy
* Alembic
* systemd
* Nginx

Current deployment architecture:

Internet
↓
Nginx (Port 80)
↓
Uvicorn (127.0.0.1:8000)
↓
FastAPI
↓
Neon PostgreSQL

---

# Infrastructure

## AWS EC2

Instance Name:

materialgraph-api

Region:

ap-south-1 (Mumbai)

Instance Type:

t3.micro

Operating System:

Ubuntu Server 24.04 LTS

Elastic IP:

35.154.84.47

---

# Database

Provider:

Neon PostgreSQL

Database:

neondb

Production Branch:

production

SSL:

Required

Connection Pooling:

Enabled for application traffic

Direct Connection:

Used for Alembic migrations

---

# Environment Variables

Production environment file:

/opt/materialgraph/.env

Application variables:

DATABASE_URL=
MATERIALS_PROJECT_API_KEY=
ENVIRONMENT=production
LOG_LEVEL=INFO

Optional migration-specific override:

DATABASE_MIGRATION_URL=

Alembic prefers `DATABASE_MIGRATION_URL` when it is configured and otherwise
uses `DATABASE_URL`. The migration-specific value is useful when pooled and
direct database connections differ. If neither variable is configured,
Alembic fails without connecting to a fallback database.

Important:

* Do not commit `.env` files or other files containing credentials.
* Production secrets are managed directly on EC2.
* Local development and production use separate environment files.
* `.env.example` may contain variable names and safe placeholders only.
* Never store a production database password, API key, token, or complete credential-bearing connection string in a tracked repository file.
* Repository pushes and pull requests are scanned for secrets by Gitleaks in GitHub Actions.
* Development environments should enable the repository's `.githooks` pre-commit hook as documented in `getting_started.md`.

## Credential Rotation

If a production credential is exposed or suspected to be exposed:

1. Rotate or revoke the credential at the provider first.
2. Update `/opt/materialgraph/.env` with the replacement credential.
3. Restart the MaterialGraph service.
4. Verify service health before performing repository cleanup.
5. Remove the exposed credential from tracked files and Git history where necessary.
6. Verify secret scanning passes after remediation.

Deleting a credential from the current working tree does not remove it from existing Git history. A leaked credential must be treated as compromised even if the repository is subsequently cleaned.

---

# Initial Server Setup

Update packages:

sudo apt update
sudo apt upgrade -y

Install dependencies:

sudo apt install -y python3-pip python3-venv git nginx

Verify:

python3 --version
git --version
nginx -v

---

# Application Deployment

Create deployment directory:

sudo mkdir -p /opt/materialgraph
sudo chown ubuntu:ubuntu /opt/materialgraph

Clone repository:

git clone https://github.com/MaterialGraph/materialgraph.git /opt/materialgraph

Enter project:

cd /opt/materialgraph

Create virtual environment:

python3 -m venv .venv

Activate:

source .venv/bin/activate

Install dependencies:

pip install --upgrade pip

pip install -e .

The editable install uses the current checkout and exposes its canonical
`pyproject.toml` package version to the running API. Do not install a second
VCS checkout of MaterialGraph through `requirements.txt`.

---

# Database Migration

Run migrations:

alembic upgrade head

Verify revision:

alembic current

Verify history:

alembic history

---

# FastAPI Verification

Manual startup:

uvicorn app.main:app --host 0.0.0.0 --port 8000

Health endpoint:

http://<server-ip>:8000/health

Expected:

{
"status": "ok"
}

---

# systemd Service

The repository supplies the reviewed unit definition at its root:

materialgraph.service

It runs Uvicorn as the `ubuntu` user from `/opt/materialgraph`, loads secrets
from `/opt/materialgraph/.env`, binds only to `127.0.0.1:8000`, and restarts
after process failures. The tracked unit contains no credential values.

Install the unit with root ownership and read-only system permissions:

sudo install -o root -g root -m 0644 \
materialgraph.service \
/etc/systemd/system/materialgraph.service

Installed service file:

/etc/systemd/system/materialgraph.service

Reload systemd, enable the service for boot, and start it now:

sudo systemctl daemon-reload

sudo systemctl enable --now materialgraph

Check status:

sudo systemctl status materialgraph

View logs:

sudo journalctl -u materialgraph -f

Restart:

sudo systemctl restart materialgraph

## Daily database backup timer

The reviewed backup job uses the existing direct database URL in
`/opt/materialgraph/.env` and the EC2 instance role. Do not add database or AWS
credentials to the backup environment file.

Prerequisites are PostgreSQL 17 client tools, AWS CLI v2, a private versioned
S3 bucket with the controls in the recovery runbook, and the constrained EC2
backup role. Copy the safe example, then replace only the bucket placeholder in
the installed file:

```bash
sudo install -d -o root -g root -m 0755 /etc/materialgraph
sudo install -o root -g root -m 0600 \
  materialgraph-backup.env.example \
  /etc/materialgraph/backup.env
sudoedit /etc/materialgraph/backup.env
```

Install the reviewed units, check their syntax, and run one manual backup
before enabling the timer:

```bash
sudo install -o root -g root -m 0644 \
  materialgraph-backup.service \
  /etc/systemd/system/materialgraph-backup.service
sudo install -o root -g root -m 0644 \
  materialgraph-backup.timer \
  /etc/systemd/system/materialgraph-backup.timer
sudo systemd-analyze verify \
  /etc/systemd/system/materialgraph-backup.service \
  /etc/systemd/system/materialgraph-backup.timer
sudo systemctl daemon-reload
sudo systemctl start materialgraph-backup.service
sudo systemctl status materialgraph-backup.service --no-pager
sudo journalctl -u materialgraph-backup.service -n 30 --no-pager
sudo systemctl enable --now materialgraph-backup.timer
sudo systemctl list-timers materialgraph-backup.timer --all --no-pager
```

A successful run logs one `backup_verified` record. Any dump, validation,
upload, encryption, or remote-size failure produces a nonzero service result
and a `backup_failed` category without logging credentials. Review the timer
and newest verified object daily until external failure notification is added
through an approved low-cost channel.

---

# Nginx Configuration

Site file:

/etc/nginx/sites-available/materialgraph

Configuration:

server {
listen 80 default_server;
server_name _;

```
location / {
    proxy_pass http://127.0.0.1:8000;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

}

Enable:

sudo ln -s /etc/nginx/sites-available/materialgraph /etc/nginx/sites-enabled/materialgraph

Disable default site:

sudo rm /etc/nginx/sites-enabled/default

Validate:

sudo nginx -t

Reload:

sudo systemctl reload nginx

---

# Security Group Rules

Inbound:

SSH (22)
Source: My IP

HTTP (80)
Source: Anywhere

HTTPS (443)
Source: Anywhere

Port 8000 is not publicly exposed.

---

# Production Endpoints

API Root:

http://35.154.84.47

Swagger UI:

http://35.154.84.47/docs

Health Check:

http://35.154.84.47/health

---

# Common Operations

Pull latest code:

cd /opt/materialgraph

git pull origin main

source .venv/bin/activate

Run migrations:

alembic upgrade head

Restart service:

sudo systemctl restart materialgraph

Verify:

curl http://127.0.0.1/health

---

# Troubleshooting

Check service:

sudo systemctl status materialgraph

Check logs:

sudo journalctl -u materialgraph -n 100 --no-pager

Check nginx:

sudo systemctl status nginx

Validate nginx:

sudo nginx -t

Restart nginx:

sudo systemctl restart nginx

Check listening ports:

sudo ss -tulpn

---

# Deployment History

Phase 1 Production Deployment

Date:

June 2026

Features:

* FastAPI backend
* Material candidate screening
* Candidate comparison
* Scenario ranking
* Sensitivity analysis
* Substitution analysis
* Materials Project integration
* Neon PostgreSQL
* Production AWS deployment
