#!/usr/bin/env bash

contacts=(
  "Ernie"
  "Bert"
  "Cookie Monster"
  "Oscar"
  "Scooby Doo"
  "Shaggy"
  "Velma"
  "Daphne"
  "Fred"
  "Optimus"
  "Bambi"
  "Marge"
)

# Quit unless there is a token
if [ $# -eq 0 ]; then
  echo "Please provide a valid token"
  exit 1
fi

for contact in "${contacts[@]}"; do
  echo "Creating contact: $contact"
  curl -X 'POST' \
    "http://localhost:5100/tenant/v1/contacts/create-invitation" \
    -H "accept: application/json" \
    -H "Authorization: Bearer $1" \
    -H "Content-Type: application/json" \
    -d "{ \"alias\":\"$contact\", \"invitation_type\": \"connections/1.0\" }"
  sleep 0.5 # Throttle requests
done