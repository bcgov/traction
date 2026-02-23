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
- `acapy.plugins.*`
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

- `acapy.argfile.yml.label` (now handled automatically)
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

## 0.5.0

The Traction Helm chart has been updated to use version `1.0.0` of the [ACA-Py Helm chart](https://github.com/openwallet-foundation/helm-charts/tree/main/charts/acapy). The primary breaking change is the replacement of the Bitnami `postgresql` sub-dependency with the [CloudPirates `postgres` chart](https://github.com/CloudPirates-io/helm-charts).

### What Changed

| | Traction 0.4.x (acapy 0.2.3) | Traction 0.5.0 (acapy 1.0.0) |
| --- | --- | --- |
| Postgres provider | Bitnami `postgresql` | CloudPirates `postgres` |
| Values key | `acapy.postgresql.*` | `acapy.postgres.*` |
| Postgres service name | `<release>-acapy-postgresql` | `<release>-acapy-postgres` |
| Consolidated DB secret | `<release>-acapy-postgresql` | `<release>-acapy-postgres` |
| Postgres version | 16 | 18 |
| OpenShift compatibility | Manual (`podSecurityContext.enabled: false`) | Auto-detected via `route.openshift.io/v1` API group |

### Values Migration

#### Disabling the Embedded Postgres (External Database)

**Before:**

```yaml
acapy:
  postgresql:
    enabled: false
```

**After:**

```yaml
acapy:
  postgres:
    enabled: false
```

#### Customising the Embedded Postgres

If you were overriding Bitnami postgres settings such as storage size or resources:

**Before:**

```yaml
acapy:
  postgresql:
    primary:
      persistence:
        size: 5Gi
      resources:
        requests:
          cpu: 100m
          memory: 256Mi
      extendedConfiguration: |
        max_connections = 500
```

**After:**

```yaml
acapy:
  postgres:
    persistence:
      size: 5Gi
    resources:
      requests:
        cpu: 100m
        memory: 256Mi
    config:
      postgresql:
        max_connections: 500
```

#### OpenShift Security Context

The CloudPirates postgres chart supports an explicit `targetPlatform` parameter. Set it to `openshift` to automatically omit `runAsUser`, `runAsGroup`, and `fsGroup` from the pod and container security contexts, which is required for OpenShift's restricted SCC.

```yaml
acapy:
  postgres:
    targetPlatform: openshift
```

Any previous manual Bitnami security context overrides can be removed:

**Remove (no longer needed):**

```yaml
acapy:
  postgresql:
    primary:
      podSecurityContext:
        enabled: false
      containerSecurityContext:
        enabled: false
```

### Data Migration (Embedded Bitnami → CloudPirates Postgres)

> [!WARNING]
> Only follow this section if your deployment was using the **embedded Bitnami postgres** (`acapy.postgresql.enabled: true`, which was the default in 0.4.x). If you are using an external database, skip to [Disabling the Embedded Postgres](#disabling-the-embedded-postgres-external-database) above and update the values key.
> Back up your data before proceeding and test this procedure in a non-production environment first.

The Helm chart upgrade replaces the Bitnami postgres `StatefulSet` with a new CloudPirates postgres `StatefulSet` that starts with an **empty database**. Wallet data must be migrated manually using a dump-and-restore approach. The `pg_dumpall` logical format is used here, which is forward-compatible from Postgres 16 to Postgres 18.

#### Step 1: Scale Down ACA-Py

Stop ACA-Py to prevent writes during migration:

```bash
kubectl scale deployment <release>-acapy --replicas=0 -n <namespace>
# Wait for the pod to terminate
kubectl get pods -n <namespace> -w
```

#### Step 2: Dump All Databases from the Bitnami Pod

The Bitnami pod will be named `<release>-acapy-postgresql-0`. Use `pg_dumpall` to capture the full cluster. The `--no-role-passwords` flag is used because role passwords will be managed by the new chart’s secrets.

```bash
kubectl exec -n <namespace> <release>-acapy-postgresql-0 -- \
  pg_dumpall -U postgres --no-role-passwords \
  > /tmp/traction-wallet-backup.sql
```

Verify the dump is non-empty before proceeding:

```bash
wc -l /tmp/traction-wallet-backup.sql
```

#### Step 3: Upgrade the Helm Chart

```bash
helm upgrade <release> charts/traction \
  -f <your-values-file>.yaml \
  -n <namespace>
```

This deploys the CloudPirates postgres `StatefulSet` with an empty database. ACA-Py remains at 0 replicas.

#### Step 4: Wait for the New Postgres Pod to Be Ready

```bash
kubectl rollout status statefulset/<release>-acapy-postgres -n <namespace>
```

#### Step 5: Restore the Dump into the New Postgres Pod

Copy the backup into the new pod and restore it:

```bash
kubectl cp /tmp/traction-wallet-backup.sql \
  <namespace>/<release>-acapy-postgres-0:/tmp/traction-wallet-backup.sql

kubectl exec -n <namespace> <release>-acapy-postgres-0 -- \
  psql -U postgres -f /tmp/traction-wallet-backup.sql
```

> [!NOTE]
> `CREATE ROLE` statements may produce errors for roles that already exist (e.g. `acapy`). These errors are expected and safe to ignore — the role was pre-created by the CloudPirates chart’s init scripts.

#### Step 6: Ensure the `acapy` Role Has `CREATEDB`

ACA-Py uses the `DatabasePerWallet` scheme and creates a new database for each wallet at runtime. The `acapy` role must have the `CREATEDB` privilege:

```bash
kubectl exec -n <namespace> <release>-acapy-postgres-0 -- \
  psql -U postgres -c "ALTER ROLE acapy CREATEDB;"
```

Confirm the restored databases are visible:

```bash
kubectl exec -n <namespace> <release>-acapy-postgres-0 -- \
  psql -U postgres -c "\l"
```

#### Step 7: Scale ACA-Py Back Up

```bash
kubectl scale deployment <release>-acapy --replicas=1 -n <namespace>
```

Monitor the logs to confirm a successful database connection:

```bash
kubectl logs -n <namespace> -l app.kubernetes.io/component=agent -f
```

#### Step 8: Clean Up the Old Bitnami PVC

Once ACA-Py is confirmed operational, delete the PVC that was used by the old Bitnami pod:

```bash
# Identify the old PVC (typically named data-<release>-acapy-postgresql-0)
kubectl get pvc -n <namespace>

kubectl delete pvc data-<release>-acapy-postgresql-0 -n <namespace>
```

> [!CAUTION]
> Do not delete the old PVC until you have fully validated that ACA-Py is operating correctly against the restored data on the new postgres instance.
