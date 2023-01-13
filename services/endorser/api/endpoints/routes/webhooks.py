from enum import Enum
import logging

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from starlette.status import HTTP_403_FORBIDDEN

from api.core.config import settings
import api.acapy_utils as au


logger = logging.getLogger(__name__)

router = APIRouter()

api_key_header = APIKeyHeader(
    name=settings.ACAPY_WEBHOOK_URL_API_KEY_NAME, auto_error=False
)


class WebhookTopicType(str, Enum):
    ping = "ping"
    connections = "connections"
    oob_invitation = "oob-invitation"
    connection_reuse = "connection-reuse"
    connection_reuse_accepted = "connection-reuse-accepted"
    basicmessages = "basicmessages"
    issue_credential = "issue-credential"
    issue_credential_v2_0 = "issue-credential-v2-0"
    issue_credential_v2_0_indy = "issue-credential-v2-0-indy"
    issue_credential_v2_0_ld_proof = "issue-credential-v2-0-ld-proof"
    issuer_cred_rev = "issuer-cred-rev"
    present_proof = "present-proof"
    present_proof_v2_0 = "present-proof-v2-0"
    endorse_transaction = "endorse_transaction"
    revocation_registry = "revocation-registry"
    revocation_notification = "revocation-notification"
    problem_report = "problem-report"


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    if api_key_header == settings.ACAPY_WEBHOOK_URL_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


def get_webhookapp() -> FastAPI:
    application = FastAPI(
        title="WebHooks",
        description="Endpoints for Aca-Py WebHooks",
        debug=settings.DEBUG,
        middleware=None,
    )
    application.include_router(router, prefix="")
    return application


@router.post("/topic/{topic}/", response_model=dict)
async def process_webhook(
    topic: WebhookTopicType, payload: dict, api_key: APIKey = Depends(get_api_key)
):
    """Called by aca-py agent."""
    state = payload.get("state")
    logger.info(f">>> Called webhook for endorser: {topic}/{state}")
    if topic == "connections":
        await setup_endorser_connection(payload)
    return {}


async def setup_endorser_connection(payload: dict):
    """Set endorser role on any connections we receive."""
    # TODO check final state for other connections protocols
    if (
        payload["state"] == "completed"
        and payload["connection_protocol"] == "didexchange/1.0"
    ):
        # confirm if we have already set the role on this connection
        connection_id = payload["connection_id"]
        conn_meta_data = await au.acapy_GET(f"connections/{connection_id}/metadata")
        logger.info(
            f">>> check for metadata on connection: {connection_id}: {conn_meta_data}"
        )
        if "transaction-jobs" in conn_meta_data["results"]:
            if "transaction_my_job" in conn_meta_data["results"]["transaction-jobs"]:
                return

        # set our endorser role
        logger.info(f">>> Setting meta-data for connection: {payload}")
        params = {"transaction_my_job": "TRANSACTION_ENDORSER"}
        await au.acapy_POST(
            f"transactions/{connection_id}/set-endorser-role", params=params
        )
        conn_meta_data = await au.acapy_GET(f"connections/{connection_id}/metadata")
        logger.info(
            f">>> re-check for metadata on connection: {connection_id}:{conn_meta_data}"
        )
