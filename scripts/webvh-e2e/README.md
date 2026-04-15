# WebVH end-to-end harness

This directory contains the Traction WebVH E2E harness entrypoint and phase registry.

Current runtime behavior:
- working CLI (`run.py`)
- profile/phase registry (`phases/smoke.py` liveness, `phases/webvh.py` WebVH configure/create, `phases/connect.py` OOB + DID Exchange, `phases/setup.py` AnonCreds schema/cred-def, `phases/indy.py` Indy endorser + public DID on BCovrin test, issue/verify/revoke)
- environment + token wiring
- smoke phase (`GET /status/live`, `GET /tenant/wallet` for issuer and holder)
- issuer wallet upgrade, WebVH configure, `webvh-create`, **AnonCreds schema + cred-def with revocation**, **DIDComm connection using public `did:webvh`**, **issue-credential-2.0**, **present-proof-2.0**, **revocation**, second proof expecting failure

## Current scope

### Implemented
- `smoke` phase calls `GET /status/live` and authenticated `GET /tenant/wallet` (issuer + holder)
- `upgrade-anoncreds-wallet`: `GET /tenant/wallet` for `settings.wallet.name` and type (ACA-Py `GET /settings` omits `wallet.name`), optional `POST /anoncreds/wallet/upgrade`, poll until `askar-anoncreds`
- `configure-webvh-plugin`: `GET /tenant/server/status/config` (controller defaults only), optional `WEBVH_WITNESS_INVITATION` or fetch `/api/invitations` on the WebVH server, `POST /did/webvh/configuration` (INFO logs the sanitized **request** body; full **responses** and other HTTP bodies only with `run.py -v` / debug logging). Merges stored `parameter_options` from `GET /did/webvh/configuration`; sets `witness_threshold` only when `WEBVH_WITNESS_THRESHOLD` is positive, and **drops** any merged `witness_threshold` when it is not (avoids echoing an old stored value)
- `webvh-create`: `POST /did/webvh/create` with `options` (`namespace`, `identifier` for the path segment, **`didcomm: true`**, optional `witness_threshold` when env is positive, optional `server_url` from stored config or context). Default identifier is **8** random `[a-z0-9]` characters (env `WEBVH_CREATE_ALIAS` / `WEBVH_CREATE_IDENTIFIER`). Sends **`apply_policy: true`** by default (merge with WebVH server identifier policy; matches ACA-Py). Set `WEBVH_CREATE_APPLY_POLICY=false` to skip policy merge. Sets `ctx.webvh_last_created_did` when the response includes a `did:webvh` id
- `publish-schema-webvh` / `publish-cred-def-webvh`: `POST /anoncreds/schema` then `POST /anoncreds/credential-definition` with **`support_revocation: true`** and **`revocation_registry_size`** (default **4** in `constants.py`). Idempotent when the same schema/cred-def already exists for the WebVH issuer DID. Schema/cred-def **responses** are debug-only (`-v`); INFO logs HTTP status lines and published ids
- `oob-didexchange-webvh-didcomm`: issuer `POST /out-of-band/create-invitation` with **`use_did`** set to the wallet’s **`did:webvh`** (no `POST /wallet/did/public` — that is Indy public-DID/endorser, not this flow) and DID Exchange 1.1; holder `POST /out-of-band/receive-invitation` (`auto_accept`); polls issuer-side OOB record / connection list until the exchange is **active** or **completed**
- `issue-webvh`: `POST /issue-credential-2.0/send-offer` (anoncreds filter, `auto_issue`); holder `POST …/send-request`; polls until issuer exchange is **done**
- `verify-webvh` / `verify-webvh-post-revoke`: `POST /present-proof-2.0/send-request` with anoncreds **non-revocation interval**, holder `POST …/send-presentation`; first round expects **verified**; after `revoke-webvh`, second round expects **not verified** (or **abandoned**)
- `revoke-webvh`: `POST /anoncreds/revocation/revoke` with **`rev_reg_id` / `cred_rev_id`** when present (else **`cred_ex_id`**); **`publish`** / **`notify`** from `constants.py` (defaults: publish on, holder notify off)
- context loading from `.env` and shell env
- required issuer/holder token validation at startup
- profile execution and end-of-run **summary** (indented `run` + `webvh` sections: `traction_url`; after create, full `did:webvh:…` and BCVH-style **explorer** links `{server_url}/api/explorer/dids?scid=…` and `{server_url}/api/explorer/resources?scid=…` when a DID is present — e.g. [resources for an SCID](https://sandbox.bcvh.vonx.io/api/explorer/resources?scid=QmRZdh2ivaQNv9YkEnSqDsbk2Vhz6TQJWSbCF95zCVfNnb))
- `--witness`: adds `endorsement: true` to the WebVH configure POST (endorser-style flow)
- **Indy (BCovrin test)** — profile `indy-bcovrin-e2e` (see below; `indy-bcovrin-setup` is an alias): **`smoke`** (polls **`GET /tenant/wallet`** through 503 upgrade), **`upgrade-anoncreds-wallet`** (issuer), ledger + endorser + public DID + **`publish-schema-indy` / `publish-cred-def-indy`** (same anoncreds revocation options as WebVH; **unqualified** Indy `issuerId` / `schemaId` for resolver compatibility), then **`oob-didexchange-indy-didcomm`**: OOB + DID Exchange 1.1 with **`use_public_did: true`** (wallet ledger public DID; do not pass a short **`use_did`** — invalid `services` and **422** on receive), distinct OOB/holder aliases from the WebVH path (`constants.py`), then **`issue-indy` / `verify-indy` / `revoke-indy` / `verify-indy-post-revoke`** — same **`anoncreds`** filters and proof shape as the WebVH phases, using `ctx.indy_cred_def_id`.

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

The checked-in **`.env.example`** comments optional WebVH create settings; other optional variables below work when set in `.env` or the shell.

**Tuning** (schema/cred-def, preview attributes, polling intervals, revoke flags, wallet-upgrade wait): edit **`constants.py`** — not environment variables. **`E2E_SMOKE_WALLET_READY_*`** / **`E2E_SMOKE_WALLET_POST_READY_SETTLE_SEC`** control smoke polling through **`GET /tenant/wallet`** 503s and optional settle after both wallets are OK (the settle is **skipped** when issuer and holder are already **`askar-anoncreds`**). Indy E2E builds a **fresh cred-def tag each run** (`E2E_INDY_CRED_DEF_TAG_PREFIX` + random hex) so **`publish-cred-def-indy`** always creates a new definition and does not hit duplicate-tag **400** from a prior run.

**Logging:** At INFO, `TractionClient` logs the full JSON body of each POST except `POST /did/webvh/configuration` (that one is sanitized). Issue and proof requests can include attribute values—treat default logs as potentially sensitive in shared CI or support channels.

Required:

- `TRACTION_TENANT_PROXY_BASE` (default: `https://traction-sandbox-tenant-proxy.apps.silver.devops.gov.bc.ca`; use `http://localhost:8032` for a local stack)
- `TRACTION_ISSUER_TENANT_TOKEN`
- `TRACTION_HOLDER_TENANT_TOKEN`

Optional (WebVH):

- `WEBVH_WITNESS_INVITATION` — full `witness_invitation` string for `POST /did/webvh/configuration` (skips unauthenticated fetch from the WebVH server)
- `WEBVH_CREATE_NAMESPACE` (default `traction-e2e`) — `POST /did/webvh/create` `options.namespace`
- `WEBVH_CREATE_ALIAS` — fixed `options.identifier` (default: random 8-char value when unset)
- `WEBVH_CREATE_IDENTIFIER` — same as `WEBVH_CREATE_ALIAS` (fixed `options.identifier`)
- `WEBVH_WITNESS_THRESHOLD` (default `0`, omitted from requests) — when set to a **positive** integer, adds `options.witness_threshold` on create and `parameter_options.witness_threshold` on configure
- `WEBVH_CREATE_APPLY_POLICY` — set to `0` / `false` / `no` / `off` to send `apply_policy: false` (omit server policy merge; default in harness is **on** / `true`)

Optional (Indy / BCovrin test — profile `indy-bcovrin-e2e`):

- `E2E_INDY_WRITE_LEDGER_ID` — ledger id for `PUT /ledger/…/set-write-ledger` (default **`bcovrin-test`** in `constants.py` if unset)
- `E2E_INDY_REGISTER_NYM_ALIAS` — optional alias for `POST /ledger/register-nym` (default: tenant `tenant_name` / `wallet_id` from `GET /tenant`, else `webvh-e2e-indy`)

**Issuer tenant requirements for Indy:** the Innkeeper tenant must be allowed to connect to endorsers and create a public DID on the target ledger (same as the Tenant UI “Issuance” prerequisites). Otherwise `POST /tenant/endorser-connection` returns **400** (“not configured as an issuer”).

## Profiles

- `all` (default): same phases as **`new-issuer-webvh`** (WebVH end-to-end only)
- `new-issuer-webvh`: WebVH path from `smoke` through `verify-webvh-post-revoke`
- `indy-bcovrin-e2e`: Full Indy path on BCovrin test — smoke (wallet readiness + optional settle in `constants.py`), issuer **`upgrade-anoncreds-wallet`**, ledger, endorser, public DID, anoncreds schema/cred-def, **DIDComm over Indy public DID**, issue / verify / revoke / verify-after-revoke (holder token required). **`indy-bcovrin-setup`** is the same phases (legacy name).

## Usage

From `scripts/webvh-e2e`:

```bash
poetry run python3 run.py
poetry run python3 run.py --profile new-issuer-webvh
poetry run python3 run.py --profile all -v
poetry run python3 run.py --profile new-issuer-webvh --witness
poetry run python3 run.py --profile indy-bcovrin-e2e
```

