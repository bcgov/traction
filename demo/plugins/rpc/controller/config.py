import os
from dotenv import load_dotenv

load_dotenv()

PROXY_URL = os.environ.get("PROXY_URL")

INNKEEPER_TENANT_ID = os.environ.get("INNKEEPER_TENANT_ID")
INNKEEPER_WALLET_KEY = os.environ.get("INNKEEPER_WALLET_KEY")

AGENT_PORT = os.environ.get("AGENT_PORT")
