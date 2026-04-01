# WebVH end-to-end harness

This directory contains the Traction WebVH E2E harness entrypoint and phase registry.

Current runtime behavior:
- working CLI (`run.py`)
- profile/phase registry (`phases/smoke.py` liveness, `phases/webvh.py` WebVH configure/create, `phases/connect.py` DIDComm connection phases)
- environment + token wiring
- smoke phase (`GET /status/live`, `GET /tenant/wallet` for issuer and holder)
- issuer wallet upgrade, WebVH configure, and `webvh-create` (HTTP-backed); other phases remain placeholders

## Current scope

### Implemented
- `smoke` phase calls `GET /status/live` and authenticated `GET /tenant/wallet` (issuer + holder)
- `upgrade-anoncreds-wallet`: `GET /tenant/wallet` for `settings.wallet.name` and type (ACA-Py `GET /settings` omits `wallet.name`), optional `POST /anoncreds/wallet/upgrade`, poll until `askar-anoncreds`
- `configure-webvh-plugin`: `GET /tenant/server/status/config` (controller defaults only), optional `WEBVH_WITNESS_INVITATION` or fetch `/api/invitations` on the WebVH server, `POST /did/webvh/configuration` with **request** / **response** logged (pretty JSON; logs shorten `witness_invitation` and replace `scids` with `{}`). Merges stored `parameter_options` from `GET /did/webvh/configuration`; sets `witness_threshold` only when `WEBVH_WITNESS_THRESHOLD` is positive, and **drops** any merged `witness_threshold` when it is not (avoids echoing an old stored value)
- `webvh-create`: `POST /did/webvh/create` with `options` (`namespace`, `identifier` for the path segment, **`didcomm: true`**, optional `witness_threshold` when env is positive, optional `server_url` from stored config or context). Default identifier is **8** random `[a-z0-9]` characters (env `WEBVH_CREATE_ALIAS` / `WEBVH_CREATE_IDENTIFIER`). Sends **`apply_policy: true`** by default (merge with WebVH server identifier policy; matches ACA-Py). Set `WEBVH_CREATE_APPLY_POLICY=false` to skip policy merge. Sets `ctx.webvh_last_created_did` when the response includes a `did:webvh` id
- context loading from `.env` and shell env
- required issuer/holder token validation at startup
- profile execution and end-of-run **summary** (indented `run` + `webvh` sections: `traction_url`; after create, full `did:webvh:…` and **explorer** link `{server_url}/api/explorer/dids?scid=…` when a DID is present)
- `--witness`: adds `endorsement: true` to the WebVH configure POST (endorser-style flow)

### Not implemented yet

**AnonCreds publish**

- `publish-schema-webvh`
- `publish-cred-def-webvh`

**Connection and issue** (`phases/connect.py` when implemented)

- `oob-didexchange-webvh-didcomm`
- `issue-webvh`

**Verify and revoke**

- `verify-webvh`
- `revoke-webvh`
- `verify-webvh-post-revoke`

**Other**

- `issue-indy`

Phases not yet implemented log "not implemented yet" and return success.

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

The checked-in **`.env.example`** only comments `WEBVH_CREATE_ALIAS` under optional WebVH settings; all other optional variables below are still supported when set in `.env` or the shell.

Required:

- `TRACTION_TENANT_PROXY_BASE` (default: `https://traction-sandbox-tenant-proxy.apps.silver.devops.gov.bc.ca`; use `http://localhost:8032` for a local stack)
- `TRACTION_ISSUER_TENANT_TOKEN`
- `TRACTION_HOLDER_TENANT_TOKEN`

Optional (WebVH / wallet upgrade):

- `WEBVH_WALLET_UPGRADE_POLL_SEC` (default `2`) — poll interval after `POST /anoncreds/wallet/upgrade`
- `WEBVH_WALLET_UPGRADE_TIMEOUT_SEC` (default `120`) — max wait for `askar-anoncreds`
- `WEBVH_WITNESS_INVITATION` — full `witness_invitation` string for `POST /did/webvh/configuration` (skips unauthenticated fetch from the WebVH server)
- `WEBVH_CREATE_NAMESPACE` (default `traction-e2e`) — `POST /did/webvh/create` `options.namespace`
- `WEBVH_CREATE_ALIAS` — fixed `options.identifier` (default: random 8-char value when unset)
- `WEBVH_CREATE_IDENTIFIER` — same as `WEBVH_CREATE_ALIAS` (fixed `options.identifier`)
- `WEBVH_WITNESS_THRESHOLD` (default `0`, omitted from requests) — when set to a **positive** integer, adds `options.witness_threshold` on create and `parameter_options.witness_threshold` on configure
- `WEBVH_CREATE_APPLY_POLICY` — set to `0` / `false` / `no` / `off` to send `apply_policy: false` (omit server policy merge; default in harness is **on** / `true`)

## Profiles

- `all` (default): all registered phases (including placeholders)
- `new-issuer-webvh`: WebVH-named path from `smoke` through `verify-webvh-post-revoke`

## Usage

From `scripts/webvh-e2e`:

```bash
poetry run python3 run.py
poetry run python3 run.py --profile new-issuer-webvh
poetry run python3 run.py --profile all -v
poetry run python3 run.py --profile new-issuer-webvh --witness
```

