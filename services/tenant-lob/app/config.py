import os

WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "http://localhost:8088/webhook")

# this is the acapy api we call...
PROXY_URL = os.environ.get("SERVER_TRACTION_URL")

# this is so we can automate the innkeeper_store work (approve reservation)
# the flow here would be outside of a line of business application
# this is simply so we can bootstrap some tenants_store/webhooks.
INNKEEPER_TENANT_ID = os.environ.get("TRACTION_INNKEEPER_TENANT_ID")
INNKEEPER_WALLET_KEY = os.environ.get("TRACTION_INNKEEPER_WALLET_KEY")
