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
Create a default fully qualified postgresql name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "postgresql.secret.name" -}}
{{ template "global.fullname" . }}-db
{{- end -}}


{{/*
Create a default fully qualified traction showcase name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "showcase.fullname" -}}
{{ template "global.fullname" . }}-app
{{- end -}}

{{/*
Create a default fully qualified traction showcase name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
*/}}
{{- define "showcase.secret.name" -}}
{{ template "showcase.fullname" . }}
{{- end -}}

{{/*
Common traction showcase labels
*/}}
{{- define "showcase.labels" -}}
{{ include "common.labels" . }}
{{ include "showcase.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector traction showcase labels
*/}}
{{- define "showcase.selectorLabels" -}}
app.kubernetes.io/name: {{ include "showcase.fullname" . }}
{{ include "common.selectorLabels" . }}
{{- end }}

{{/*
Mount the traction showcase config map as env vars
*/}}
{{- define "showcase.configmap.env.vars" -}}
envFrom:
  - configMapRef:
      name: {{ template "showcase.fullname" . }}
{{- end -}}

{{/*
Create the name of the traction showcase service account to use
*/}}
{{- define "showcase.serviceAccountName" -}}
{{- if .Values.showcase.serviceAccount.create }}
{{- default (include "showcase.fullname" .) .Values.showcase.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.showcase.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
generate traction showcase hosts if not overriden
*/}}
{{- define "showcase.host" -}}
{{- include "showcase.fullname" . }}{{ .Values.global.ingressSuffix -}}
{{- end }}

{{- define "showcase.openshift.route.tls" -}}
{{- if (.Values.showcase.openshift.route.tls.enabled) -}}
tls:
  insecureEdgeTerminationPolicy: {{ .Values.showcase.openshift.route.tls.insecureEdgeTerminationPolicy }}
  termination: {{ .Values.showcase.openshift.route.tls.termination }}
{{- end -}}
{{- end -}}

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