# WebVH end-to-end harness

Scripted checks against the **Traction tenant proxy** for **did:webvh** flows. Supports a local stack (`scripts/manage start`) or any deployment where you have tenant JWTs.

Tracks [bcgov/DITP#136](https://github.com/bcgov/DITP/issues/136) (comprehensive WebVH-in-Traction testing). Human walkthrough: [Traction did:webvh Workshop](../../docs/traction-webvh-workshop.md).

## Scope and scenarios

**Profiles:**

- **`all`** (default): runs **every registered phase** in order, including **`issue-indy`** (placeholder until [DITP#136](https://github.com/bcgov/DITP/issues/136)).
- **`new-issuer-webvh`**: **new issuer, WebVH only** — full path through **issue**, **verify** (with **non_revoked**), **revoke**, and a **second verify** that must **not** verify (revocation). Skips the Indy placeholder.

**Scenarios we expect to add or clarify over time:**

| Scenario | Intent |
|----------|--------|
| **New issuer, WebVH only** | **`--profile new-issuer-webvh`** (focused CI / dev test). |
| **Full suite** | **`run.py`** with no args, or **`--profile all`** (default). |
| **Existing issuer** | Future profile with slimmer phases + env / discovery (not implemented yet). |
| **WebVH and Indy** | Future composition once Indy E2E exists; likely separate profiles or ordered bundles. |
| **OOB inviter DID** | Today: issuer OOB uses ACA-Py **`use_did`** with the **did:webvh** from `webvh-create` (not did:peer). Later: optional path for invitations tied to the wallet’s **public Indy** DID. |

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation) 1.8+ (uses `package-mode = false` for a script-only project)
- Tenant proxy reachable (default `http://localhost:8032`)
- **Authentication:** `TRACTION_ISSUER_TENANT_TOKEN` (issuer / WebVH tenant). For holder-side steps (`oob-didexchange-webvh-didcomm`, `issue-webvh`, `verify-webvh`, `verify-webvh-post-revoke`) you need **`TRACTION_HOLDER_TENANT_TOKEN`** — must differ from the issuer token (required for **`new-issuer-webvh`** and for **`all`** once execution reaches those phases).

## Setup

```bash
cd scripts/webvh-e2e
poetry install
cp .env.example .env
# Edit .env: set base URL and both tenant tokens (see .env.example)
```

`run.py` loads **`.env`** from this directory automatically (via `python-dotenv`). Values already set in your shell are not overwritten. **Do not commit `.env`** — it is listed in `.gitignore`.

**Poetry:** only **`pyproject.toml`** is tracked; **`poetry.lock`** is gitignored for this script bundle. Run **`poetry install`** as usual. For a reproducible lockfile locally, run **`poetry lock`** (optional). Dependencies include **[Rich](https://github.com/Textualize/rich)** for log lines and phase banners (replaces hand-rolled ANSI).

```bash
poetry run python3 run.py                              # default: profile all
poetry run python3 run.py --profile new-issuer-webvh   # WebVH new-issuer path only
```

**`--witness`** — include `witnesses` and `witness: {threshold: 1}` in `POST /did/webvh/create` (Tenant UI style). **Default is off** (create omits witness fields).

## Profiles

| Profile | Phases (order) |
|---------|----------------|
| **`all`** (default) | Same as **`new-issuer-webvh`**, then **`issue-indy`** — i.e. every row in **Phases** below, top to bottom. |
| **`new-issuer-webvh`** | `smoke` → `upgrade-anoncreds-wallet` → `configure-webvh-plugin` → `webvh-create` → `publish-schema-webvh` → `publish-cred-def-webvh` → `oob-didexchange-webvh-didcomm` → `issue-webvh` → `verify-webvh` → `revoke-webvh` → `verify-webvh-post-revoke` |

There is no **`--phase`** flag; pick a **profile** only. To run a single step during development, import the phase from **`phases`** (same names as the **`PHASES`** keys) in Python.

## Phases

Phase names use a **`-webvh`** suffix when the step is part of the WebVH AnonCreds path (issuer `did:webvh`, same tenant proxy). **`issue-indy`** is reserved for a future Indy-specific path (not implemented).

| Phase | What it does |
|-------|----------------|
| `smoke` | `GET /status/live`; tenant config when token is set |
| `upgrade-anoncreds-wallet` | Ensure issuer wallet is `askar-anoncreds` (upgrade if needed) |
| `configure-webvh-plugin` | `GET /tenant/server/status/config` (read `webvh` / `did-webvh` defaults), then `POST /did/webvh/configuration` (witness invitation or env override) |
| `webvh-create` | `POST /did/webvh/create` — create a **did:webvh** identifier; sets **`options.didcomm`** so the DID document includes a DIDComm service (default **on**; set `WEBVH_CREATE_DIDCOMM=0` to omit) |
| `publish-schema-webvh` | `POST /anoncreds/schema` with **WebVH** `issuerId` |
| `publish-cred-def-webvh` | `POST /anoncreds/credential-definition` (revocation on) for that schema |
| `oob-didexchange-webvh-didcomm` | Issuer **`POST /out-of-band/create-invitation`** with **`use_did`** = that run’s **did:webvh** (from `webvh-create`; override with `WEBVH_OOB_USE_DID`), then DID Exchange **active** with the holder — not a did:peer invitation |
| `issue-webvh` | Issue Credential **2.0** (AnonCreds) over that connection |
| `verify-webvh` | Present Proof **2.0** with **`non_revoked`** on requested attributes — must **verify** while the credential is still valid |
| `revoke-webvh` | **`POST /anoncreds/revocation/revoke`** using the issuer’s `cred_ex_id` from `issue-webvh` (polls credential-revocation record for ids); **`publish`** on by default |
| `verify-webvh-post-revoke` | Second present-proof round (again with **`non_revoked`**) — verifier must end **done** with **not verified** (revoked credential) |
| `issue-indy` | Placeholder — Indy issuance E2E **TBD** (use `issue-webvh` today); runs only under profile **`all`** |

## Configuration

**`.env.example`** only lists what you must set for a typical run: proxy base URL and **two tenant JWTs**. Phases, defaults (schema name, OOB aliases, revocation on cred-def, proof `non_revoked`, etc.) come from the harness and the **profile** you choose—no extra env required.

Optional **`WEBVH_*`** overrides (re-run helpers, witness URL, soft-fail on registry poll, etc.) can be set in `.env` or the shell when you need them; scan **`phases.py`** / phase docstrings for names, or extend the README if you document a common override.

| Variable | Description |
|----------|-------------|
| `TRACTION_TENANT_PROXY_BASE` | Tenant proxy base URL (no trailing slash). Default: `http://localhost:8032` |
| `TRACTION_ISSUER_TENANT_TOKEN` | Bearer JWT for the issuer tenant |
| `TRACTION_HOLDER_TENANT_TOKEN` | Second tenant JWT (required when running phases that use the holder tenant) |

## Examples

```bash
poetry run python3 run.py
poetry run python3 run.py --profile new-issuer-webvh
poetry run python3 run.py --profile all -v
```

## Sandbox / CI

Point `TRACTION_TENANT_PROXY_BASE` at your sandbox URL and use short-lived JWTs. Do not commit tokens.
