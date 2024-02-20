# Traction

![version: 0.2.8](https://img.shields.io/badge/Version-0.2.7-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.4.0](https://img.shields.io/badge/AppVersion-0.4.0-informational?style=flat-square)

The Traction service allows organizations to verify, hold, and issue verifiable credentials.

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

The command deploys Traction and PostgrSQL on the Kubernetes cluster in the default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

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

> **Note**: Deleting the PVC's will delete postgresql data as well. Please be cautious before doing it.

## Parameters

### Acapy Configuration

| Name                                                  | Description                                                                                                         | Value                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| `acapy.image.repository`                              |                                                                                                                     | `ghcr.io/bcgov/traction-plugins-acapy` |
| `acapy.image.pullPolicy`                              |                                                                                                                     | `IfNotPresent`                         |
| `acapy.image.pullSecrets`                             |                                                                                                                     | `[]`                                   |
| `acapy.image.tag`                                     | Overrides the image tag which defaults to the chart appVersion.                                                     | `""`                                   |
| `acapy.serviceAccount.create`                         | Specifies whether a ServiceAccount should be created                                                                | `false`                                |
| `acapy.serviceAccount.annotations`                    | Annotations for service account. Evaluated as a template. Only used if `create` is `true`.                          | `{}`                                   |
| `acapy.serviceAccount.automountServiceAccountToken`   | Automount service account token for the server service account                                                      | `true`                                 |
| `acapy.serviceAccount.name`                           | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""`                                   |
| `acapy.replicaCount`                                  | Number of AcaPy replicas to deploy                                                                                  | `1`                                    |
| `acapy.autoscaling.enabled`                           | Enable Horizontal POD autoscaling for AcaPy                                                                         | `false`                                |
| `acapy.autoscaling.minReplicas`                       | Minimum number of AcaPy replicas                                                                                    | `1`                                    |
| `acapy.autoscaling.maxReplicas`                       | Maximum number of AcaPy replicas                                                                                    | `10`                                   |
| `acapy.autoscaling.targetCPUUtilizationPercentage`    | Target CPU utilization percentage                                                                                   | `80`                                   |
| `acapy.autoscaling.targetMemoryUtilizationPercentage` | Target Memory utilization percentage                                                                                | `80`                                   |
| `acapy.autoscaling.stabilizationWindowSeconds`        | Stabilization window in seconds                                                                                     | `300`                                  |
| `acapy.labelOverride`                                 |                                                                                                                     | `""`                                   |

### Acapy configuration file

| Name                                                    | Description                                                                                                                                                                                                                                                                                                                                                                                         | Value                          |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| `acapy.argfile.yml.auto-accept-invites`                 | Automatically accept invites without firing a webhook event or waiting for an admin request. Default: false.                                                                                                                                                                                                                                                                                        | `true`                         |
| `acapy.argfile.yml.auto-accept-requests`                | Automatically accept connection requests without firing a webhook event or waiting for an admin request. Default: false.                                                                                                                                                                                                                                                                            | `true`                         |
| `acapy.argfile.yml.auto-create-revocation-transactions` | For Authors, specify whether to automatically create transactions for a cred def's revocation registry. (If not specified, the controller must invoke the endpoints required to create the revocation registry and assign to the cred def.)                                                                                                                                                         | `true`                         |
| `acapy.argfile.yml.auto-ping-connection`                | Automatically send a trust ping immediately after a connection response is accepted. Some agents require this before marking a connection as 'active'. Default: false.                                                                                                                                                                                                                              | `true`                         |
| `acapy.argfile.yml.auto-promote-author-did`             | For authors, specify whether to automatically promote a DID to the wallet public DID after writing to the ledger.``                                                                                                                                                                                                                                                                                 | `true`                         |
| `acapy.argfile.yml.auto-provision`                      | If the requested profile does not exist, initialize it with the given parameters.                                                                                                                                                                                                                                                                                                                   | `true`                         |
| `acapy.argfile.yml.auto-request-endorsement`            | For Authors, specify whether to automatically request endorsement for all transactions. (If not specified, the controller must invoke the request endorse operation for each transaction.)                                                                                                                                                                                                          | `true`                         |
| `acapy.argfile.yml.auto-respond-credential-offer`       | Automatically respond to Indy credential offers with a credential request. Default: false                                                                                                                                                                                                                                                                                                           | `false`                        |
| `acapy.argfile.yml.auto-respond-credential-proposal`    | Auto-respond to credential proposals with corresponding credential offers.                                                                                                                                                                                                                                                                                                                          | `false`                        |
| `acapy.argfile.yml.auto-respond-credential-request`     | Auto-respond to credential requests with corresponding credentials.                                                                                                                                                                                                                                                                                                                                 | `true`                         |
| `acapy.argfile.yml.auto-respond-messages`               | Automatically respond to basic messages indicating the message was received. Default: false.                                                                                                                                                                                                                                                                                                        | `true`                         |
| `acapy.argfile.yml.auto-respond-presentation-proposal`  | Auto-respond to presentation proposals with corresponding presentation requests.                                                                                                                                                                                                                                                                                                                    | `true`                         |
| `acapy.argfile.yml.auto-respond-presentation-request`   | Automatically respond to Indy presentation requests with a constructed presentation if a corresponding credential can be retrieved for every referent in the presentation request. Default: false.                                                                                                                                                                                                  | `false`                        |
| `acapy.argfile.yml.auto-store-credential`               | Automatically store an issued credential upon receipt. Default: false.                                                                                                                                                                                                                                                                                                                              | `true`                         |
| `acapy.argfile.yml.auto-verify-presentation`            | Automatically verify a presentation when it is received. Default: false.                                                                                                                                                                                                                                                                                                                            | `true`                         |
| `acapy.argfile.yml.auto-write-transactions`             | For Authors, specify whether to automatically write any endorsed transactions. (If not specified, the controller must invoke the write transaction operation for each transaction.)                                                                                                                                                                                                                 | `true`                         |
| `acapy.argfile.yml.emit-new-didcomm-mime-type`          | Send packed agent messages with the DIDComm MIME type as of RFC 0044; i.e., 'application/didcomm-envelope-enc' instead of 'application/ssi-agent-wire'.                                                                                                                                                                                                                                             | `true`                         |
| `acapy.argfile.yml.emit-new-didcomm-prefix`             | Emit protocol messages with new DIDComm prefix; i.e., 'https://didcomm.org/' instead of (default) prefix 'did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/'.                                                                                                                                                                                                                                                    | `true`                         |
| `acapy.argfile.yml.endorser-alias`                      | For transaction Authors, specify the alias of the Endorser connection that will be used to endorse transactions.                                                                                                                                                                                                                                                                                    | `endorser`                     |
| `acapy.argfile.yml.endorser-protocol-role`              | Specify the role ('author' or 'endorser') which this agent will participate. Authors will request transaction endorement from an Endorser. Endorsers will endorse transactions from Authors, and may write their own  transactions to the ledger. If no role (or 'none') is specified then the endorsement protocol will not be used and this agent will write transactions to the ledger directly. | `author`                       |
| `acapy.argfile.yml.genesis-transactions-list`           | Path to YAML configuration for connecting to multiple HyperLedger Indy ledgers.                                                                                                                                                                                                                                                                                                                     | `/home/aries/ledgers.yml`      |
| `acapy.argfile.yml.label`                               | Specifies the label for this agent. This label is publicized (self-attested) to other agents as part of forming a connection. Set to release name by default.                                                                                                                                                                                                                                       | `{{ include "acapy.label" .}}` |
| `acapy.argfile.yml.log-level`                           | Specifies a custom logging level as one of: ('debug', 'info', 'warning', 'error', 'critical')                                                                                                                                                                                                                                                                                                       | `info`                         |
| `acapy.argfile.yml.monitor-ping`                        | Send a webhook when a ping is sent or received.                                                                                                                                                                                                                                                                                                                                                     | `true`                         |
| `acapy.argfile.yml.monitor-revocation-notification`     | Specifies that aca-py will emit webhooks on notification of revocation received.                                                                                                                                                                                                                                                                                                                    | `true`                         |
| `acapy.argfile.yml.multitenant-admin`                   | Specify whether to enable the multitenant admin api.                                                                                                                                                                                                                                                                                                                                                | `true`                         |
| `acapy.argfile.yml.multitenant`                         | Enable multitenant mode.                                                                                                                                                                                                                                                                                                                                                                            | `true`                         |
| `acapy.argfile.yml.notify-revocation`                   | Specifies that aca-py will notify credential recipients when revoking a credential it issued.                                                                                                                                                                                                                                                                                                       | `true`                         |
| `acapy.argfile.yml.preserve-exchange-records`           | Keep credential exchange records after exchange has completed.                                                                                                                                                                                                                                                                                                                                      | `true`                         |
| `acapy.argfile.yml.public-invites`                      | Send invitations out using the public DID for the agent, and receive connection requests solicited by invitations which use the public DID. Default: false.                                                                                                                                                                                                                                         | `true`                         |
| `acapy.argfile.yml.read-only-ledger`                    | Sets ledger to read-only to prevent updates. Default: false.                                                                                                                                                                                                                                                                                                                                        | `false`                        |
| `acapy.argfile.yml.tails-server-base-url`               | Sets the base url of the tails server in use.                                                                                                                                                                                                                                                                                                                                                       | `https://tails-test.vonx.io`   |
| `acapy.argfile.yml.tails-server-upload-url`             | Sets the base url of the tails server for upload, defaulting to the tails server base url.                                                                                                                                                                                                                                                                                                          | `https://tails-test.vonx.io`   |
| `acapy.argfile.yml.wallet-name`                         | Specifies the wallet name to be used by the agent. This is useful if your deployment has multiple wallets.                                                                                                                                                                                                                                                                                          | `askar-wallet`                 |
| `acapy.argfile.yml.wallet-storage-type`                 | Specifies the type of Indy wallet backend to use. Supported internal storage types are 'basic' (memory), 'default' (sqlite), and 'postgres_storage'.  The default, if not specified, is 'default'.                                                                                                                                                                                                  | `postgres_storage`             |
| `acapy.argfile.yml.wallet-type`                         | Specifies the type of Indy wallet provider to use. Supported internal storage types are 'basic' (memory) and 'indy'. The default (if not specified) is 'basic'.                                                                                                                                                                                                                                     | `askar`                        |
| `acapy.ledgers.yml`                                     | YAML configuration for connecting to multiple HyperLedger Indy                                                                                                                                                                                                                                                                                                                                      | `{}`                           |

### Wallet Storage configuration

| Name                                        | Description                                                                                                                                                            | Value               |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| `acapy.walletStorageConfig.json`            | Raw json, overrides all other values including postgres subchart values. e.g.: '{"url":"localhost:5432", "max_connections":"10", "wallet_scheme":"DatabasePerWallet"}' | `""`                |
| `acapy.walletStorageConfig.url`             | Database url. Overrides all other values including postgres subchart values.                                                                                           | `""`                |
| `acapy.walletStorageConfig.max_connections` | Client max connections, defaults to 10.                                                                                                                                | `10`                |
| `acapy.walletStorageConfig.wallet_scheme`   | Wallet scheme.                                                                                                                                                         | `DatabasePerWallet` |

### Wallet Storage Credentials

| Name                                            | Description                                                                                                                                                                                                                    | Value      |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| `acapy.walletStorageCredentials.json`           | Raw json with database credentials. Overrides all other values including postgres subchart values. e.g.: '{"account":"postgres","password":"mysecretpassword","admin_account":"postgres","admin_password":"mysecretpassword"}' | `""`       |
| `acapy.walletStorageCredentials.account`        | Database account name.                                                                                                                                                                                                         | `""`       |
| `acapy.walletStorageCredentials.password`       | Database password.                                                                                                                                                                                                             | `""`       |
| `acapy.walletStorageCredentials.admin_account`  | Database account with CREATEDB role used to create additional databases per wallet.                                                                                                                                            | `postgres` |
| `acapy.walletStorageCredentials.admin_password` | Database password for admin account.                                                                                                                                                                                           | `""`       |
| `acapy.walletStorageCredentials.existingSecret` | Name of an existing secret containing 'database-user', 'database-password', 'admin-password' keys.                                                                                                                             | `""`       |

### Acapy Plugins

| Name                                | Description                             | Value  |
| ----------------------------------- | --------------------------------------- | ------ |
| `acapy.plugins.basicmessageStorage` | Enable the basicmessage storage plugin. | `true` |
| `acapy.plugins.connectionUpdate`    | Enable the connection update plugin.    | `true` |
| `acapy.plugins.multitenantProvider` | Enable the multitenant provider plugin. | `true` |
| `acapy.plugins.tractionInnkeeper`   | Enable the traction innkeeper plugin.   | `true` |
| `acapy.plugins.rpc`                 | Enable the RPC plugin.                  | `true` |

### Acapy Plugin Configuration

| Name                                                                                    | Description | Value                                                                                  |
| --------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------- |
| `acapy.plugin-config.yml.multitenant_provider.manager.class_name`                       |             | `multitenant_provider.v1_0.manager.AskarMultitokenMultitenantManager`                  |
| `acapy.plugin-config.yml.multitenant_provider.manager.always_check_provided_wallet_key` |             | `true`                                                                                 |
| `acapy.plugin-config.yml.multitenant_provider.errors.on_unneeded_wallet_key`            |             | `false`                                                                                |
| `acapy.plugin-config.yml.multitenant_provider.token_expiry.units`                       |             | `days`                                                                                 |
| `acapy.plugin-config.yml.multitenant_provider.token_expiry.amount`                      |             | `1`                                                                                    |
| `acapy.plugin-config.yml.traction_innkeeper.innkeeper_wallet.wallet_name`               |             | `traction_innkeeper`                                                                   |
| `acapy.plugin-config.yml.traction_innkeeper.innkeeper_wallet.print_key`                 |             | `false`                                                                                |
| `acapy.plugin-config.yml.traction_innkeeper.innkeeper_wallet.print_token`               |             | `false`                                                                                |
| `acapy.plugin-config.yml.traction_innkeeper.innkeeper_wallet.connect_to_endorser`       |             | `[]`                                                                                   |
| `acapy.plugin-config.yml.traction_innkeeper.innkeeper_wallet.create_public_did`         |             | `[]`                                                                                   |
| `acapy.plugin-config.yml.traction_innkeeper.reservation.expiry_minutes`                 |             | `2880`                                                                                 |
| `acapy.plugin-config.yml.traction_innkeeper.reservation.auto_approve`                   |             | `false`                                                                                |
| `acapy.plugin-config.yml.traction_innkeeper.reservation.auto_issuer`                    |             | `false`                                                                                |
| `acapy.plugin-config.yml.basicmessage_storage.wallet_enabled`                           |             | `true`                                                                                 |

### Acapy tails persistence configuration

| Name                              | Description                                                                              | Value                            |
| --------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------- |
| `acapy.persistence.existingClaim` | Name of an existing PVC to use                                                           | `""`                             |
| `acapy.persistence.mountPath`     |                                                                                          | `/home/aries/.indy_client/tails` |
| `acapy.persistence.storageClass`  | PVC Storage Class                                                                        | `""`                             |
| `acapy.persistence.accessModes`   | PVC Access Mode. ReadWriteMany is required for each Acapy pod to access the same volume. | `["ReadWriteMany"]`              |
| `acapy.persistence.size`          | PVC Storage Request for tails volume                                                     | `1Gi`                            |

### Acapy common configurations

| Name                              | Description                                   | Value       |
| --------------------------------- | --------------------------------------------- | ----------- |
| `acapy.resources.limits.memory`   | The memory limit for the Acapy containers     | `512Mi`     |
| `acapy.resources.limits.cpu`      | The cpu limit for the Acapy containers        | `300m`      |
| `acapy.resources.requests.memory` | The requested memory for the Acapy containers | `128Mi`     |
| `acapy.resources.requests.cpu`    | The requested cpu for the Acapy containers    | `120m`      |
| `acapy.podAnnotations`            | Map of annotations to add to the acapy pods   | `{}`        |
| `acapy.podSecurityContext`        | Pod Security Context                          | `{}`        |
| `acapy.containerSecurityContext`  | Container Security Context                    | `{}`        |
| `acapy.service.type`              | Kubernetes Service type                       | `ClusterIP` |
| `acapy.service.adminPort`         | Port to expose for admin service              | `8031`      |
| `acapy.service.httpPort`          | Port to expose for http service               | `8030`      |
| `acapy.affinity`                  | Affinity for acapy pods assignment            | `{}`        |
| `acapy.nodeSelector`              | Node labels for acapy pods assignment         | `{}`        |
| `acapy.tolerations`               | Tolerations for acapy pods assignment         | `[]`        |

### Acapy NetworkPolicy parameters

| Name                                            | Description                                                               | Value   |
| ----------------------------------------------- | ------------------------------------------------------------------------- | ------- |
| `acapy.networkPolicy.enabled`                   | Enable network policies                                                   | `false` |
| `acapy.networkPolicy.ingress.enabled`           | Enable ingress rules                                                      | `false` |
| `acapy.networkPolicy.ingress.namespaceSelector` | Namespace selector label that is allowed to access the Tenant proxy pods. | `{}`    |
| `acapy.networkPolicy.ingress.podSelector`       | Pod selector label that is allowed to access the Tenant proxy pods.       | `{}`    |

### Acapy OpenShift Route parameters

| Name                                                           | Description                                                       | Value   |
| -------------------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| `acapy.openshift.route.enabled`                                | Create OpenShift Route resource for Acapy                         | `false` |
| `acapy.openshift.route.path`                                   | Path that the router watches for, to route traffic to the service | `/`     |
| `acapy.openshift.route.targetPort`                             | Target port for the service                                       | `http`  |
| `acapy.openshift.route.timeout`                                | Timeout in seconds for a route to return                          | `2m`    |
| `acapy.openshift.route.tls.enabled`                            | Enable TLS termination                                            | `true`  |
| `acapy.openshift.route.tls.insecureEdgeTerminationPolicy`      | TLS termination policy                                            | `None`  |
| `acapy.openshift.route.tls.termination`                        | TLS termination type                                              | `edge`  |
| `acapy.openshift.route.wildcardPolicy`                         | Wildcard policy for the route                                     | `None`  |
| `acapy.openshift.adminRoute.enabled`                           | Create OpenShift Route resource for Acapy admin service           | `false` |
| `acapy.openshift.adminRoute.path`                              | Path that the router watches for, to route traffic to the service | `/`     |
| `acapy.openshift.adminRoute.targetPort`                        | Target port for the service                                       | `admin` |
| `acapy.openshift.adminRoute.timeout`                           | Timeout in seconds for a route to return                          | `2m`    |
| `acapy.openshift.adminRoute.tls.enabled`                       | Enable TLS termination                                            | `true`  |
| `acapy.openshift.adminRoute.tls.insecureEdgeTerminationPolicy` | TLS termination policy                                            | `None`  |
| `acapy.openshift.adminRoute.tls.termination`                   | TLS termination type                                              | `edge`  |
| `acapy.openshift.adminRoute.wildcardPolicy`                    | Wildcard policy for the route                                     | `None`  |

### Acapy Secrets Configuration

| Name                                     | Description                             | Value  |
| ---------------------------------------- | --------------------------------------- | ------ |
| `acapy.secret.adminApiKey.generated`     | Generate admin api key                  | `true` |
| `acapy.secret.adminApiKey.value`         | Override admin api key                  | `""`   |
| `acapy.secret.pluginInnkeeper.generated` | Generate plugin innkeeper secret values | `true` |
| `acapy.secret.pluginInnkeeper.walletkey` | Override plugin innkeeper wallet key    | `""`   |
| `acapy.secret.pluginInnkeeper.tenantid`  | Override plugin innkeeper tenant id     | `""`   |

### Tenant Proxy configuration

| Name                                                         | Description                                                                                                         | Value                                 |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `tenant_proxy.image.repository`                              |                                                                                                                     | `ghcr.io/bcgov/traction-tenant-proxy` |
| `tenant_proxy.image.pullPolicy`                              |                                                                                                                     | `IfNotPresent`                        |
| `tenant_proxy.image.pullSecrets`                             |                                                                                                                     | `[]`                                  |
| `tenant_proxy.image.tag`                                     | Overrides the image tag which defaults to the chart appVersion.                                                     | `""`                                  |
| `tenant_proxy.serviceAccount.create`                         | Specifies whether a ServiceAccount should be created                                                                | `false`                               |
| `tenant_proxy.serviceAccount.annotations`                    | Annotations for service account. Evaluated as a template. Only used if `create` is `true`.                          | `{}`                                  |
| `tenant_proxy.serviceAccount.automountServiceAccountToken`   | Automount service account token for the server service account                                                      | `true`                                |
| `tenant_proxy.serviceAccount.name`                           | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""`                                  |
| `tenant_proxy.replicaCount`                                  | Number of Tenant proxy replicas to deploy. Ignored if autoscaling is enabled.                                       | `1`                                   |
| `tenant_proxy.autoscaling.enabled`                           | Enable Horizontal POD autoscaling for Tenant proxy                                                                  | `false`                               |
| `tenant_proxy.autoscaling.minReplicas`                       | Minimum number of Tenant proxy replicas                                                                             | `1`                                   |
| `tenant_proxy.autoscaling.maxReplicas`                       | Maximum number of Tenant proxy replicas                                                                             | `5`                                   |
| `tenant_proxy.autoscaling.targetCPUUtilizationPercentage`    | Target CPU utilization percentage                                                                                   | `80`                                  |
| `tenant_proxy.autoscaling.targetMemoryUtilizationPercentage` | Target Memory utilization percentage                                                                                | `80`                                  |
| `tenant_proxy.autoscaling.stabilizationWindowSeconds`        | Stabilization window in seconds                                                                                     | `300`                                 |
| `tenant_proxy.podAnnotations`                                | Map of annotations to add to the Tenant proxy pods                                                                  | `{}`                                  |
| `tenant_proxy.podSecurityContext`                            | Pod Security Context                                                                                                | `{}`                                  |
| `tenant_proxy.containerSecurityContext`                      | Container Security Context                                                                                          | `{}`                                  |
| `tenant_proxy.service.type`                                  | Kubernetes Service type                                                                                             | `ClusterIP`                           |
| `tenant_proxy.service.port`                                  | Port to expose for http services                                                                                    | `8032`                                |

### Tenant proxy OpenShift Route parameters

| Name                                                             | Description                                                       | Value   |
| ---------------------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| `tenant_proxy.openshift.route.enabled`                           | Create OpenShift Route resource for Tenant proxy                  | `false` |
| `tenant_proxy.openshift.route.path`                              | Path that the router watches for, to route traffic to the service | `/`     |
| `tenant_proxy.openshift.route.targetPort`                        | Target port for the service                                       | `http`  |
| `tenant_proxy.openshift.route.timeout`                           | Timeout in seconds for a route to return                          | `2m`    |
| `tenant_proxy.openshift.route.tls.enabled`                       | Enable TLS termination                                            | `true`  |
| `tenant_proxy.openshift.route.tls.insecureEdgeTerminationPolicy` | TLS termination policy                                            | `None`  |
| `tenant_proxy.openshift.route.tls.termination`                   | TLS termination type                                              | `edge`  |
| `tenant_proxy.openshift.route.wildcardPolicy`                    | Wildcard policy for the route                                     | `None`  |
| `tenant_proxy.resources.limits.memory`                           | The memory limit for the Tenant proxy containers                  | `256Mi` |
| `tenant_proxy.resources.limits.cpu`                              | The cpu limit for the Tenant proxy containers                     | `250m`  |
| `tenant_proxy.resources.requests.memory`                         | The requested memory for the Tenant proxy containers              | `128Mi` |
| `tenant_proxy.resources.requests.cpu`                            | The requested cpu for the Tenant proxy containers                 | `125m`  |

### Tenant Proxy NetworkPolicy parameters

| Name                                                   | Description                                                               | Value   |
| ------------------------------------------------------ | ------------------------------------------------------------------------- | ------- |
| `tenant_proxy.networkPolicy.enabled`                   | Enable network policies                                                   | `false` |
| `tenant_proxy.networkPolicy.ingress.enabled`           | Enable ingress rules                                                      | `true`  |
| `tenant_proxy.networkPolicy.ingress.namespaceSelector` | Namespace selector label that is allowed to access the Tenant proxy pods. | `{}`    |
| `tenant_proxy.networkPolicy.ingress.podSelector`       | Pod selector label that is allowed to access the Tenant proxy pods.       | `{}`    |
| `tenant_proxy.affinity`                                | Affinity for acapy pods assignment                                        | `{}`    |
| `tenant_proxy.nodeSelector`                            | Node labels for acapy pods assignment                                     | `{}`    |
| `tenant_proxy.tolerations`                             | Tolerations for acapy pods assignment                                     | `[]`    |

### Tenant-UI Configuration

| Name                                               | Description                                                                                                         | Value                                          |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| `ui.enabled`                                       | Deploy tenant-ui                                                                                                    | `true`                                         |
| `ui.showOIDCReservationLogin`                      | Use OIDC to make reservations                                                                                       | `false`                                        |
| `ui.quickConnectEndorserName`                      | Flag a ledger as auto-accept/endorse so the Tenant UI can quick connect                                             | `""`                                           |
| `ui.requireEmailForReservation`                    | Whether the Email field is needed for a reservation (if false will default not.applicable@example.com to API)       | `true`                                         |
| `ui.image.repository`                              |                                                                                                                     | `ghcr.io/bcgov/traction-tenant-ui`             |
| `ui.image.pullPolicy`                              |                                                                                                                     | `IfNotPresent`                                 |
| `ui.image.pullSecrets`                             |                                                                                                                     | `[]`                                           |
| `ui.image.tag`                                     | Overrides the image tag which defaults to the chart appVersion.                                                     | `""`                                           |
| `ui.existingSecret`                                | Name of an existing secret to be mounted as environment variables                                                   | `""`                                           |
| `ui.ux.appTitle`                                   | Title of the application                                                                                            | `Traction Tenant Console`                      |
| `ui.ux.appInnkeeperTitle`                          | Title of the Innkeeper Console                                                                                      | `Traction Innkeeper Console`                   |
| `ui.ux.sidebarTitle`                               | Sidebar title                                                                                                       | `Traction`                                     |
| `ui.ux.copyright`                                  |                                                                                                                     | `""`                                           |
| `ui.ux.owner`                                      |                                                                                                                     | `""`                                           |
| `ui.ux.coverImageCopyright`                        |                                                                                                                     | `Photo by Kristoffer Fredriksson on StockSnap` |
| `ui.ux.aboutBusiness.title`                        | The title for the About page business section                                                                       | `Government of British Columbia`               |
| `ui.ux.aboutBusiness.linkTitle`                    | The description for the About page business section link                                                            | `BC Digital Trust Service Agreement`           |
| `ui.ux.aboutBusiness.link`                         | The URL for the About page business section link                                                                    | `https://github.com/bcgov/bc-vcpedia/`         |
| `ui.ux.aboutBusiness.imageUrl`                     | The image in the About page business section                                                                        | `/img/bc/bc_logo.png`                          |
| `ui.oidc.showInnkeeperAdminLogin`                  | Show Innkeeper Admin Login                                                                                          | `true`                                         |
| `ui.oidc.showWritableComponents`                   | Show ledger-write UI components                                                                                     | `true`                                         |
| `ui.oidc.active`                                   | Enable OIDC authentication                                                                                          | `true`                                         |
| `ui.oidc.authority`                                | OIDC authority                                                                                                      | `""`                                           |
| `ui.oidc.client`                                   | OIDC client                                                                                                         | `innkeeper-frontend`                           |
| `ui.oidc.label`                                    | OIDC label                                                                                                          | `IDIR`                                         |
| `ui.oidc.jwksUri`                                  | OIDC jwksUri                                                                                                        | `""`                                           |
| `ui.oidc.realm`                                    | OIDC realm                                                                                                          | `Traction`                                     |
| `ui.oidc.roleName`                                 | OIDC role name                                                                                                      | `innkeeper`                                    |
| `ui.oidc.session.timeoutSeconds`                   | OIDC session timeout seconds                                                                                        | `600`                                          |
| `ui.oidc.session.countdownSeconds`                 | OIDC session countdown seconds                                                                                      | `30`                                           |
| `ui.oidc.extraQueryParams`                         | OIDC client login additional parameters                                                                             | `{}`                                           |
| `ui.smtp.server`                                   | SMTP server                                                                                                         | `""`                                           |
| `ui.smtp.port`                                     | SMTP port                                                                                                           | `25`                                           |
| `ui.smtp.secure`                                   | if true the connection will use TLS when connecting to server. If false (the default) then TLS is used if server supports the STARTTLS extension. In most cases set this value to true if you are connecting to port 465. For port 587 or 25 keep it false | `false`                                        |
| `ui.smtp.user`                                     | SMTP user (Requires setting `ui.existingSecret` with the name of a secret containing `SERVER_SMTP_PASSWORD`)        | `""`                                           |
| `ui.smtp.senderAddress`                            | SMTP sender address                                                                                                 | `""`                                           |
| `ui.smtp.innkeeperInbox`                           | innkeeper notification inbox                                                                                        | `""`                                           |
| `ui.serviceAccount.create`                         | Specifies whether a ServiceAccount should be created                                                                | `false`                                        |
| `ui.serviceAccount.annotations`                    | Annotations for service account. Evaluated as a template. Only used if `create` is `true`.                          | `{}`                                           |
| `ui.serviceAccount.automountServiceAccountToken`   | Automount service account token for the server service account                                                      | `true`                                         |
| `ui.serviceAccount.name`                           | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""`                                           |
| `ui.podAnnotations`                                | Map of annotations to add to the pods                                                                               | `{}`                                           |
| `ui.podSecurityContext`                            | Pod Security Context                                                                                                | `{}`                                           |
| `ui.containerSecurityContext`                      | Container Security Context                                                                                          | `{}`                                           |
| `ui.service.type`                                  | Kubernetes Service type                                                                                             | `ClusterIP`                                    |
| `ui.service.httpPort`                              | Port to expose for http service                                                                                     | `8080`                                         |
| `ui.networkPolicy.enabled`                         | Enable network policies                                                                                             | `false`                                        |
| `ui.networkPolicy.ingress.enabled`                 | Enable ingress rules                                                                                                | `false`                                        |
| `ui.networkPolicy.ingress.namespaceSelector`       | Namespace selector label that is allowed to access the tenant-ui pods.                                              | `{}`                                           |
| `ui.networkPolicy.ingress.podSelector`             | Pod selector label that is allowed to access the tenant-ui pods.                                                    | `{}`                                           |
| `ui.resources.limits.memory`                       | The memory limit for the tenant-ui containers                                                                       | `256Mi`                                        |
| `ui.resources.limits.cpu`                          | The cpu limit for the tenant-ui containers                                                                          | `300m`                                         |
| `ui.resources.requests.memory`                     | The requested memory for the tenant-ui containers                                                                   | `16Mi`                                         |
| `ui.resources.requests.cpu`                        | The requested cpu for the tenant-ui containers                                                                      | `10m`                                          |
| `ui.replicaCount`                                  | Number of tenant-ui replicas to deploy. Ignored if autoscaling is enabled.                                          | `1`                                            |
| `ui.autoscaling.enabled`                           | Enable Horizontal POD autoscaling for tenant-ui                                                                     | `false`                                        |
| `ui.autoscaling.minReplicas`                       | Minimum number of tenant-ui replicas                                                                                | `1`                                            |
| `ui.autoscaling.maxReplicas`                       | Maximum number of tenant-ui replicas                                                                                | `5`                                            |
| `ui.autoscaling.targetCPUUtilizationPercentage`    | Target CPU utilization percentage                                                                                   | `80`                                           |
| `ui.autoscaling.targetMemoryUtilizationPercentage` | Target Memory utilization percentage                                                                                | `80`                                           |
| `ui.nodeSelector`                                  | Node labels for tenant-ui pods assignment                                                                           | `{}`                                           |
| `ui.tolerations`                                   | Tolerations for tenant-ui pods assignment                                                                           | `[]`                                           |
| `ui.affinity`                                      | Affinity for tenant-ui pods assignment                                                                              | `{}`                                           |

### Tenant-UI OpenShift Route parameters

| Name                                                   | Description                                                       | Value   |
| ------------------------------------------------------ | ----------------------------------------------------------------- | ------- |
| `ui.openshift.route.enabled`                           | Create OpenShift Route resource for tenant-ui                     | `false` |
| `ui.openshift.route.path`                              | Path that the router watches for, to route traffic to the service | `/`     |
| `ui.openshift.route.targetPort`                        | Target port for the service                                       | `http`  |
| `ui.openshift.route.timeout`                           | Timeout in seconds for a route to return                          | `2m`    |
| `ui.openshift.route.tls.enabled`                       | Enable TLS termination                                            | `true`  |
| `ui.openshift.route.tls.insecureEdgeTerminationPolicy` | TLS termination policy                                            | `None`  |
| `ui.openshift.route.tls.termination`                   | TLS termination type                                              | `edge`  |
| `ui.openshift.route.wildcardPolicy`                    | Wildcard policy for the route                                     | `None`  |

### Ingress Configuration

| Name                  | Description                                                                   | Value  |
| --------------------- | ----------------------------------------------------------------------------- | ------ |
| `ingress.enabled`     | Enable ingress record generation for traction                                 | `true` |
| `ingress.className`   | IngressClass that will be be used to implement the Ingress (Kubernetes 1.18+) | `""`   |
| `ingress.annotations` | Additional annotations for the Ingress resource.                              | `{}`   |
| `ingress.tls`         | Enable TLS configuration for the host defined at ingress.                     | `[]`   |

### PostgreSQL parameters

| Name                                                  | Description                                                                                                                                                                                                                                                                                                                                                                    | Value                               |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| `postgresql.enabled`                                  | Deploy Bitnami PostgreSQL chart.                                                                                                                                                                                                                                                                                                                                               | `true`                              |
| `postgresql.fullnameOverride`                         | When overriding fullnameOverride, you must override this to match.                                                                                                                                                                                                                                                                                                             | `""`                                |
| `postgresql.architecture`                             | PostgreSQL architecture (`standalone` or `replication`)                                                                                                                                                                                                                                                                                                                        | `standalone`                        |
| `postgresql.auth.enablePostgresUser`                  | Assign a password to the "postgres" admin user. Otherwise, remote access will be blocked for this user                                                                                                                                                                                                                                                                         | `true`                              |
| `postgresql.auth.existingSecret`                      | Name of existing secret to use for PostgreSQL credentials. `postgresql.auth.postgresPassword`, `postgresql.auth.password`, and `postgresql.auth.replicationPassword` will be ignored and picked up from this secret. The secret might also contains the key `ldap-password` if LDAP is enabled. `ldap.bind_password` will be ignored and picked from this secret in this case. | `{{ include "global.fullname" . }}` |
| `postgresql.auth.secretKeys.adminPasswordKey`         | Name of key in existing secret to use for PostgreSQL credentials. Only used when `auth.existingSecret` is set.                                                                                                                                                                                                                                                                 | `admin-password`                    |
| `postgresql.auth.secretKeys.userPasswordKey`          | Name of key in existing secret to use for PostgreSQL credentials. Only used when `auth.existingSecret` is set.                                                                                                                                                                                                                                                                 | `database-password`                 |
| `postgresql.auth.database`                            | Name for a custom database to create                                                                                                                                                                                                                                                                                                                                           | `traction`                          |
| `postgresql.auth.username`                            | Name for a custom user to create                                                                                                                                                                                                                                                                                                                                               | `acapy`                             |
| `postgresql.primary.persistence.enabled`              | Enable PostgreSQL Primary data persistence using PVC                                                                                                                                                                                                                                                                                                                           | `true`                              |
| `postgresql.primary.persistence.size`                 | PVC Storage Request for PostgreSQL volume                                                                                                                                                                                                                                                                                                                                      | `1Gi`                               |
| `postgresql.primary.containerSecurityContext.enabled` | Enable container security context                                                                                                                                                                                                                                                                                                                                              | `false`                             |
| `postgresql.primary.podSecurityContext.enabled`       | Enable security context                                                                                                                                                                                                                                                                                                                                                        | `false`                             |
| `postgresql.primary.resources.limits.memory`          | The memory limit for the PostgreSQL Primary containers                                                                                                                                                                                                                                                                                                                         | `2600Mi`                            |
| `postgresql.primary.resources.limits.cpu`             | The cpu limit for the PostgreSQL Primary containers                                                                                                                                                                                                                                                                                                                            | `600m`                              |
| `postgresql.primary.resources.requests.memory`        | The requested memory for the PostgreSQL Primary containers                                                                                                                                                                                                                                                                                                                     | `1300Mi`                            |
| `postgresql.primary.resources.requests.cpu`           | The requested cpu for the PostgreSQL Primary containers                                                                                                                                                                                                                                                                                                                        | `300m`                              |
| `postgresql.primary.service.ports.postgresql`         | PostgreSQL service port                                                                                                                                                                                                                                                                                                                                                        | `5432`                              |
| `postgresql.primary.extendedConfiguration`            | Extended PostgreSQL Primary configuration (appended to main or default configuration)                                                                                                                                                                                                                                                                                          | `max_connections = 500
`            |
| `postgresql-ha.enabled`                               | Deploy HA PostgreSQL chart. Not currently supported, provided for future use.                                                                                                                                                                                                                                                                                                  | `false`                             |


## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| i5okie | <ivan.polchenko@quartech.com> | <https://github.com/i5okie> |
| usingtechnology | <tools@usingtechnolo.gy> | <https://github.com/usingtechnology> |
| Jsyro | <jason.syrotuck@nttdata.com> | <https://github.com/Jsyro> |
| esune | <emiliano.sune@quartech.com> | <https://github.com/esune> |

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

<https://github.com/bcgov/traction/blob/main/LICENSE>

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
