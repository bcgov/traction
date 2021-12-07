{{/*
Expand the name of the chart.
*/}}
{{- define "tekton.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "tekton.fullname" -}}
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
{{- define "tekton.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "tekton.labels" -}}
helm.sh/chart: {{ include "tekton.chart" . }}
{{ include "tekton.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "tekton.selectorLabels" -}}
app.kubernetes.io/name: {{ include "tekton.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "tekton.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "tekton.fullname" .) .Values.serviceAccount.name }}-sa
{{- else }}
{{- default "default" .Values.serviceAccount.name }}-sa
{{- end }}
{{- end }}

{{/*
Create the role for the service account to use
*/}}
{{- define "tekton.serviceAccountRole" -}}
{{- include "tekton.serviceAccountName" . }}-role
{{- end }}

{{/*
Create the role for the service account to use
*/}}
{{- define "tekton.serviceAccountBinding" -}}
{{- include "tekton.serviceAccountRole" . }}-binding
{{- end }}

{{/*
Create the name of the github secret to use
*/}}
{{- define "tekton.githubSecret" -}}
{{- if .Values.githubSecret.create }}
{{- default (include "tekton.fullname" .) .Values.githubSecret.name }}-github
{{- else }}
{{- default "default" .Values.githubSecret.name }}-github
{{- end }}
{{- end }}

{{/*
Create the name of the pipeline
*/}}
{{- define "tekton.pipelineName" -}}
{{- if .Values.pipeline.create }}
{{- default (include "tekton.fullname" .) .Values.pipeline.name }}-pipeline
{{- else }}
{{- default "default" .Values.pipeline.name }}-pipeline
{{- end }}
{{- end }}

{{/*
Create the name of the trigger/event listener to use
*/}}
{{- define "tekton.triggers.pr.name" -}}
{{- default (include "tekton.fullname" .) }}
{{- end }}

{{/*
Create the name of the trigger/event listener to use
*/}}
{{- define "tekton.triggers.pr.listenerName" -}}
{{- default (include "tekton.triggers.pr.name" .) }}-github
{{- end }}

{{/*
Create the name of the trigger template to use
*/}}
{{- define "tekton.triggers.pr.templateName" -}}
{{- default (include "tekton.triggers.pr.name" .) }}-template
{{- end }}

{{/*
Create the name of the trigger binding to use
*/}}
{{- define "tekton.triggers.pr.bindingName" -}}
{{- default (include "tekton.triggers.pr.name" .) }}-binding
{{- end }}

{{- define "tekton.pipelineRunName" -}}
{{- default (include "tekton.pipelineName" .)  }}-run-
{{- end }}

{{- define "tekton.pipelinePvcName" -}}
{{- default (include "tekton.pipelineName" .) }}-pvc
{{- end }}

{{/*
generate listener hosts
*/}}
{{- define "tekton.triggers.pr.listenerHost" -}}
{{- include "tekton.triggers.pr.listenerName" . }}{{ .Values.listeners.ingressSuffix -}}
{{- end }}

{{/*
generate listener service name
*/}}
{{- define "tekton.triggers.pr.listenerService" -}}
el-{{- include "tekton.triggers.pr.listenerName" . }}
{{- end }}