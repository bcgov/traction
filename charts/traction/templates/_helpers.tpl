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
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "acapy.database.secret.name" -}}
{{ template "global.fullname" . }}-postgresql
{{- end -}}

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
Create a default fully qualified acapy name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "acapy.walletkey.secret.name" -}}
{{ template "acapy.fullname" . }}-walletkey
{{- end -}}

{{/*
Create a default fully qualified acapy innkeeper plugin name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "acapy.plugin.innkeeper.name" -}}
{{ template "acapy.fullname" . }}-plugin-innkeeper
{{- end -}}

{{/*
Create a default fully qualified tenant proxy name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "tenant_proxy.fullname" -}}
{{ template "global.fullname" . }}-tenant-proxy
{{- end -}}


{{/*
generate ledger browser url
*/}}
{{- define "traction.ledgerBrowser" -}}
{{- $ledgerBrowser := dict "bcovrin-test" "http://test.bcovrin.vonx.io" -}}
{{ .Values.traction.config.ledger.browserUrlOverride | default ( get $ledgerBrowser .Values.global.ledger ) }}
{{- end }}

{{/*
generate genesisfileurl
*/}}
{{- define "traction.genesisUrl" -}}
{{ default (printf "%s%s" (include "traction.ledgerBrowser" .) "/genesis") .Values.traction.config.ledger.genesisUrlOverride }}
{{- end }}


{{/*
Common acapy labels
*/}}
{{- define "acapy.labels" -}}
{{ include "common.labels" . }}
{{ include "acapy.selectorLabels" . }}
{{- end }}

