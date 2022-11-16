#!/bin/bash

# based on code developed by Sovrin:  https://github.com/hyperledger/aries-acapy-plugin-toolbox

if [[ "${TRACTION_ENV}" == "local" ]]; then
	echo "using ngrok end point [$NGROK_NAME]"

	NGROK_ENDPOINT=null
	while [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]
	do
	    echo "Fetching end point from ngrok service"
	    NGROK_ENDPOINT=$(curl --silent $NGROK_NAME:4040/api/tunnels | ./jq -r '.tunnels[] | select(.proto=="https") | .public_url')

	    if [ -z "$NGROK_ENDPOINT" ] || [ "$NGROK_ENDPOINT" = "null" ]; then
	        echo "ngrok not ready, sleeping 5 seconds...."
	        sleep 5
	    fi
	done

	export ACAPY_ENDPOINT=$NGROK_ENDPOINT
fi

echo "fetched end point [$ACAPY_ENDPOINT]"

echo "Starting aca-py agent ..."

# ... if you want to echo the aca-py startup command ...
# set -x

exec aca-py start \
    --auto-provision \
    --arg-file acapy-static-args.yml \
    --inbound-transport http "0.0.0.0" ${ACAPY_HTTP_PORT} \
    --webhook-url "${TRACTION_WEBHOOK_URL}" \
    --genesis-url "${ACAPY_GENESIS_URL}" \
    --endpoint ${ACAPY_ENDPOINT} \
    --wallet-name "${ACAPY_WALLET_DATABASE}" \
    --wallet-key "${ACAPY_WALLET_ENCRYPTION_KEY}" \
    --wallet-storage-type "${ACAPY_WALLET_STORAGE_TYPE}" \
    --wallet-storage-config "{\"url\":\"${POSTGRESQL_HOST}:5432\",\"max_connections\":5, \"wallet_scheme\":\"${ACAPY_WALLET_SCHEME}\"}" \
    --wallet-storage-creds "{\"account\":\"${POSTGRESQL_USER}\",\"password\":\"${POSTGRESQL_PASSWORD}\",\"admin_account\":\"${POSTGRESQL_USER}\",\"admin_password\":\"${POSTGRESQL_PASSWORD}\"}" \
    --wallet-name traction-wallet  \
    --admin "0.0.0.0" ${ACAPY_ADMIN_PORT} \
    --emit-new-didcomm-prefix \
    --label "${AGENT_NAME}" \
    --jwt-secret "${JWT_SECRET}" \
    ${ACAPY_ADMIN_CONFIG} \
    ${ACAPY_READ_ONLY_MODE} \
    ${ACAPY_TAILS_BASE_URL} \
    ${ACAPY_TAILS_UPLOAD_URL} \
    --endorser-protocol-role author \
    --endorser-public-did ${ACAPY_ENDORSER_PUBLIC_DID} \
    --endorser-alias ${ENDORSER_CONNECTION_ALIAS} \
    --auto-request-endorsement \
    --auto-write-transactions \
    --auto-create-revocation-transactions \
    --notify-revocation \
    --monitor-revocation-notification \
    --plugin traction_plugins.multitenant_provider \
    --plugin-config-value multitenant_provider.manager_class=traction_plugins.multitenant_provider.manager.BasicMultitokenMultitenantManager \
    --plugin traction_plugins.basicmessage_storage.v1_0 \
    --plugin traction_plugins.traction_innkeeper.v1_0 \
