#!/usr/bin/env bash

# Quit unless there is a token
if [ $# -eq 0 ]; then
  echo "Please provide a valid token"
  exit 1
fi

test_url="https://traction-api-test.apps.silver.devops.gov.bc.ca/tenant/v1/governance/schema_templates"
proxy_url="https://localhost:8080/api/traction/tenant/v1/governance/schema_templates"

payload="
  {
      \"schema_definition\": {
          \"schema_name\": \"my_schema\",
          \"schema_version\": \"1.0.0\",
          \"attributes\": [
              \"my_attribute\"
          ]
      },
      \"name\": \"my_schema\",
      \"tags\": [],
      \"credential_definition\": {
          \"tag\": \"string\",
          \"revocation_enabled\": false,
          \"revocation_registry_size\": 0
      }
  }
"

curl -X 'POST' \
  url \
  -H "accept: application/json" \
  -H "Authorization: Bearer $1" \
  -H "Content-Type: application/json" \
  -d payload