{{/*
Selector acapy labels
*/}}
{{- define "acapy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "acapy.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{/*
generate hosts if not overriden
*/}}
{{- define "acapy.host" -}}
{{- include "acapy.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end }}

{{/*
generate admin url (internal)
*/}}
{{- define "acapy.internal.admin.url" -}}
http://{{- include "acapy.fullname" . }}:{{.Values.acapy.service.adminPort }}
{{- end }}

{{/*
generate hosts for acapy admin if not overriden
*/}}
{{- define "acapy.admin.host" -}}
{{- include "acapy.fullname" . }}-admin{{ .Values.global.ingressSuffix -}}
{{- end }}

{{/*
Return seed
*/}}
{{- define "acapy.seed" -}}
{{- if .Values.acapy.agentSeed -}}
    {{- .Values.acapy.agentSeed -}}
{{- else -}}
    {{ include "getOrGeneratePass" (dict "Namespace" .Release.Namespace "Kind" "Secret" "Name" (include "acapy.fullname" .) "Key" "seed" "Length" 32) }}
{{- end -}}
{{- end -}}

{{/*
Return acapy label
*/}}
{{- define "acapy.label" -}}
{{- if .Values.acapy.labelOverride -}}
    {{- .Values.acapy.labelOverride }}
{{- else if eq .Values.global.ledger "idu" -}}
$identifier   
{{- else -}} 
    {{- .Release.Name }}     
{{- end -}}
{{- end -}}

{{/*
Return acapy initialization call
*/}}
{{- define "acapy.registerLedger" -}}
{{- if (eq .Values.global.ledger "bcovrin-test") -}}
curl -d '{\"seed\":\"$(ACAPY_WALLET_SEED)\", \"role\":\"TRUST_ANCHOR\", \"alias\":\"{{ include "acapy.fullname" . }}\"}' -X POST {{ include "traction.ledgerBrowser" . }}/register;
{{- end -}}
{{- end -}}

{{/*
generate tails baseUrl
*/}}
{{- define "acapy.tails.baseUrl" -}}
{{- $tailsBaseUrl := dict "bcovrin-dev" "https://tails-dev.vonx.io" "bcovrin-test" "https://tails-test.vonx.io" "idu" (printf "https://tails%s" .Values.global.ingressSuffix) -}}
{{ .Values.acapy.tails.baseUrlOverride| default ( get $tailsBaseUrl .Values.global.ledger ) }}
{{- end }}

{{/*
generate tails uploadUrl
*/}}
{{- define "acapy.tails.uploadUrl" -}}
{{- $tailsUploadUrl:= dict "bcovrin-dev" "https://tails-dev.vonx.io" "bcovrin-test" "https://tails-test.vonx.io" "idu" "http://idu-tails:6543" -}}
{{ .Values.acapy.tails.uploadUrlOverride| default ( get $tailsUploadUrl .Values.global.ledger ) }}
{{- end }}

{{/*
Create a default fully qualified app name for the postgres requirement.
*/}}
{{- define "global.postgresql.fullname" -}}
{{- if .Values.postgresql.fullnameOverride }}
{{- .Values.postgresql.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $postgresContext := dict "Values" .Values.postgresql "Release" .Release "Chart" (dict "Name" "postgresql") -}}
{{ template "postgresql.primary.fullname" $postgresContext }}
{{- end -}}
{{- end -}}

{{/*
Create the name for the database secret.
*/}}
{{- define "global.externalDbSecret" -}}
{{- if .Values.global.persistence.existingSecret -}}
  {{- .Values.global.persistence.existingSecret -}}
{{- else -}}
  {{- template "global.fullname" . -}}-db
{{- end -}}
{{- end -}}

{{/*
Create the name for the password secret key.
*/}}
{{- define "global.dbPasswordKey" -}}
{{- if .Values.global.persistence.existingSecret -}}
  {{- .Values.global.persistence.existingSecretKey -}}
{{- else -}}
  password
{{- end -}}
{{- end -}}

{{/*
Create environment variables for database configuration.
*/}}
{{- define "global.externalDbConfig" -}}
- name: DB_VENDOR
  value: {{ .Values.global.persistence.dbVendor | quote }}
{{- if eq .Values.global.persistence.dbVendor "POSTGRES" }}
- name: POSTGRES_PORT_5432_TCP_ADDR
  value: {{ .Values.global.persistence.dbHost | quote }}
- name: POSTGRES_PORT_5432_TCP_PORT
  value: {{ .Values.global.persistence.dbPort | quote }}
- name: POSTGRES_USER
  value: {{ .Values.global.persistence.dbUser | quote }}
- name: POSTGRES_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ template "global.externalDbSecret" . }}
      key: {{ include "global.dbPasswordKey" . | quote }}
- name: POSTGRES_DATABASE
  value: {{ .Values.global.persistence.dbName | quote }}
{{- else if eq .Values.global.persistence.dbVendor "MYSQL" }}
- name: MYSQL_PORT_3306_TCP_ADDR
  value: {{ .Values.global.persistence.dbHost | quote }}
- name: MYSQL_PORT_3306_TCP_PORT
  value: {{ .Values.global.persistence.dbPort | quote }}
- name: MYSQL_USER
  value: {{ .Values.global.persistence.dbUser | quote }}
- name: MYSQL_PASSWORD
  valueFrom:
    secretKeyRef:
      name: {{ template "global.externalDbSecret" . }}
      key: {{ include "global.dbPasswordKey" . | quote }}
- name: MYSQL_DATABASE
  value: {{ .Values.global.persistence.dbName | quote }}
{{- end }}
{{- end -}}

{{- define "acapy.openshift.route.tls" -}}
{{- if (.Values.acapy.openshift.route.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.acapy.openshift.route.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.acapy.openshift.route.tls.termination }}
{{- end -}}
{{- end -}}

{{- define "acapy.openshift.adminRoute.tls" -}}
{{- if (.Values.acapy.openshift.adminRoute.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.acapy.openshift.adminRoute.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.acapy.openshift.adminRoute.tls.termination }}
{{- end -}}
{{- end -}}

{{/*
Common tenant proxy labels
*/}}
{{- define "tenant_proxy.labels" -}}
{{ include "common.labels" . }}
{{ include "tenant_proxy.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
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
Mount the tenant proxy config map as env vars
*/}}
{{- define "tenant_proxy.configmap.env.vars" -}}
envFrom:
  - configMapRef:
      name: {{ template "tenant_proxy.fullname" . }}-img
{{- end -}}

{{/*
generate tenant proxy hosts if not overriden
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

