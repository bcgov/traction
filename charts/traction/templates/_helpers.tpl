{{/*
Expand the name of the chart.
*/}}
{{- define "global.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "global.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "global.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "common.labels" -}}
app: {{ include "global.name" . }}
helm.sh/chart: {{ include "global.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector common labels
*/}}
{{- define "common.selectorLabels" -}}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Returns a secret if it already in Kubernetes, otherwise it creates
it randomly.
*/}}
{{- define "getOrGeneratePass" }}
{{- $len := (default 16 .Length) | int -}}
{{- $obj := (lookup "v1" .Kind .Namespace .Name).data -}}
{{- if $obj }}
{{- index $obj .Key -}}
{{- else if (eq (lower .Kind) "secret") -}}
{{- randAlphaNum $len | b64enc -}}
{{- else -}}
{{- randAlphaNum $len -}}
{{- end -}}
{{- end }}

{{/*
Returns a secret if it already in Kubernetes, otherwise it creates
it randomly.
*/}}
{{- define "getOrGenerateUUID" }}
{{- $obj := (lookup "v1" .Kind .Namespace .Name).data -}}
{{- if $obj }}
{{- index $obj .Key -}}
{{- else if (eq (lower .Kind) "secret") -}}
{{- uuidv4 | b64enc -}}
{{- end -}}
{{- end }}

{{/*
Create a default fully qualified tenant proxy name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "tenant_proxy.fullname" -}}
{{ template "global.fullname" . }}-tenant-proxy
{{- end -}}

{{/*
Create a default fully qualified tenant-ui name.
*/}}
{{- define "tenant-ui.fullname" -}}
{{ template "global.fullname" . }}-tenant-ui
{{- end -}}

{{/*
tenant-ui labels
*/}}
{{- define "tenant-ui.labels" -}}
{{ include "common.labels" . }}
{{ include "tenant-ui.selectorLabels" . }}
{{- end }}

{{/*
tenant-ui selector labels
*/}}
{{- define "tenant-ui.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tenant-ui.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{/*
Create the name of the tenant-ui service account to use
*/}}
{{- define "tenant-ui.serviceAccountName" -}}
{{- if .Values.ui.serviceAccount.create }}
{{- default (include "tenant-ui.fullname" .) .Values.ui.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.ui.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate tenant-ui host if not overriden
*/}}
{{- define "tenant-ui.host" -}}
{{- include "tenant-ui.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end -}}

{{/*
Generate tenant-ui openshift route tls config
*/}}
{{- define "tenant-ui.openshift.route.tls" -}}
{{- if (.Values.openshift.route.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.openshift.route.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.openshift.route.tls.termination }}
{{- end -}}
{{- end -}}

{{/*
Common tenant proxy labels
*/}}
{{- define "tenant_proxy.labels" -}}
{{ include "common.labels" . }}
{{- end }}

{{/*
Selector tenant proxy labels
*/}}
{{- define "tenant_proxy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tenant_proxy.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{/*
Create the name of the tenant proxy service account to use
*/}}
{{- define "tenant_proxy.serviceAccountName" -}}
{{- if .Values.tenant_proxy.serviceAccount.create }}
{{- default (include "tenant_proxy.fullname" .) .Values.tenant_proxy.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.tenant_proxy.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Generate tenant proxy hosts if not overriden
*/}}
{{- define "tenant_proxy.host" -}}
{{- include "tenant_proxy.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end }}

{{- define "tenant_proxy.openshift.route.tls" -}}
{{- if (.Values.tenant_proxy.openshift.route.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.tenant_proxy.openshift.route.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.tenant_proxy.openshift.route.tls.termination }}
{{- end -}}
{{- end -}}

{{/*
ACA-Py dependency related template functions
These functions reference the ACA-Py subchart properly
*/}}

{{/* Define ACA-Py base name */}}
{{- define "traction.acapy.name" -}}
{{- default "acapy" .Values.acapy.nameOverride -}}
{{- end -}}

{{/*
Returns ACA-Py Fullname
*/}}
{{- define "traction.acapy.fullname" -}}
{{- if .Values.acapy.fullnameOverride }}
{{- .Values.acapy.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" (include "global.fullname" .) (include "traction.acapy.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end }}
{{- end }}

{{/*
Multitenancy config
*/}}
{{- define "traction.acapy.multitenancyConfiguration" -}}
{{- if .Values.acapy.multitenancyConfiguration.json -}}
{{- .Values.acapy.multitenancyConfiguration.json -}}
{{- else -}}
'{"wallet_type":"{{ .Values.acapy.multitenancyConfiguration.wallet_type | default "single-wallet-askar" }}"}'
{{- end -}}
{{- end -}}

{{/*
Generate ACA-Py host from dependency subchart
Since we're using Traction's ingress instead of ACA-Py's, we use the ingressSuffix pattern
*/}}
{{- define "traction.acapy.host" -}}
{{- template "traction.acapy.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end -}}

{{/*
Generate ACA-Py admin host from dependency subchart
Since we're using Traction's ingress instead of ACA-Py's, we use the ingressSuffix pattern
*/}}
{{- define "traction.acapy.admin.host" -}}
{{- template "traction.acapy.fullname" . }}-admin{{ .Values.global.ingressSuffix -}}
{{- end -}}

{{/*
Generate ACA-Py internal admin URL for tenant proxy
*/}}
{{- define "traction.acapy.internal.admin.url" -}}
http://{{- template "traction.acapy.fullname" . }}:{{ .Values.acapy.service.ports.admin | default 8022 }}
{{- end -}}

{{/*
ACA-Py API secret name (for tenant proxy)
*/}}
{{- define "traction.acapy.api.secretName" -}}
{{- template "traction.acapy.fullname" . }}-api
{{- end -}}

{{/*
ACA-Py plugin innkeeper secret name (for tenant ui)
*/}}
{{- define "traction.acapy.plugin.innkeeper.name" -}}
{{- template "traction.acapy.fullname" . }}-plugin-innkeeper
{{- end -}}
