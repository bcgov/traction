# tenant-ui

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.2.14](https://img.shields.io/badge/AppVersion-0.2.14-informational?style=flat-square)

The Traction Tenant UI allows tenants to manage their agent.

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
| https://charts.bitnami.com/bitnami | common | 2.x.x |

## Parameters

### Common parameters

| Name                                            | Description                                                                                                         | Value                              |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| `image.repository`                              |                                                                                                                     | `ghcr.io/bcgov/traction-tenant-ui` |
| `image.pullPolicy`                              |                                                                                                                     | `IfNotPresent`                     |
| `image.pullSecrets`                             |                                                                                                                     | `[]`                               |
| `image.tag`                                     | Overrides the image tag which defaults to the chart appVersion.                                                     | `""`                               |
| `nameOverride`                                  |                                                                                                                     | `""`                               |
| `fullnameOverride`                              |                                                                                                                     | `""`                               |
| `ingressSuffix`                                 | Domain suffix to be used for default hostpaths in ingress                                                           | `-dev.example.com`                 |
| `serviceAccount.create`                         | Specifies whether a ServiceAccount should be created                                                                | `false`                            |
| `serviceAccount.annotations`                    | Annotations for service account. Evaluated as a template. Only used if `create` is `true`.                          | `{}`                               |
| `serviceAccount.automountServiceAccountToken`   | Automount service account token for the server service account                                                      | `true`                             |
| `serviceAccount.name`                           | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `""`                               |
| `podAnnotations`                                | Map of annotations to add to the pods                                                                               | `{}`                               |
| `podSecurityContext`                            | Pod Security Context                                                                                                | `{}`                               |
| `containerSecurityContext`                      | Container Security Context                                                                                          | `{}`                               |
| `service.type`                                  | Kubernetes Service type                                                                                             | `ClusterIP`                        |
| `service.httpPort`                              | Port to expose for http service                                                                                     | `8080`                             |
| `networkPolicy.enabled`                         | Enable network policies                                                                                             | `false`                            |
| `networkPolicy.ingress.enabled`                 | Enable ingress rules                                                                                                | `false`                            |
| `networkPolicy.ingress.namespaceSelector`       | Namespace selector label that is allowed to access the tenant-ui pods.                                              | `{}`                               |
| `networkPolicy.ingress.podSelector`             | Pod selector label that is allowed to access the tenant-ui pods.                                                    | `{}`                               |
| `ingress.enabled`                               | Enable ingress record generation for tenant-ui                                                                      | `true`                             |
| `ingress.ingressClassName`                      | IngressClass that will be be used to implement the Ingress (Kubernetes 1.18+)                                       | `""`                               |
| `ingress.annotations`                           | Additional annotations for the Ingress resource.                                                                    | `{}`                               |
| `ingress.tls`                                   | Enable TLS configuration for the host defined at ingress.                                                           | `[]`                               |
| `resources.limits.memory`                       | The memory limit for the tenant-ui containers                                                                       | `2600Mi`                           |
| `resources.limits.cpu`                          | The cpu limit for the tenant-ui containers                                                                          | `600m`                             |
| `resources.requests.memory`                     | The requested memory for the tenant-ui containers                                                                   | `1300Mi`                           |
| `resources.requests.cpu`                        | The requested cpu for the tenant-ui containers                                                                      | `300m`                             |
| `replicaCount`                                  | Number of tenant-ui replicas to deploy. Ignored if autoscaling is enabled.                                          | `1`                                |
| `autoscaling.enabled`                           | Enable Horizontal POD autoscaling for tenant-ui                                                                     | `false`                            |
| `autoscaling.minReplicas`                       | Minimum number of tenant-ui replicas                                                                                | `1`                                |
| `autoscaling.maxReplicas`                       | Maximum number of tenant-ui replicas                                                                                | `5`                                |
| `autoscaling.targetCPUUtilizationPercentage`    | Target CPU utilization percentage                                                                                   | `80`                               |
| `autoscaling.targetMemoryUtilizationPercentage` | Target Memory utilization percentage                                                                                | `80`                               |
| `nodeSelector`                                  | Node labels for tenant-ui pods assignment                                                                           | `{}`                               |
| `tolerations`                                   | Tolerations for tenant-ui pods assignment                                                                           | `[]`                               |
| `affinity`                                      | Affinity for tenant-ui pods assignment                                                                              | `{}`                               |

### OpenShift Route parameters

| Name                                                | Description                                                       | Value   |
| --------------------------------------------------- | ----------------------------------------------------------------- | ------- |
| `openshift.route.enabled`                           | Create OpenShift Route resource for tenant-ui                     | `false` |
| `openshift.route.path`                              | Path that the router watches for, to route traffic to the service | `/`     |
| `openshift.route.targetPort`                        | Target port for the service                                       | `http`  |
| `openshift.route.timeout`                           | Timeout in seconds for a route to return                          | `2m`    |
| `openshift.route.tls.enabled`                       | Enable TLS termination                                            | `true`  |
| `openshift.route.tls.insecureEdgeTerminationPolicy` | TLS termination policy                                            | `None`  |
| `openshift.route.tls.termination`                   | TLS termination type                                              | `edge`  |
| `openshift.route.wildcardPolicy`                    | Wildcard policy for the route                                     | `None`  |

### Frontend Configuration

| Name                             | Description                    | Value                                          |
| -------------------------------- | ------------------------------ | ---------------------------------------------- |
| `ux.appTitle`                    | Title of the application       | `Traction Tenant Console`                      |
| `ux.appInnkeeperTitle`           | Title of the Innkeeper Console | `Traction Innkeeper Console`                   |
| `ux.sidebarTitle`                | Sidebar title                  | `Traction`                                     |
| `ux.copyright`                   |                                | `""`                                           |
| `ux.owner`                       |                                | `""`                                           |
| `ux.coverImageCopyright`         |                                | `Photo by Kristoffer Fredriksson on StockSnap` |
| `ariesDetails.ledgerDescription` | Ledger description             | `bcovrin-test`                                 |

### Backend Configuration

| Name                                      | Description                                                                                          | Value                               |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------- |
| `oidc.showInnkeeperAdminLogin`            | Show Innkeeper Admin Login                                                                           | `true`                              |
| `oidc.active`                             | Enable OIDC authentication                                                                           | `true`                              |
| `oidc.authority`                          | OIDC authority                                                                                       | `""`                                |
| `oidc.client`                             | OIDC client                                                                                          | `innkeeper-frontend`                |
| `oidc.label`                              | OIDC label                                                                                           | `IDIR`                              |
| `oidc.jwksUri`                            | OIDC jwksUri                                                                                         | `""`                                |
| `oidc.realm`                              | OIDC realm                                                                                           | `Traction`                          |
| `oidc.roleName`                           | OIDC role name                                                                                       | `innkeeper`                         |
| `smtp.server`                             | SMTP server                                                                                          | `""`                                |
| `smtp.port`                               | SMTP port                                                                                            | `25`                                |
| `smtp.senderAddress`                      | SMTP sender address                                                                                  | `""`                                |
| `smtp.innkeeperInbox`                     | innkeeper notification inbox                                                                         | `""`                                |
| `traction.pluginInnkeeper.existingSecret` | Name of the existing secret for Acapy plugin Innkeeper. Must contain keys `tenantid` and `walletkey` | `""`                                |
| `traction.pluginInnkeeper.tenantid`       | Tenant ID, ignored if existingSecret is set                                                          | `""`                                |
| `traction.pluginInnkeeper.walletkey`      | Wallet key, ignored if existingSecret is set                                                         | `""`                                |
| `traction.apiEndpoint`                    | Traction API endpoint                                                                                | `http://traction-tenant-proxy:8030` |
| `traction.tenantProxyEndpoint`            | Traction Tenant Proxy endpoint                                                                       | `http://traction-tenant-proxy:8030` |
