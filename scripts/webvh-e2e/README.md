# WebVH end-to-end harness

Scripted checks against the **Traction tenant proxy** for **did:webvh** flows. Supports a local stack (`scripts/manage start`) or any deployment where you have a tenant JWT / API key.

Tracks [bcgov/DITP#136](https://github.com/bcgov/DITP/issues/136) (comprehensive WebVH-in-Traction testing). Human walkthrough: [Traction did:webvh Workshop](../../docs/traction-webvh-workshop.md).

## Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation) 1.8+ (uses `package-mode = false` for a script-only project)
- Tenant proxy reachable (default `http://localhost:8032`)
- **Authentication** (one of):
  - `TRACTION_TENANT_TOKEN` — wallet JWT used as `Authorization: Bearer …` (same as Tenant UI), **or**
  - `TRACTION_TENANT_API_KEY` — `X-API-Key` (see workshop examples)

## Setup

```bash
cd scripts/webvh-e2e
poetry install
cp .env.example .env
# Edit .env: set TRACTION_TENANT_TOKEN or TRACTION_TENANT_API_KEY (and proxy URL if needed)
```

`run.py` loads **`.env`** from this directory automatically (via `python-dotenv`). Values already set in your shell are not overwritten. **Do not commit `.env`** — it is listed in `.gitignore`.

Run the harness via Poetry’s env:

```bash
poetry run python3 run.py --phase all
```

**`--witness`** — include `witnesses` and `witness: {threshold: 1}` in `POST /did/webvh/create` (Tenant UI style). **Default is off** (create omits witness fields).

## Phases

| Phase | What it does |
|-------|----------------|
| `smoke` | `GET /status/live`; optional tenant config fetch if token set |
| `webvh-plugin` | `GET /tenant/server/status/config` — assert `webvh` / `did-webvh` plugin defaults exist |
| `webvh-configure` | `POST /did/webvh/configuration` (witness invitation or simple server/witness payload) |
| `webvh-create` | `POST /did/webvh/create` — create a did:webvh identifier; use **`--witness`** to send witness fields (default: omit) |
| `issue-webvh` | *Planned* — schema / cred-def / issue / revoke on WebVH issuer |
| `issue-indy` | *Planned* — Indy issuance while WebVH is enabled |
| `verify` | *Planned* — presentation verification |
| `all` | `smoke`, `webvh-plugin`, `webvh-configure`, `webvh-create` (stops on first failure) |

## Configuration env vars

| Variable | Description |
|----------|-------------|
| `TRACTION_TENANT_PROXY_BASE` | Tenant proxy base URL (no trailing path). Default: `http://localhost:8032` |
| `TRACTION_TENANT_TOKEN` | Bearer token for tenant API |
| `TRACTION_TENANT_API_KEY` | If set, sent as `X-API-Key` instead of Bearer |
| `WEBVH_CONFIGURE_MODE` | `invitation` (default), `simple`, or `auto` (try invitation, then simple) |
| `WEBVH_WITNESS_INVITATION` | Optional full `didcomm://?oob=...` string; skips invitation fetch |
| `WEBVH_DID_ALIAS` | Alias for `webvh-create` (default includes random suffix) |
| `WEBVH_NAMESPACE` | Namespace for create (default `default`) |
| `WEBVH_SERVER_URL` | Override server URL for create/configure (else from server config) |

## Examples

```bash
# Liveness only (no token)
poetry run python run.py --phase smoke

# Confirm plugin defaults are published
poetry run python run.py --phase webvh-plugin

# Full automated path to create a WebVH DID
poetry run python run.py --phase all
```

## Sandbox / CI

Point `TRACTION_TENANT_PROXY_BASE` at your sandbox URL and supply a short-lived tenant token (in `.env` or the environment). Do not commit tokens or keys.
