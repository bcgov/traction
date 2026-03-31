# WebVH end-to-end harness

This directory contains the Traction WebVH E2E harness entrypoint and phase registry.

Current runtime behavior:
- working CLI (`run.py`)
- profile/phase registry
- environment + token wiring
- smoke phase (`GET /status/live`)
- placeholder phases for the rest of the workflow

## Current scope

### Implemented
- `smoke` phase calls `GET /status/live`
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
- Traction tenant proxy reachable (default `http://localhost:8032`)

## Setup

```bash
cd scripts/webvh-e2e
poetry install
cp .env.example .env
```

`run.py` loads `.env` automatically (without overriding variables already set in your shell).

## Environment variables

Required:

- `TRACTION_TENANT_PROXY_BASE` (default: `http://localhost:8032`)
- `TRACTION_ISSUER_TENANT_TOKEN`
- `TRACTION_HOLDER_TENANT_TOKEN`

## Profiles

- `all` (default): all registered phases (including placeholders)
- `new-issuer-webvh`: WebVH-named path from `smoke` through `verify-webvh-post-revoke`

## Usage

```bash
poetry run python3 run.py
poetry run python3 run.py --profile new-issuer-webvh
poetry run python3 run.py --profile all -v
```

