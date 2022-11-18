{{/*
Expand the name of the chart.
*/}}
{{- define "global.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "global.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
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
Create a default fully qualified acapy name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "acapy.fullname" -}}
{{ template "global.fullname" . }}-acapy
{{- end -}}

{{/*
Create a default fully qualified acapy name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "acapy.api.secret.name" -}}
{{ template "acapy.fullname" . }}-api
{{- end -}}

{{/*
Create a default fully qualified traction tenant ui name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "tenant_ui.fullname" -}}
{{ template "global.fullname" . }}
{{- end -}}

{{/*
Create a default fully qualified traction tenant ui name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "tenant_ui.secret.name" -}}
{{ template "tenant_ui.fullname" . }}
{{- end -}}

{{/*
Common traction tenant ui labels
*/}}
{{- define "tenant_ui.labels" -}}
{{ include "common.labels" . }}
{{ include "tenant_ui.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector traction tenant ui labels
*/}}
{{- define "tenant_ui.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tenant_ui.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{/*
Mount the traction tenant ui config map as env vars
*/}}
{{- define "tenant_ui.configmap.env.vars" -}}
envFrom:
  - configMapRef:
      name: {{ template "tenant_ui.fullname" . }}
{{- end -}}

{{/*
Create the name of the traction tenant ui service account to use
*/}}
{{- define "tenant_ui.serviceAccountName" -}}
{{- if .Values.tenant_ui.serviceAccount.create }}
{{- default (include "tenant_ui.fullname" .) .Values.tenant_ui.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.tenant_ui.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
generate traction tenant ui hosts if not overriden
*/}}
{{- define "tenant_ui.host" -}}
{{- include "tenant_ui.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end }}

{{- define "tenant_ui.openshift.route.tls" -}}
{{- if (.Values.tenant_ui.openshift.route.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.tenant_ui.openshift.route.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.tenant_ui.openshift.route.tls.termination }}
{{- end -}}
{{- end -}}
