# WebVH end-to-end harness

This directory contains the Traction WebVH E2E harness entrypoint and phase registry.

Current runtime behavior:
- working CLI (`run.py`)
- profile/phase registry
- environment + token wiring
- smoke phase (`GET /status/live`, `GET /tenant/wallet` for issuer and holder)
- placeholder phases for the rest of the workflow

## Current scope

### Implemented
- `smoke` phase calls `GET /status/live` and authenticated `GET /tenant/wallet` (issuer + holder)
- context loading from `.env` and shell env
- required issuer/holder token validation at startup
- profile execution and run summary

### Not implemented yet
- `upgrade-anoncreds-wallet`
- `configure-webvh-plugin`
- `webvh-create`
- `publish-schema-webvh`
- `publish-cred-def-webvh`
- `oob-didexchange-webvh-didcomm`
- `issue-webvh`
- `verify-webvh`
- `revoke-webvh`
- `verify-webvh-post-revoke`
- `issue-indy`

Each placeholder phase currently logs "not implemented yet" and returns success.

## Prerequisites

- Python 3.10+
- Poetry 1.8+
- Traction tenant proxy reachable (default BC Gov sandbox URL; override with `TRACTION_TENANT_PROXY_BASE`)

## Setup

```bash
cd scripts/webvh-e2e
poetry install
cp .env.example .env
```

Run commands from this directory (`scripts/webvh-e2e`) so `python-dotenv` picks up `./.env` (it does not override variables already set in your shell).

## Environment variables

Required:

- `TRACTION_TENANT_PROXY_BASE` (default: `https://traction-sandbox-tenant-proxy.apps.silver.devops.gov.bc.ca`; use `http://localhost:8032` for a local stack)
- `TRACTION_ISSUER_TENANT_TOKEN`
- `TRACTION_HOLDER_TENANT_TOKEN`

## Profiles

- `all` (default): all registered phases (including placeholders)
- `new-issuer-webvh`: WebVH-named path from `smoke` through `verify-webvh-post-revoke`

## Usage

From `scripts/webvh-e2e`:

```bash
poetry run python3 run.py
poetry run python3 run.py --profile new-issuer-webvh
poetry run python3 run.py --profile all -v
```

