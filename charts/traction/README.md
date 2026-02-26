# traction

![Version: 0.5.0](https://img.shields.io/badge/Version-0.5.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.3.1](https://img.shields.io/badge/AppVersion-1.3.1-informational?style=flat-square)

The Traction service allows organizations to verify, hold, and issue verifiable credentials. The Traction Tenant UI allows tenants to manage their agent.

**Homepage:** <https://github.com/bcgov/traction>

## TL;DR

```console
helm repo add traction https://bcgov.github.io/traction
helm install my-release traction/traction
```

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PV provisioner support in the underlying infrastructure

## Installing the Chart

To install the chart with the release name `my-release`:

```console
helm repo add traction https://bcgov.github.io/traction
helm install my-release traction/traction
```

The command deploys Traction and PostgreSQL on the Kubernetes cluster in the default configuration. The [Values](#values) section lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `my-release` deployment:

```console
helm delete my-release
```

The command removes all the Kubernetes components but secrets and PVC's associated with the chart and deletes the release.

To delete the secrets and PVC's associated with `my-release`:

```console
kubectl delete secret,pvc --selector "app.kubernetes.io/instance"=my-release
```

> **Note**: Deleting the PVC's will delete PostgreSQL data as well. Please be cautious before doing it.

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| acapy."argfile.yml".auto-accept-invites | bool | `true` | Automatically accept invites without firing a webhook event or waiting for an admin request. Default: false. |
| acapy."argfile.yml".auto-accept-requests | bool | `true` | Automatically accept connection requests without firing a webhook event or waiting for an admin request. Default: false. |
| acapy."argfile.yml".auto-create-revocation-transactions | bool | `true` | For Authors, specify whether to automatically create transactions for a cred def's revocation registry. (If not specified, the controller must invoke the endpoints required to create the revocation registry and assign to the cred def.) |
| acapy."argfile.yml".auto-ping-connection | bool | `true` | Automatically send a trust ping immediately after a connection response is accepted. Some agents require this before marking a connection as 'active'. Default: false. |
| acapy."argfile.yml".auto-promote-author-did | bool | `true` | For authors, specify whether to automatically promote a DID to the wallet public DID after writing to the ledger. |
| acapy."argfile.yml".auto-provision | bool | `true` | If the requested profile does not exist, initialize it with the given parameters. |
| acapy."argfile.yml".auto-request-endorsement | bool | `true` | For Authors, specify whether to automatically request endorsement for all transactions. (If not specified, the controller must invoke the request endorse operation for each transaction.) |
| acapy."argfile.yml".auto-respond-credential-offer | bool | `false` | Automatically respond to Indy credential offers with a credential request. Default: false |
| acapy."argfile.yml".auto-respond-credential-proposal | bool | `false` | Auto-respond to credential proposals with corresponding credential offers. |
| acapy."argfile.yml".auto-respond-credential-request | bool | `true` | Auto-respond to credential requests with corresponding credentials. |
| acapy."argfile.yml".auto-respond-messages | bool | `true` | Automatically respond to basic messages indicating the message was received. Default: false. |
| acapy."argfile.yml".auto-respond-presentation-proposal | bool | `true` | Auto-respond to presentation proposals with corresponding presentation requests. |
| acapy."argfile.yml".auto-respond-presentation-request | bool | `false` | Automatically respond to Indy presentation requests with a constructed presentation if a corresponding credential can be retrieved for every referent in the presentation request. Default: false. |
| acapy."argfile.yml".auto-store-credential | bool | `true` | Automatically store an issued credential upon receipt. Default: false. |
| acapy."argfile.yml".auto-verify-presentation | bool | `true` | Automatically verify a presentation when it is received. Default: false. |
| acapy."argfile.yml".auto-write-transactions | bool | `true` | For Authors, specify whether to automatically write any endorsed transactions. (If not specified, the controller must invoke the write transaction operation for each transaction.) |
| acapy."argfile.yml".debug-webhooks | bool | `true` |  |
| acapy."argfile.yml".emit-new-didcomm-mime-type | bool | `true` | Send packed agent messages with the DIDComm MIME type as of RFC 0044; i.e., 'application/didcomm-envelope-enc' instead of 'application/ssi-agent-wire'. |
| acapy."argfile.yml".emit-new-didcomm-prefix | bool | `true` | Emit protocol messages with new DIDComm prefix; i.e., 'https://didcomm.org/' instead of (default) prefix 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/'. |
| acapy."argfile.yml".endorser-alias | string | `"endorser"` | For transaction Authors, specify the alias of the Endorser connection that will be used to endorse transactions. |
| acapy."argfile.yml".endorser-protocol-role | string | `"author"` | Specify the role ('author' or 'endorser') which this agent will participate. Authors will request transaction endorsement from an Endorser. Endorsers will endorse transactions from Authors, and may write their own  transactions to the ledger. If no role (or 'none') is specified then the endorsement protocol will not be used and this agent will write transactions to the ledger directly. |
| acapy."argfile.yml".log-level | string | `"info"` | Specifies a custom logging level as one of: ('debug', 'info', 'warning', 'error', 'critical') |
| acapy."argfile.yml".monitor-ping | bool | `true` | Send a webhook when a ping is sent or received. |
| acapy."argfile.yml".monitor-revocation-notification | bool | `true` | Specifies that aca-py will emit webhooks on notification of revocation received. |
| acapy."argfile.yml".multitenancy-config[0] | string | `"wallet_type=single-wallet-askar"` |  |
| acapy."argfile.yml".multitenant | bool | `true` | Enable multitenant mode. |
| acapy."argfile.yml".multitenant-admin | bool | `true` | Specify whether to enable the multitenant admin api. |
| acapy."argfile.yml".notify-revocation | bool | `true` | Specifies that aca-py will notify credential recipients when revoking a credential it issued. |
| acapy."argfile.yml".preserve-exchange-records | bool | `true` | Keep credential exchange records after exchange has completed. |
| acapy."argfile.yml".public-invites | bool | `true` | Send invitations out using the public DID for the agent, and receive connection requests solicited by invitations which use the public DID. Default: false. |
| acapy."argfile.yml".read-only-ledger | bool | `false` | Sets ledger to read-only to prevent updates. Default: false. |
| acapy."argfile.yml".tails-server-base-url | string | `"https://tails-test.vonx.io"` | Sets the base url of the tails server in use. |
| acapy."argfile.yml".tails-server-upload-url | string | `"https://tails-test.vonx.io"` | Sets the base url of the tails server for upload, defaulting to the tails server base url. |
| acapy."argfile.yml".wallet-name | string | `"askar-wallet"` | Specifies the wallet name to be used by the agent. This is useful if your deployment has multiple wallets. |
| acapy."argfile.yml".wallet-storage-type | string | `"postgres_storage"` | Specifies the type of Indy wallet backend to use. Supported internal storage types are 'basic' (memory), 'default' (sqlite), and 'postgres_storage'.  The default, if not specified, is 'default'. |
| acapy."argfile.yml".wallet-type | string | `"askar"` | Specifies the type of Indy wallet provider to use. Supported internal storage types are 'basic' (memory) and 'indy'. The default (if not specified) is 'basic'. |
| acapy."argfile.yml".webhook-url | string | `""` | Send webhooks containing internal state changes to the specified URL. Optional API key to be passed in the request body can be appended using a hash separator [#]. This is useful for a controller to monitor agent events and respond to those events using the admin API. If not specified, webhooks are not published by the agent. |
| acapy."ledgers.yml"[0].endorser_alias | string | `"bcovrin-test-endorser"` |  |
| acapy."ledgers.yml"[0].endorser_did | string | `"DfQetNSm7gGEHuzfUvpfPn"` |  |
| acapy."ledgers.yml"[0].genesis_url | string | `"https://test.bcovrin.vonx.io/genesis"` |  |
| acapy."ledgers.yml"[0].id | string | `"bcovrin-test"` |  |
| acapy."ledgers.yml"[0].is_production | bool | `true` |  |
| acapy."ledgers.yml"[0].is_write | bool | `true` |  |
| acapy."plugin-config.yml".basicmessage_storage.wallet_enabled | bool | `true` |  |
| acapy."plugin-config.yml".did-webvh.server_url | string | `""` |  |
| acapy."plugin-config.yml".multitenant_provider.errors.on_unneeded_wallet_key | bool | `false` |  |
| acapy."plugin-config.yml".multitenant_provider.manager.always_check_provided_wallet_key | bool | `true` |  |
| acapy."plugin-config.yml".multitenant_provider.manager.class_name | string | `"multitenant_provider.v1_0.manager.AskarMultitokenMultitenantManager"` |  |
| acapy."plugin-config.yml".multitenant_provider.token_expiry.amount | int | `1` |  |
| acapy."plugin-config.yml".multitenant_provider.token_expiry.units | string | `"days"` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.connect_to_endorser[0].endorser_alias | string | `"bcovrin-test-endorser"` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.connect_to_endorser[0].ledger_id | string | `"bcovrin-test"` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.create_public_did[0] | string | `"bcovrin-test"` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.print_key | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.print_token | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.innkeeper_wallet.wallet_name | string | `"traction_innkeeper"` |  |
| acapy."plugin-config.yml".traction_innkeeper.reservation.auto_approve | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.reservation.auto_issuer | bool | `false` |  |
| acapy."plugin-config.yml".traction_innkeeper.reservation.expiry_minutes | int | `2880` |  |
| acapy.adminUrl | string | `""` | Override the admin URL for internal access |
| acapy.agentUrl | string | `""` | Override the agent URL advertised by ACA-Py |
| acapy.automountServiceAccountToken | bool | `false` | Automount service account token for the ACA-Py pod |
| acapy.autoscaling.enabled | bool | `false` | Enable Horizontal POD autoscaling for ACA-Py |
| acapy.autoscaling.maxReplicas | int | `3` | Maximum number of ACA-Py replicas |
| acapy.autoscaling.minReplicas | int | `1` | Minimum number of ACA-Py replicas |
| acapy.autoscaling.stabilizationWindowSeconds | int | `300` | Stabilization window in seconds |
| acapy.autoscaling.targetCPUUtilizationPercentage | int | `80` | Target CPU utilization percentage |
| acapy.autoscaling.targetMemoryUtilizationPercentage | int | `80` | Target Memory utilization percentage |
| acapy.commonAnnotations | object | `{}` |  |
| acapy.commonLabels | object | `{}` |  |
| acapy.existingConfigmap | string | `""` | Name of an existing ConfigMap providing argfile.yml and other config |
| acapy.extraArgs[0] | string | `"--plugin 'aries_cloudagent.messaging.jsonld'"` |  |
| acapy.extraArgs[10] | string | `"--plugin rpc.v1_0"` |  |
| acapy.extraArgs[11] | string | `"--plugin webvh"` |  |
| acapy.extraArgs[1] | string | `"--plugin traction_plugins.traction_innkeeper.v1_0"` |  |
| acapy.extraArgs[2] | string | `"--plugin-config-value traction_innkeeper.innkeeper_wallet.tenant_id=\\\"$(INNKEEPER_WALLET_TENANT_ID)\\\""` |  |
| acapy.extraArgs[3] | string | `"--plugin-config-value traction_innkeeper.innkeeper_wallet.wallet_key=\\\"$(INNKEEPER_WALLET_WALLET_KEY)\\\""` |  |
| acapy.extraArgs[4] | string | `"--plugin multitenant_provider.v1_0"` |  |
| acapy.extraArgs[5] | string | `"--plugin basicmessage_storage.v1_0"` |  |
| acapy.extraArgs[6] | string | `"--plugin connections"` |  |
| acapy.extraArgs[7] | string | `"--plugin connection_update.v1_0"` |  |
| acapy.extraArgs[8] | string | `"--plugin issue_credential.v1_0"` |  |
| acapy.extraArgs[9] | string | `"--plugin present_proof.v1_0"` |  |
| acapy.extraEnvVars | list | `[]` |  |
| acapy.extraEnvVarsCM | string | `""` | Name of an existing ConfigMap with extra env vars |
| acapy.extraEnvVarsSecret | string | `"{{- printf \"%s-%s\" (include \"common.names.fullname\" .) \"plugin-innkeeper\" }}"` | Name of an existing Secret with extra env vars (required for innkeeper plugin) |
| acapy.extraVolumeMounts | list | `[]` |  |
| acapy.extraVolumes | list | `[]` |  |
| acapy.image.digest | string | `""` | Overrides the image digest which is used instead of the tag. |
| acapy.image.pullPolicy | string | `"IfNotPresent"` |  |
| acapy.image.pullSecrets | list | `[]` |  |
| acapy.image.registry | string | `"ghcr.io"` |  |
| acapy.image.repository | string | `"bcgov/traction-plugins-acapy"` |  |
| acapy.image.tag | string | `"1.3.1"` | Overrides the image tag which defaults to the chart appVersion. |
| acapy.ingress.admin.enabled | bool | `false` | Enable ingress for the admin endpoint |
| acapy.ingress.admin.hostname | string | `""` | Hostname to expose the admin endpoint |
| acapy.ingress.agent.enabled | bool | `false` | Enable ingress for the agent endpoint |
| acapy.ingress.agent.hostname | string | `""` | Hostname to expose the agent endpoint |
| acapy.initContainers | list | `[]` |  |
| acapy.networkPolicy.allowExternal | bool | `false` | Allow ingress from any source (disables from selectors when true) |
| acapy.networkPolicy.allowExternalEgress | bool | `true` | Allow all egress traffic (when false, only DNS and extraEgress are applied) |
| acapy.networkPolicy.enabled | bool | `false` | Enable network policies |
| acapy.networkPolicy.extraEgress | list | `[]` |  |
| acapy.networkPolicy.extraIngress | list | `[]` |  |
| acapy.networkPolicy.ingressNSMatchLabels | object | `{}` |  |
| acapy.networkPolicy.ingressPodMatchLabels | object | `{}` |  |
| acapy.nodeAffinityPreset.key | string | `""` | Node label key for node affinity preset |
| acapy.nodeAffinityPreset.type | string | `""` | Node affinity preset type (soft|hard|empty) |
| acapy.nodeAffinityPreset.values | list | `[]` |  |
| acapy.podAffinityPreset | string | `""` | Pod affinity preset (soft|hard|empty) |
| acapy.podAntiAffinityPreset | string | `""` | Pod anti-affinity preset (soft|hard|empty) |
| acapy.replicaCount | int | `1` | Number of ACA-Py replicas to deploy |
| acapy.resources.requests.cpu | string | `"120m"` | The requested cpu for the ACA-Py containers |
| acapy.resources.requests.memory | string | `"200Mi"` | The requested memory for the ACA-Py containers |
| acapy.secrets.api.existingSecret | string | `""` | Name of an existing Secret providing API related keys. If set, the chart will NOT create the api secret. |
| acapy.secrets.api.retainOnUninstall | bool | `true` | When true, adds helm.sh/resource-policy: keep to generated api secret |
| acapy.secrets.api.secretKeys.adminApiKey | string | `"adminApiKey"` | Key in the API secret holding the admin API key. |
| acapy.secrets.api.secretKeys.jwtKey | string | `"jwt"` | Key in the API secret holding the multitenant JWT signing secret. |
| acapy.secrets.api.secretKeys.walletKey | string | `"walletKey"` | Key in the API secret holding the wallet key. |
| acapy.secrets.api.secretKeys.webhookapiKey | string | `"webhookapi"` | Key in the API secret holding the webhook API key (used when embedding in webhook-url). |
| acapy.secrets.seed.enabled | bool | `false` | Disabled by default, turning this on will cause the Traction agent to NOT start unless additional setup steps are completed (refer to ACA-Py chart docs). |
| acapy.service.ports.admin | int | `8022` | Port to expose for admin service |
| acapy.service.ports.http | int | `8021` | Port to expose for http service |
| acapy.service.ports.ws | int | `8023` | Port to expose for websocket service |
| acapy.serviceAccount.annotations | object | `{}` |  |
| acapy.serviceAccount.automountServiceAccountToken | bool | `true` | Automount service account token for the server service account |
| acapy.serviceAccount.create | bool | `false` | Specifies whether a ServiceAccount should be created |
| acapy.serviceAccount.name | string | `""` | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. |
| acapy.topologySpreadConstraints | list | `[]` |  |
| acapy.updateStrategy | object | `{}` |  |
| acapy.websockets.enabled | bool | `false` | Enable WebSocket transport for ACA-Py |
| fullnameOverride | string | `""` | String to fully override the helm chart name, full prefix. *Must be provided if using a custom release name that does not include the word traction.* |
| global.compatibility.openshift.adaptSecurityContext | string | `"auto"` | Adapt the securityContext sections of the deployment to make them compatible with Openshift restricted-v2 SCC: remove runAsUser, runAsGroup and fsGroup and let the platform use their allowed default IDs. Possible values: auto (apply if the detected running cluster is Openshift), force (perform the adaptation always), disabled (do not perform adaptation) |
| global.defaultStorageClass | string | `""` | Default StorageClass for Persistent Volume Claim |
| global.imagePullSecrets | list | `[]` | Global Docker registry secret names as an array |
| global.imageRegistry | string | `""` | Global Docker image registry |
| global.ingressSuffix | string | `"-dev.example.com"` | Domain suffix to be used for default hostpaths in ingress |
| global.security.allowInsecureImages | bool | `false` | Allows skipping image verification |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` | IngressClass that will be be used to implement the Ingress (Kubernetes 1.18+) |
| ingress.enabled | bool | `false` | Enable ingress record generation for traction |
| ingress.tls | list | `[]` |  |
| nameOverride | string | `""` | String to override the helm chart name, second part of the prefix |
| tenant_proxy.affinity | object | `{}` |  |
| tenant_proxy.autoscaling.enabled | bool | `false` | Enable Horizontal POD autoscaling for Tenant proxy |
| tenant_proxy.autoscaling.maxReplicas | int | `3` | Maximum number of Tenant proxy replicas |
| tenant_proxy.autoscaling.minReplicas | int | `1` | Minimum number of Tenant proxy replicas |
| tenant_proxy.autoscaling.stabilizationWindowSeconds | int | `300` | Stabilization window in seconds |
| tenant_proxy.autoscaling.targetCPUUtilizationPercentage | int | `80` | Target CPU utilization percentage |
| tenant_proxy.autoscaling.targetMemoryUtilizationPercentage | int | `80` | Target Memory utilization percentage |
| tenant_proxy.containerSecurityContext | object | `{}` |  |
| tenant_proxy.image.pullPolicy | string | `"IfNotPresent"` |  |
| tenant_proxy.image.pullSecrets | list | `[]` |  |
| tenant_proxy.image.repository | string | `"ghcr.io/bcgov/traction-tenant-proxy"` |  |
| tenant_proxy.image.tag | string | `""` | Overrides the image tag which defaults to the chart appVersion. |
| tenant_proxy.networkPolicy.enabled | bool | `false` | Enable network policies |
| tenant_proxy.networkPolicy.ingress.enabled | bool | `true` | Enable ingress rules |
| tenant_proxy.networkPolicy.ingress.namespaceSelector | object | `{}` |  |
| tenant_proxy.networkPolicy.ingress.podSelector | object | `{}` |  |
| tenant_proxy.nodeSelector | object | `{}` |  |
| tenant_proxy.openshift.route.enabled | bool | `false` | Create OpenShift Route resource for Tenant proxy |
| tenant_proxy.openshift.route.path | string | `"/"` | Path that the router watches for, to route traffic to the service |
| tenant_proxy.openshift.route.targetPort | string | `"http"` | Target port for the service |
| tenant_proxy.openshift.route.timeout | string | `"2m"` | Timeout in seconds for a route to return |
| tenant_proxy.openshift.route.tls.enabled | bool | `true` | Enable TLS termination |
| tenant_proxy.openshift.route.tls.insecureEdgeTerminationPolicy | string | `"None"` | TLS termination policy |
| tenant_proxy.openshift.route.tls.termination | string | `"edge"` | TLS termination type |
| tenant_proxy.openshift.route.wildcardPolicy | string | `"None"` | Wildcard policy for the route |
| tenant_proxy.podAnnotations | object | `{}` |  |
| tenant_proxy.podSecurityContext | object | `{}` |  |
| tenant_proxy.replicaCount | int | `1` | Number of Tenant proxy replicas to deploy. Ignored if autoscaling is enabled. |
| tenant_proxy.resources.requests.cpu | string | `"10m"` | The requested cpu for the Tenant proxy containers |
| tenant_proxy.resources.requests.memory | string | `"50Mi"` | The requested memory for the Tenant proxy containers |
| tenant_proxy.service.port | int | `8032` | Port to expose for http services |
| tenant_proxy.service.type | string | `"ClusterIP"` | Kubernetes Service type |
| tenant_proxy.serviceAccount.annotations | object | `{}` |  |
| tenant_proxy.serviceAccount.automountServiceAccountToken | bool | `true` | Automount service account token for the server service account |
| tenant_proxy.serviceAccount.create | bool | `false` | Specifies whether a ServiceAccount should be created |
| tenant_proxy.serviceAccount.name | string | `""` | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. |
| tenant_proxy.tolerations | list | `[]` |  |
| ui.affinity | object | `{}` |  |
| ui.autoscaling.enabled | bool | `false` | Enable Horizontal POD autoscaling for tenant-ui |
| ui.autoscaling.maxReplicas | int | `3` | Maximum number of tenant-ui replicas |
| ui.autoscaling.minReplicas | int | `1` | Minimum number of tenant-ui replicas |
| ui.autoscaling.targetCPUUtilizationPercentage | int | `80` | Target CPU utilization percentage |
| ui.autoscaling.targetMemoryUtilizationPercentage | int | `80` | Target Memory utilization percentage |
| ui.containerSecurityContext | object | `{}` |  |
| ui.enabled | bool | `true` | Deploy tenant-ui |
| ui.image.pullPolicy | string | `"IfNotPresent"` |  |
| ui.image.pullSecrets | list | `[]` |  |
| ui.image.repository | string | `"ghcr.io/bcgov/traction-tenant-ui"` |  |
| ui.image.tag | string | `""` | Overrides the image tag which defaults to the chart appVersion. |
| ui.lokiUrl | string | `""` | The endpoint to stream loki logs from for the Tenant UI |
| ui.networkPolicy.enabled | bool | `false` | Enable network policies |
| ui.networkPolicy.ingress.enabled | bool | `false` | Enable ingress rules |
| ui.networkPolicy.ingress.namespaceSelector | object | `{}` |  |
| ui.networkPolicy.ingress.podSelector | object | `{}` |  |
| ui.nodeSelector | object | `{}` |  |
| ui.oidc.active | bool | `true` | Enable OIDC authentication |
| ui.oidc.authority | string | `""` | OIDC authority |
| ui.oidc.client | string | `"innkeeper-frontend"` | OIDC client |
| ui.oidc.extraQueryParams | string | `"{}"` |  |
| ui.oidc.jwksUri | string | `""` | OIDC jwksUri |
| ui.oidc.label | string | `"IDIR"` | OIDC label |
| ui.oidc.realm | string | `"Traction"` | OIDC realm |
| ui.oidc.reservationForm | string | `"{}"` |  |
| ui.oidc.roleName | string | `"innkeeper"` | OIDC role name |
| ui.oidc.session.countdownSeconds | int | `30` | OIDC session countdown seconds |
| ui.oidc.session.timeoutSeconds | int | `600` | OIDC session timeout seconds |
| ui.oidc.showInnkeeperAdminLogin | bool | `true` | Show Innkeeper Admin Login |
| ui.oidc.showWritableComponents | bool | `true` | Show writable components |
| ui.openshift.route.enabled | bool | `false` | Create OpenShift Route resource for tenant-ui |
| ui.openshift.route.path | string | `"/"` | Path that the router watches for, to route traffic to the service |
| ui.openshift.route.targetPort | string | `"http"` | Target port for the service |
| ui.openshift.route.timeout | string | `"2m"` | Timeout in seconds for a route to return |
| ui.openshift.route.tls.enabled | bool | `true` | Enable TLS termination |
| ui.openshift.route.tls.insecureEdgeTerminationPolicy | string | `"None"` | TLS termination policy |
| ui.openshift.route.tls.termination | string | `"edge"` | TLS termination type |
| ui.openshift.route.wildcardPolicy | string | `"None"` | Wildcard policy for the route |
| ui.pluginInnkeeper.existingSecret | string | `""` | Name of an existing Secret providing INNKEEPER_WALLET_TENANT_ID and INNKEEPER_WALLET_WALLET_KEY |
| ui.podAnnotations | object | `{}` |  |
| ui.podSecurityContext | object | `{}` |  |
| ui.quickConnectEndorserName | string | `""` | A ledger that has endorser auto-accept/transact enabled |
| ui.replicaCount | int | `1` | Number of tenant-ui replicas to deploy. Ignored if autoscaling is enabled. |
| ui.requireEmailForReservation | bool | `true` | Whether the Email field is needed for a tenant reservation |
| ui.resources.requests.cpu | string | `"10m"` | The requested cpu for the tenant-ui containers |
| ui.resources.requests.memory | string | `"80Mi"` | The requested memory for the tenant-ui containers |
| ui.service.httpPort | int | `8080` | Port to expose for http service |
| ui.service.type | string | `"ClusterIP"` | Kubernetes Service type |
| ui.serviceAccount.annotations | object | `{}` |  |
| ui.serviceAccount.automountServiceAccountToken | bool | `true` | Automount service account token for the server service account |
| ui.serviceAccount.create | bool | `false` | Specifies whether a ServiceAccount should be created |
| ui.serviceAccount.name | string | `""` | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. |
| ui.showOIDCReservationLogin | bool | `false` | OIDC reservation login |
| ui.smtp.existingSecret | string | `""` | Name of an existing secret to be mounted as environment variables |
| ui.smtp.innkeeperInbox | string | `""` | innkeeper notification inbox |
| ui.smtp.port | int | `25` | SMTP port |
| ui.smtp.secure | bool | `false` | if true the connection will use TLS when connecting to server. If false (the default) then TLS is used if server supports the STARTTLS extension. In most cases set this value to true if you are connecting to port 465. For port 587 or 25 keep it false |
| ui.smtp.senderAddress | string | `""` | SMTP sender address |
| ui.smtp.server | string | `""` | SMTP server |
| ui.smtp.user | string | `""` | SMTP user (use ui.smtp.existingSecret to provide SERVER_SMTP_PASSWORD) |
| ui.tolerations | list | `[]` |  |
| ui.ux.aboutBusiness.imageUrl | string | `"/img/bc/bc_logo.png"` |  |
| ui.ux.aboutBusiness.link | string | `"https://github.com/bcgov/bc-vcpedia/blob/main/agents/bc-gov-agent-service.md"` |  |
| ui.ux.aboutBusiness.linkTitle | string | `"BC Digital Trust Service Agreement"` |  |
| ui.ux.aboutBusiness.title | string | `"Government of British Columbia"` |  |
| ui.ux.appInnkeeperTitle | string | `"Traction Innkeeper Console"` | Title of the Innkeeper Console |
| ui.ux.appTitle | string | `"Traction Tenant Console"` | Title of the application |
| ui.ux.copyright | string | `""` |  |
| ui.ux.coverImageCopyright | string | `"Photo by Kristoffer Fredriksson on StockSnap"` |  |
| ui.ux.infoBanner.message | string | `""` |  |
| ui.ux.infoBanner.messageLevel | string | `"info"` | <info|warn|error|success> |
| ui.ux.infoBanner.showMessage | bool | `false` | Show the info banner <boolean> |
| ui.ux.owner | string | `""` |  |
| ui.ux.sidebarTitle | string | `"Traction"` | Sidebar title |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
