# traction

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.2.14](https://img.shields.io/badge/AppVersion-0.2.14-informational?style=flat-square)

The Traction service allows organizations to verify, hold, and issue verifiable credentials.

**Homepage:** <https://github.com/bcgov/traction>

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| i5okie | <ivan.polchenko@quartech.com> | <https://github.com/i5okie> |
| usingtechnology | <tools@usingtechnolo.gy> | <https://github.com/usingtechnology> |
| Jsyro | <jason.syrotuck@nttdata.com> | <https://github.com/Jsyro> |
| esune | <emiliano.sune@quartech.com> | <https://github.com/esune> |

## Source Code

* <https://github.com/bcgov/traction>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| https://charts.bitnami.com/bitnami/ | postgresql | 11.9.13 |
| https://charts.bitnami.com/bitnami | common | 2.x.x |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| acapy."argfile.yml".auto-accept-invites | bool | `true` |  |
| acapy."argfile.yml".auto-accept-requests | bool | `true` |  |
| acapy."argfile.yml".auto-create-revocation-transactions | bool | `true` |  |
| acapy."argfile.yml".auto-ping-connection | bool | `true` |  |
| acapy."argfile.yml".auto-promote-author-did | bool | `true` |  |
| acapy."argfile.yml".auto-provision | bool | `true` |  |
| acapy."argfile.yml".auto-request-endorsement | bool | `true` |  |
| acapy."argfile.yml".auto-respond-credential-offer | bool | `false` |  |
| acapy."argfile.yml".auto-respond-credential-proposal | bool | `false` |  |
| acapy."argfile.yml".auto-respond-credential-request | bool | `true` |  |
| acapy."argfile.yml".auto-respond-messages | bool | `true` |  |
| acapy."argfile.yml".auto-respond-presentation-proposal | bool | `true` |  |
| acapy."argfile.yml".auto-respond-presentation-request | bool | `false` |  |
| acapy."argfile.yml".auto-store-credential | bool | `true` |  |
| acapy."argfile.yml".auto-verify-presentation | bool | `true` |  |
| acapy."argfile.yml".auto-write-transactions | bool | `true` |  |
| acapy."argfile.yml".emit-new-didcomm-mime-type | bool | `true` |  |
| acapy."argfile.yml".emit-new-didcomm-prefix | bool | `true` |  |
| acapy."argfile.yml".endorser-alias | string | `"endorser"` |  |
| acapy."argfile.yml".endorser-protocol-role | string | `"author"` |  |
| acapy."argfile.yml".endorser-public-did | string | `"UjmxKBZe1qv1NBE7GaohdP"` |  |
| acapy."argfile.yml".genesis-url | string | `"{{ include \"traction.genesisUrl\" . }}"` |  |
| acapy."argfile.yml".label | string | `"{{ include \"acapy.label\" .}}"` |  |
| acapy."argfile.yml".log-level | string | `"info"` |  |
| acapy."argfile.yml".monitor-ping | bool | `true` |  |
| acapy."argfile.yml".monitor-revocation-notification | bool | `true` |  |
| acapy."argfile.yml".multitenant | bool | `true` |  |
| acapy."argfile.yml".multitenant-admin | bool | `true` |  |
| acapy."argfile.yml".notify-revocation | bool | `true` |  |
| acapy."argfile.yml".preserve-exchange-records | bool | `true` |  |
| acapy."argfile.yml".public-invites | bool | `true` |  |
| acapy."argfile.yml".read-only-ledger | bool | `false` |  |
| acapy."argfile.yml".tails-server-base-url | string | `"{{ include \"acapy.tails.baseUrl\" . }}"` |  |
| acapy."argfile.yml".tails-server-upload-url | string | `"{{ include \"acapy.tails.uploadUrl\" . }}"` |  |
| acapy."argfile.yml".wallet-name | string | `"askar-wallet"` |  |
| acapy."argfile.yml".wallet-storage-type | string | `"postgres_storage"` |  |
| acapy."argfile.yml".wallet-type | string | `"askar"` |  |
| acapy."plugin-config.yml".multitenant_provider.errors.on_unneeded_wallet_key | bool | `false` |  |
| acapy."plugin-config.yml".multitenant_provider.manager.always_check_provided_wallet_key | bool | `true` |  |
| acapy."plugin-config.yml".multitenant_provider.manager.class_name | string | `"traction_plugins.multitenant_provider.v1_0.manager.AskarMultitokenMultitenantManager"` |  |
| acapy."plugin-config.yml".multitenant_provider.token_expiry.amount | int | `1` |  |
| acapy."plugin-config.yml".multitenant_provider.token_expiry.units | string | `"days"` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.print_key | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.print_token | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.wallet_name | string | `"traction_innkeeper"` |  |
| acapy."plugin-config.yml".traction_innkeeper.reservation.auto_approve | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.reservation.expiry_minutes | int | `2880` |  |
| acapy.affinity | object | `{}` |  |
| acapy.agentSeed | string | `""` |  |
| acapy.autoscaling.enabled | bool | `true` |  |
| acapy.autoscaling.maxReplicas | int | `100` |  |
| acapy.autoscaling.minReplicas | int | `1` |  |
| acapy.autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| acapy.image.pullPolicy | string | `"IfNotPresent"` |  |
| acapy.image.repository | string | `"ghcr.io/bcgov/traction-plugins-acapy"` |  |
| acapy.imagePullSecrets | list | `[]` |  |
| acapy.labelOverride | string | `""` |  |
| acapy.networkPolicy.enabled | bool | `true` |  |
| acapy.networkPolicy.ingress.enabled | bool | `true` |  |
| acapy.networkPolicy.ingress.namespaceSelector."network.openshift.io/policy-group" | string | `"ingress"` |  |
| acapy.networkPolicy.ingress.podSelector | object | `{}` |  |
| acapy.networkPolicy.namespaceSelector | object | `{}` |  |
| acapy.nodeSelector | object | `{}` |  |
| acapy.openshift.adminRoute.enabled | bool | `false` |  |
| acapy.openshift.adminRoute.path | string | `"/"` |  |
| acapy.openshift.adminRoute.targetPort | string | `"admin"` |  |
| acapy.openshift.adminRoute.timeout | string | `"2m"` |  |
| acapy.openshift.adminRoute.tls.enabled | bool | `true` |  |
| acapy.openshift.adminRoute.tls.insecureEdgeTerminationPolicy | string | `"None"` |  |
| acapy.openshift.adminRoute.tls.termination | string | `"edge"` |  |
| acapy.openshift.adminRoute.wildcardPolicy | string | `"None"` |  |
| acapy.openshift.route.enabled | bool | `false` |  |
| acapy.openshift.route.path | string | `"/"` |  |
| acapy.openshift.route.targetPort | string | `"http"` |  |
| acapy.openshift.route.timeout | string | `"2m"` |  |
| acapy.openshift.route.tls.enabled | bool | `true` |  |
| acapy.openshift.route.tls.insecureEdgeTerminationPolicy | string | `"None"` |  |
| acapy.openshift.route.tls.termination | string | `"edge"` |  |
| acapy.openshift.route.wildcardPolicy | string | `"None"` |  |
| acapy.plugins.basicmessageStorage | bool | `true` |  |
| acapy.plugins.connectionUpdate | bool | `true` |  |
| acapy.plugins.multitenantProvider | bool | `true` |  |
| acapy.plugins.tractionInnkeeper | bool | `true` |  |
| acapy.podAnnotations | object | `{}` |  |
| acapy.podSecurityContext | object | `{}` |  |
| acapy.replicaCount | int | `1` |  |
| acapy.resources.limits.cpu | string | `"1"` |  |
| acapy.resources.limits.memory | string | `"1000Mi"` |  |
| acapy.resources.requests.cpu | string | `"250m"` |  |
| acapy.resources.requests.memory | string | `"384Mi"` |  |
| acapy.secret.adminurl.generated | bool | `true` |  |
| acapy.secret.pluginInnkeeper.generated | bool | `true` |  |
| acapy.securityContext | object | `{}` |  |
| acapy.service.adminPort | int | `8031` |  |
| acapy.service.httpPort | int | `8030` |  |
| acapy.service.type | string | `"ClusterIP"` |  |
| acapy.serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| acapy.serviceAccount.create | bool | `false` | Specifies whether a service account should be created |
| acapy.serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| acapy.tails.baseUrlOverride | string | `""` | Override the otherwise ledger-specifically generated base URL of the external tails server |
| acapy.tails.uploadUrlOverride | string | `""` | Override the otherwise ledger-specifically generated upload URL of the external tails server |
| acapy.tolerations | list | `[]` |  |
| acapy.walletStorageConfig.max_connections | int | `10` |  |
| acapy.walletStorageConfig.wallet_scheme | string | `"DatabasePerWallet"` |  |
| acapy.walletStorageCredentials.admin_account | string | `"postgres"` |  |
| acapy.walletStorageCredentials.existingSecret | string | `""` |  |
| fullnameOverride | string | `""` |  |
| global.ingressSuffix | string | `".apps.silver.devops.gov.bc.ca"` | set global.ingressSuffix |
| global.ledger | string | `"bcovrin-test"` | The used ledger. Will be used for default values. |
| ingress.annotations."route.openshift.io/termination" | string | `"edge"` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `true` |  |
| ingress.tls | list | `[]` |  |
| nameOverride | string | `""` |  |
| postgresql-ha.enabled | bool | `false` |  |
| postgresql.auth.database | string | `"traction"` | PostgreSQL Database to create. |
| postgresql.auth.existingSecret | string | `"{{ include \"global.fullname\" . }}"` |  |
| postgresql.auth.secretKeys.adminPasswordKey | string | `"postgres-password"` |  |
| postgresql.auth.secretKeys.userPasswordKey | string | `"database-password"` |  |
| postgresql.auth.username | string | `"acapy"` |  |
| postgresql.enabled | bool | `true` |  |
| postgresql.fullnameOverride | string | `""` |  |
| postgresql.primary.containerSecurityContext.enabled | bool | `false` |  |
| postgresql.primary.extendedConfiguration | string | `"max_connections = 500\n"` | Increase max_connections to support higher workloads |
| postgresql.primary.persistence | object | `{"enabled":true,"size":"1Gi"}` | Persistent Volume Storage configuration. ref: https://kubernetes.io/docs/user-guide/persistent-volumes |
| postgresql.primary.podSecurityContext.enabled | bool | `false` |  |
| postgresql.primary.resources.limits.cpu | string | `"600m"` |  |
| postgresql.primary.resources.limits.memory | string | `"2600Mi"` |  |
| postgresql.primary.resources.requests.cpu | string | `"300m"` |  |
| postgresql.primary.resources.requests.memory | string | `"1300Mi"` |  |
| postgresql.primary.securityContext | object | `{"enabled":false}` | add securityContext (fsGroup, runAsUser). These need to be false for Openshift 4 |
| postgresql.service | object | `{"ports":{"postgresql":5432}}` | PostgreSQL service configuration |
| tenant_proxy.affinity | object | `{}` |  |
| tenant_proxy.autoscaling.enabled | bool | `true` |  |
| tenant_proxy.autoscaling.maxReplicas | int | `100` |  |
| tenant_proxy.autoscaling.minReplicas | int | `1` |  |
| tenant_proxy.autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| tenant_proxy.image.pullPolicy | string | `"IfNotPresent"` |  |
| tenant_proxy.image.repository | string | `"ghcr.io/bcgov/traction-tenant-proxy"` |  |
| tenant_proxy.imagePullSecrets | list | `[]` |  |
| tenant_proxy.networkPolicy.enabled | bool | `true` |  |
| tenant_proxy.networkPolicy.ingress.enabled | bool | `true` |  |
| tenant_proxy.networkPolicy.ingress.namespaceSelector."network.openshift.io/policy-group" | string | `"ingress"` |  |
| tenant_proxy.networkPolicy.ingress.podSelector | object | `{}` |  |
| tenant_proxy.networkPolicy.namespaceSelector | object | `{}` |  |
| tenant_proxy.nodeSelector | object | `{}` |  |
| tenant_proxy.openshift.route.enabled | bool | `false` |  |
| tenant_proxy.openshift.route.path | string | `"/"` |  |
| tenant_proxy.openshift.route.targetPort | string | `"http"` |  |
| tenant_proxy.openshift.route.timeout | string | `"2m"` |  |
| tenant_proxy.openshift.route.tls.enabled | bool | `true` |  |
| tenant_proxy.openshift.route.tls.insecureEdgeTerminationPolicy | string | `"None"` |  |
| tenant_proxy.openshift.route.tls.termination | string | `"edge"` |  |
| tenant_proxy.openshift.route.wildcardPolicy | string | `"None"` |  |
| tenant_proxy.podAnnotations | object | `{}` |  |
| tenant_proxy.podSecurityContext | object | `{}` |  |
| tenant_proxy.replicaCount | int | `1` |  |
| tenant_proxy.resources.limits.cpu | string | `"250m"` |  |
| tenant_proxy.resources.limits.memory | string | `"256Mi"` |  |
| tenant_proxy.resources.requests.cpu | string | `"125m"` |  |
| tenant_proxy.resources.requests.memory | string | `"128Mi"` |  |
| tenant_proxy.securityContext | object | `{}` |  |
| tenant_proxy.service.port | int | `8032` |  |
| tenant_proxy.service.type | string | `"ClusterIP"` |  |
| tenant_proxy.serviceAccount.annotations | object | `{}` | Annotations to add to the service account |
| tenant_proxy.serviceAccount.create | bool | `false` | Specifies whether a service account should be created |
| tenant_proxy.serviceAccount.name | string | `""` | The name of the service account to use. If not set and create is true, a name is generated using the fullname template |
| tenant_proxy.tolerations | list | `[]` |  |
| traction.config.ledger.browserUrlOverride | string | `""` |  |
| traction.config.ledger.genesisUrlOverride | string | `""` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.11.0](https://github.com/norwoodj/helm-docs/releases/v1.11.0)
