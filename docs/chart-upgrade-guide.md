# Traction Helm Chart Values Migration Guide

This document contains information related to breaking/major changes to the Traction Helm Chart and provides guidelines for migrating/upgrading deployments to newer chart versoins.

## 0.4.0

The Traction Helm chart has been refactored to use the [ACA-Py Helm chart](https://github.com/openwallet-foundation/helm-charts/tree/main/charts/acapy) from the OpenWallet Foundation as a dependency, replacing the built-in ACA-Py templates. This change improves maintainability and alignment with the broader ACA-Py community.

### Migration Steps

> [!IMPORTANT]
> The following migration steps assume the upgrade target is a working > deployment of Traction using version `0.3.8` of the chart.

#### Update Global Configuration
```yaml
# Move ingressSuffix to global section
global:
  ingressSuffix: -dev.example.com  # Move from root level
```

#### Update ACA-Py Image Configuration
```yaml
acapy:
  image:
    registry: ghcr.io                              # Add registry field
    repository: bcgov/traction-plugins-acapy       # Remove registry prefix
    # ... keep other image settings
```

#### Update Service Port Configuration
```yaml
acapy:
  service:
    ports:
      http: 8021    # Update from httpPort: 8030
      admin: 8022   # Update from adminPort: 8031
      ws: 8023      # Add websocket port if needed
```

#### Convert Plugin Configuration
Replace the `plugins` section with `extraArgs`:
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
      existingSecret: ""  # Update from acapy.secret.adminApiKey.existingSecret
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
      - wallet_type=single-wallet-askar  # Simplified array format
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
  pluginInnkeeper:           # New section for innkeeper config
    existingSecret: ""
  smtp:
    existingSecret: ""       # Move from root level existingSecret
```

> [!WARNING]
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
