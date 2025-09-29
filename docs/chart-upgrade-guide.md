# Traction Helm Chart Values Migration Guide

This document contains information related to breaking/major changes to the Traction Helm Chart and provides guidelines for migrating/upgrading deployments to newer chart versions.

## 0.4.0

The Traction Helm chart has been refactored to use the [ACA-Py Helm chart](https://github.com/openwallet-foundation/helm-charts/tree/main/charts/acapy) from the OpenWallet Foundation as a dependency, replacing the built-in ACA-Py templates. This change improves maintainability and alignment with the broader ACA-Py community.

### Migration Steps

> [!IMPORTANT]
> The following migration steps assume the upgrade target is a working deployment of Traction using version `0.3.8` of the chart. Upgrades from previous versions have not been tested.

#### Update Global Configuration

```yaml
# Move ingressSuffix to global section
global:
  ingressSuffix: -dev.example.com # Move from root level
```

#### Update ACA-Py Image Configuration

```yaml
acapy:
  image:
    registry: ghcr.io # Add registry field
    repository: bcgov/traction-plugins-acapy # Remove registry prefix
    # ... keep other image settings
```

#### Update Service Port Configuration

```yaml
acapy:
  service:
    ports:
      http: 8021 # Update from httpPort: 8030
      admin: 8022 # Update from adminPort: 8031
      ws: 8023 # Add websocket port if needed
```

#### Convert Plugin Configuration

> [!NOTE]
> Plugins are now configured directly as CLI arguments, replace the `plugins` section with `extraArgs`

```yaml
acapy:
  extraArgs:
    - --plugin 'aries_cloudagent.messaging.jsonld'
    - --plugin traction_plugins.traction_innkeeper.v1_0
    - --plugin multitenant_provider.v1_0
    - --plugin basicmessage_storage.v1_0
    - --plugin connections
    - --plugin connection_update.v1_0
    - --plugin rpc.v1_0
    - --plugin webvh
```

#### Update Secrets Configuration

```yaml
acapy:
  secrets:
    api:
      retainOnUninstall: true
      existingSecret: "" # Update from acapy.secret.adminApiKey.existingSecret
      secretKeys:
        adminApiKey: adminApiKey
        jwtKey: jwt
        walletKey: walletKey
        webhookapiKey: webhookapi
```

#### Update Multitenancy Configuration

```yaml
acapy:
  argfile.yml:
    multitenancy-config:
      - wallet_type=single-wallet-askar # Simplified array format
```

#### Remove Obsolete Configurations

Remove these sections from your values file:

- `postgresql.*`
- `acapy.walletStorageConfig.*`
- `acapy.walletStorageCredentials.*`
- `acapy.multitenancyConfiguration.*`
- `acapy.plugins.*`
- `acapy.persistence.*`
- `acapy.secret.*` (replaced with `acapy.secrets.*`)

#### Update UI Configuration

```yaml
ui:
  pluginInnkeeper: # New section for innkeeper config
    existingSecret: ""
  smtp:
    existingSecret: "" # Move from root level existingSecret
```

> [!WARNING]
>
> 1. **Port Changes:** The default ACA-Py service ports have changed from 8030/8031 to 8021/8022. Update any external configurations accordingly.
>
> 2. **Database Configuration:** PostgreSQL configuration is now handled by the ACA-Py chart dependency, not directly in the Traction chart.
>
> 3. **Secret Structure:** Secret configuration has been restructured. Review your secret management approach.
>
> 4. **Plugin Configuration:** Plugins are now configured via command-line arguments rather than a dedicated plugins section.
>
> 5. **Resource Configuration:** Some resource limit configurations have been simplified to requests-only in the new structure.
>
> 6. **Template Changes:** Since ACA-Py templates are now provided by the dependency chart, any custom template modifications will need to be reconsidered.

<details>

<summary>Detailed list of changes for 0.4.0</summary>

### Chart.yaml Dependencies

**Old Structure (v0.3.8):**

```yaml
dependencies:
  - name: postgresql
    version: 11.9.13
    repository: https://charts.bitnami.com/bitnami/
    condition: postgresql.enabled
  - name: common
    repository: "https://charts.bitnami.com/bitnami"
    version: 2.x.x
```

**New Structure (v0.4.0+):**

```yaml
dependencies:
  - name: acapy
    version: 0.2.3
    repository: https://openwallet-foundation.github.io/helm-charts/
  - name: common
    repository: "https://charts.bitnami.com/bitnami"
    version: 2.31.3
```

### Values.yaml Structural Changes

#### Global Section (NEW)

**New Section:**

```yaml
global:
  imageRegistry: ""
  imagePullSecrets: []
  ingressSuffix: -dev.example.com
  defaultStorageClass: ""
  security:
    allowInsecureImages: false
  compatibility:
    openshift:
      adaptSecurityContext: auto
```

**Migration Required:**

- Move `ingressSuffix` from root level to `global.ingressSuffix`

#### ACA-Py Configuration Changes

**Old Agent Image Configuration:**

```yaml
acapy:
  image:
    repository: ghcr.io/bcgov/traction-plugins-acapy
    pullPolicy: IfNotPresent
    pullSecrets: []
    tag: ""
```

**New Agent Image Configuration:**

```yaml
acapy:
  image:
    registry: ghcr.io # NEW: separate registry field
    repository: bcgov/traction-plugins-acapy # CHANGED: no registry prefix
    pullPolicy: IfNotPresent
    pullSecrets: []
    tag: ""
    digest: "" # NEW: digest support
```

#### Configuration Files

**Removed Sections:**

- `acapy.argfile.yml.genesis-transactions-list` (replaced with `ledgers.yml`)
- `acapy.argfile.yml.label` (now handled automatically)
- `acapy.walletStorageConfig.*` (moved to ACA-Py chart)
- `acapy.walletStorageCredentials.*` (moved to ACA-Py chart)
- `acapy.multitenancyConfiguration.*` (moved to ACA-Py chart)
- `acapy.plugins.*` (replaced with `extraArgs`)

**New/Changed Sections:**

```yaml
acapy:
  argfile.yml:
    # REMOVED: genesis-transactions-list: /home/aries/ledgers.yml
    # REMOVED: label: '{{ include "acapy.label" .}}'
    multitenancy-config: # NEW: array format instead of complex config
      - wallet_type=single-wallet-askar
    webhook-url: "" # NEW: explicit webhook URL field
```

#### Plugin Configuration Changes

**Old Structure:**

```yaml
acapy:
  plugins:
    basicmessageStorage: true
    connectionUpdate: true
    multitenantProvider: true
    tractionInnkeeper: true
    rpc: true
```

**New Structure:**

```yaml
acapy:
  extraArgs: # Plugins now configured directly as CLI arguments
    - --plugin 'aries_cloudagent.messaging.jsonld'
    - --plugin traction_plugins.traction_innkeeper.v1_0
    - --plugin-config-value traction_innkeeper.innkeeper_wallet.tenant_id="$(INNKEEPER_WALLET_TENANT_ID)"
    - --plugin-config-value traction_innkeeper.innkeeper_wallet.wallet_key="$(INNKEEPER_WALLET_WALLET_KEY)"
    - --plugin multitenant_provider.v1_0
    - --plugin basicmessage_storage.v1_0
    - --plugin connections
    - --plugin connection_update.v1_0
    - --plugin rpc.v1_0
    - --plugin webvh
```

#### Service Configuration

**Old Structure:**

```yaml
acapy:
  service:
    type: ClusterIP
    adminPort: 8031
    httpPort: 8030
```

**New Structure:**

```yaml
acapy:
  service:
    ports:
      http: 8021 # CHANGED: port number and structure
      admin: 8022 # CHANGED: port number and structure
      ws: 8023 # NEW: websocket port
```

#### Secrets Configuration

**Old Structure:**

```yaml
acapy:
  secret:
    adminApiKey:
      existingSecret: ""
      generated: true
      value: ""
    walletKey:
      existingSecret: ""
    pluginInnkeeper:
      existingSecret: ""
      generated: true
      walletkey: ""
      tenantid: ""
```

**New Structure:**

```yaml
acapy:
  secrets:
    api:
      retainOnUninstall: true
      existingSecret: ""
      secretKeys:
        adminApiKey: adminApiKey
        jwtKey: jwt
        walletKey: walletKey
        webhookapiKey: webhookapi
    seed:
      enabled: false
```

#### Network and Ingress Changes

**New Additions:**

```yaml
acapy:
  ingress: # NEW: ACA-Py specific ingress (disabled by default)
    agent:
      enabled: false
      hostname: ""
    admin:
      enabled: false
      hostname: ""

  agentUrl: "" # NEW: override URLs
  adminUrl: "" # NEW: override URLs

  extraEnvVars: [] # NEW: environment variables
  extraEnvVarsCM: "" # NEW: ConfigMap for env vars
  extraEnvVarsSecret: "" # NEW: Secret for env vars

  websockets: # NEW: WebSocket support
    enabled: false
```

#### Removed Sections

**Sections No Longer Available:**

- `acapy.persistence.*` (handled by ACA-Py chart)
- `acapy.openshift.adminRoute.*` (simplified routing)
- Most resource limit configurations (now use requests only)

### 3. Tenant UI Configuration Changes

#### SMTP Configuration Changes

**Old Structure:**

```yaml
ui:
  existingSecret: "" # Root level secret
  smtp:
    # ... smtp config
```

**New Structure:**

```yaml
ui:
  pluginInnkeeper: # NEW: separate innkeeper config
    existingSecret: ""
  smtp:
    existingSecret: "" # NEW: SMTP-specific secret
    # ... smtp config
```

#### New UI Features

**New Sections:**

```yaml
ui:
  showOIDCReservationLogin: false # NEW: OIDC reservation login
  lokiUrl: "" # NEW: Loki logging endpoint
```

### 4. PostgreSQL Removal

**Major Change:** The PostgreSQL subchart dependency has been removed. Database configuration is now handled through the ACA-Py chart dependency.

**Removed Section:**

```yaml
postgresql:
  enabled: true
  # ... entire postgresql configuration
```

</details>
