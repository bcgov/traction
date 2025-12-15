# Traction did:webvh Workshop

This workshop walks through configuring the did:webvh plugin and creating a did:webvh identifier in a Traction tenant. The flow uses the existing Traction sandbox and ACA-Py containers, and assumes you already have the services running locally via `scripts/manage start`.

## Prerequisites

- Traction stack running locally (`scripts/manage start`)
- Browser access to the Tenant UI (default `http://localhost:8080`)
- Tenant API key generated during onboarding
- curl (or similar) available for API calls

## 1. Inspect the did:webvh plugin configuration

The Traction agent exposes plugin configuration through the server config endpoint. Confirm the controller exposes a did:webvh entry by running:

```bash
curl -H "X-API-Key: <tenant_api_key>" \
  http://localhost:8032/tenant/server/status/config | jq '.config.plugin_config["did-webvh"] // .config.plugin_config.webvh'
```

If the response includes something like:

```json
{
  "server_url": "https://sandbox.bcvh.vonx.io",
  "witnesses": [
    "did:key:z6MkfJ2Sb5fW7pb3xiv4Cr5Utvr6XugtF1QT7ZTfdP8P3c6d"
  ],
  "witness": true
}
```

you are ready to configure the tenant. If this object is missing, update `scripts/plugin-config.yml` and restart the stack so the controller loads the plugin defaults.

## 2. Seed tenant configuration (optional)

The Tenant UI now offers a “Connect” button for the did:webvh entry on the Profile → Issuer page. Clicking the button issues a single POST to `/did/webvh/configuration` using the server URL and witness list from the controller configuration. You can also perform this step via curl:

```bash
curl -X POST http://localhost:8032/did/webvh/configuration \
  -H "X-API-Key: <tenant_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
        "server_url": "https://sandbox.bcvh.vonx.io",
        "witness": true,
        "witnesses": [
          "did:key:z6MkfJ2Sb5fW7pb3xiv4Cr5Utvr6XugtF1QT7ZTfdP8P3c6d"
        ]
      }'
```

A 200 response indicates the tenant configuration is stored. Subsequent GETs to `/did/webvh/configuration` should return the same payload.

## 3. Register the did:webvh server in the Issuer UI

Navigate to **Profile → Issuer** in the Tenant UI. At the top of the ledger table you will now see a row similar to:

| Connect | Ledger             | Alias               | Method | Writable |
|---------|--------------------|---------------------|--------|----------|
| (button)| `sandbox.bcvh.vonx.io` | `sandbox.bcvh.vonx.io` | `webvh` | ✔ |

Clicking the button triggers the configuration helper (step 2). Once configured, the button shows success feedback. No Aries connection is created for the webvh ledger; it simply primes ACA-Py with the correct witnesses.

## 4. Create a did:webvh identifier

Go to **Identifiers** in the sidebar. The did:webvh configuration section shows the server URL and witness status. Click “Create DID” and fill in:

- **Server URL** – auto-populated with the configured value (select from the dropdown if more are added in future).
- **Alias** – a unique label for the identifier (e.g., `demo-alias`).
- **Namespace** – optional, defaults to `default`.

Submit the form. The Tenant UI sends a POST to `/did/webvh/create` with the alias, namespace, server URL, and witness list. ACA-Py returns the identifier request immediately; the identifiers table reflects the new entry once the witness attests.

## 5. Verify identifiers

Use the Identifiers table to view existing did:webvh entries. Each row provides:

- Namespace
- Alias
- Status (Pending/Active/Error)
- Created timestamp
- DID string (copyable)

Pending entries flip to Active once the witness attestation completes. If an entry remains pending, check the ACA-Py logs (`scripts/manage logs traction-agent`) to ensure the witness endpoint is reachable.

## 6. Troubleshooting tips

- **Missing configuration:** The Identifiers page shows a yellow warning if the controller can’t find witnesses. Use the Profile button or curl command to seed the config.
- **404 on create:** Indicates the tenant has not stored the configuration. Re-run the configure step.
- **Witness errors:** Inspect ACA-Py logs. The usual causes are incorrect witness DID or networking issues.
- **Multiple servers:** When the controller exports more than one did:webvh entry, the dropdown in the modal lists them automatically.

## 7. Next steps

- Export the did:webvh identifier using the ACA-Py admin API or the Witness dashboard.
- Automate tenant creation by POSTing both `/multitenancy/wallet` and `/did/webvh/configuration` in your provisioning script.
- Explore the didwebvh-ts project (under `../didwebvh-ts`) for utilities to publish witness statements or host verified history documents.

Happy configuring!
