from aiohttp import ClientSession
import json
import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.tenant_webhook import (
    TenantWebhookCreate,
    TenantWebhookUpdate,
    TenantWebhook,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository


logger = logging.getLogger(__name__)


async def post_tenant_webhook(
    topic: str, payload: dict, wallet_id: uuid.UUID, db: AsyncSession
):
    # save webhook record to the DB
    _t_repo = TenantsRepository(db_session=db)
    tenant = await _t_repo.get_by_wallet_id(wallet_id)
    _wh_repo = TenantWebhooksRepository(db_session=db)
    in_webhook = TenantWebhookCreate(
        wallet_id=wallet_id,
        msg_id=uuid.uuid4(),
        webhook_url=tenant.webhook_url,
        payload=json.dumps(payload),
        state="PROCESSING",
        sequence=1,
    )
    if not tenant.webhook_url or 0 == len(tenant.webhook_url):
        in_webhook.state = "NOT_POSTED"
    out_webhook = await _wh_repo.create(in_webhook)

    if not tenant.webhook_url or 0 == len(tenant.webhook_url):
        return

    in_upd_webhook = TenantWebhookUpdate(
        id=out_webhook.id,
    )
    in_q_webhook = None

    try:
        (state, status, response) = await call_tenant_lob_app(out_webhook)
        logger.warn(f"Webhook call retuens with: {state} {status} {response}")
        in_upd_webhook.state = state
        in_upd_webhook.response_code = status  # TODO
        in_upd_webhook.response = response
    except Exception as e:
        # log the error and try again later
        in_upd_webhook.state = "ERROR"
        in_upd_webhook.response_code = 500  # TODO
        in_upd_webhook.response = str(e)

        # TODO spin up a thread to retry
        in_q_webhook = TenantWebhookCreate(
            wallet_id=out_webhook.wallet_id,
            msg_id=out_webhook.msg_id,
            webhook_url=out_webhook.webhook_url,
            payload=out_webhook.payload,
            state="RETRY",
            sequence=out_webhook.sequence + 1,
        )
    try:
        _ = await _wh_repo.update(in_upd_webhook)
        if in_q_webhook:
            _ = await _wh_repo.create(in_q_webhook)
    except Exception:
        # log the error saying that we can't log the error
        logger.exception("Failed to update webhook status")


def get_tenant_headers(webhook_api_key: str) -> dict:
    """Return HTTP headers required for tenant lob webhook call."""

    headers = {}
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    if webhook_api_key:
        headers["X-API-Key"] = webhook_api_key
    return headers


async def call_tenant_lob_app(webhook: TenantWebhook):
    # call the tenant LOB webhook url

    webhook_parts = webhook.webhook_url.split("#")
    if 1 == len(webhook_parts):
        webhook_url = webhook.webhook_url
        webhook_api_key = None
    else:
        webhook_url = webhook_parts[0]
        webhook_api_key = webhook_parts[1]
    headers = get_tenant_headers(webhook_api_key)

    async with ClientSession() as client_session:
        logger.warn(
            f"Calling LOB {webhook_url} with {webhook_api_key} {webhook.payload}"
        )
        resp_text = None
        try:
            resp = await client_session.request(
                "POST",
                webhook_url,
                json=webhook.payload,
                headers=headers,
            )
            logger.warn("Post-processing LOB request")
            try:
                resp_text = await resp.text()
            except Exception:
                pass
            try:
                resp.raise_for_status()
                resp_status = resp.status
                resp_state = "OK"
            except Exception as e:
                resp_text = str(e)
                resp_status = 500
                resp_state = "ERROR"
        except Exception as e:
            logger.exception("Error calling LOB webhook")
            resp_text = str(e)
            resp_status = 500
            resp_state = "ERROR"

        return (resp_state, resp_status, resp_text)
