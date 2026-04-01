# WebVH end-to-end harness

This directory contains the Traction WebVH E2E harness entrypoint and phase registry.

Current runtime behavior:
- working CLI (`run.py`)
- profile/phase registry (`phases/smoke.py` liveness, `phases/webvh.py` WebVH configure/create, `phases/connect.py` OOB + DID Exchange, `phases/setup.py` AnonCreds schema/cred-def, issue/verify/revoke)
- environment + token wiring
- smoke phase (`GET /status/live`, `GET /tenant/wallet` for issuer and holder)
- issuer wallet upgrade, WebVH configure, `webvh-create`, **AnonCreds schema + cred-def with revocation**, **DIDComm connection using public `did:webvh`**, **issue-credential-2.0**, **present-proof-2.0**, **revocation**, second proof expecting failure

## Current scope

### Implemented
- `smoke` phase calls `GET /status/live` and authenticated `GET /tenant/wallet` (issuer + holder)
- `upgrade-anoncreds-wallet`: `GET /tenant/wallet` for `settings.wallet.name` and type (ACA-Py `GET /settings` omits `wallet.name`), optional `POST /anoncreds/wallet/upgrade`, poll until `askar-anoncreds`
- `configure-webvh-plugin`: `GET /tenant/server/status/config` (controller defaults only), optional `WEBVH_WITNESS_INVITATION` or fetch `/api/invitations` on the WebVH server, `POST /did/webvh/configuration` with **request** / **response** logged (pretty JSON; logs shorten `witness_invitation` and replace `scids` with `{}`). Merges stored `parameter_options` from `GET /did/webvh/configuration`; sets `witness_threshold` only when `WEBVH_WITNESS_THRESHOLD` is positive, and **drops** any merged `witness_threshold` when it is not (avoids echoing an old stored value)
- `webvh-create`: `POST /did/webvh/create` with `options` (`namespace`, `identifier` for the path segment, **`didcomm: true`**, optional `witness_threshold` when env is positive, optional `server_url` from stored config or context). Default identifier is **8** random `[a-z0-9]` characters (env `WEBVH_CREATE_ALIAS` / `WEBVH_CREATE_IDENTIFIER`). Sends **`apply_policy: true`** by default (merge with WebVH server identifier policy; matches ACA-Py). Set `WEBVH_CREATE_APPLY_POLICY=false` to skip policy merge. Sets `ctx.webvh_last_created_did` when the response includes a `did:webvh` id
- `publish-schema-webvh` / `publish-cred-def-webvh`: `POST /anoncreds/schema` then `POST /anoncreds/credential-definition` with **`support_revocation: true`** and **`revocation_registry_size`** (default **4**, env `WEBVH_E2E_REVOCATION_REGISTRY_SIZE`). Idempotent when the same schema/cred-def already exists for the WebVH issuer DID
- `oob-didexchange-webvh-didcomm`: issuer `POST /wallet/did/public` (WebVH DID), `POST /out-of-band/create-invitation` with **`use_public_did: true`** and DID Exchange 1.1; holder `POST /out-of-band/receive-invitation` (`auto_accept`); polls until issuer has a new **active** connection
- `issue-webvh`: `POST /issue-credential-2.0/send-offer` (anoncreds filter, `auto_issue`); holder `POST …/send-request`; polls until issuer exchange is **done**
- `verify-webvh` / `verify-webvh-post-revoke`: `POST /present-proof-2.0/send-request` with anoncreds **non-revocation interval**, holder `POST …/send-presentation`; first round expects **verified**; after `revoke-webvh`, second round expects **not verified** (or **abandoned**)
- `revoke-webvh`: `POST /anoncreds/revocation/revoke` with **`cred_ex_id`** from issuance and **`publish: true`**
- context loading from `.env` and shell env
- required issuer/holder token validation at startup
- profile execution and end-of-run **summary** (indented `run` + `webvh` sections: `traction_url`; after create, full `did:webvh:…` and **explorer** link `{server_url}/api/explorer/dids?scid=…` when a DID is present)
- `--witness`: adds `endorsement: true` to the WebVH configure POST (endorser-style flow)

### Not implemented yet

- `issue-indy` (placeholder only)

Phases that are not implemented log a short message and return success.

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

Optional (full issuance / proof flow — see phases above):

- `WEBVH_E2E_SCHEMA_NAME` (default `WebVHE2EHarness`) — AnonCreds schema name
- `WEBVH_E2E_SCHEMA_VERSION` (default `1.0`)
- `WEBVH_E2E_SCHEMA_ATTRS` (default `name,score`) — comma-separated attribute names (must match preview + proof request)
- `WEBVH_E2E_CRED_DEF_TAG` (defaults to schema name) — cred-def tag
- `WEBVH_E2E_REVOCATION_REGISTRY_SIZE` (default `4`) — AnonCreds revocation registry size on cred-def
- `WEBVH_E2E_CRED_VALUES` — optional JSON object of attribute values for the offer, e.g. `{"name":"Alice","score":"99"}` (defaults: `name` / `score` sample strings)
- `WEBVH_E2E_HOLDER_CONNECTION_ALIAS` (default `webvh-e2e-holder`) — holder alias for `receive-invitation`
- `WEBVH_E2E_CONNECTION_POLL_SEC` / `WEBVH_E2E_CONNECTION_TIMEOUT_SEC` — DID Exchange polling (defaults `2` / `120`)
- `WEBVH_E2E_ISSUE_POLL_SEC` / `WEBVH_E2E_ISSUE_TIMEOUT_SEC` — credential issue polling (defaults `2` / `180`)
- `WEBVH_E2E_PROOF_POLL_SEC` / `WEBVH_E2E_PROOF_TIMEOUT_SEC` — presentation polling (defaults `2` / `180`)

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

