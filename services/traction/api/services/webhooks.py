from aiohttp import ClientSession
import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.errors import DoesNotExist
from api.db.models import TenantWebhook
from api.db.models.tenant_webhook_msg import (
    TenantWebhookMsgCreate,
    TenantWebhookMsgUpdate,
    TenantWebhookMsg,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_webhook_msgs import TenantWebhookMsgsRepository


logger = logging.getLogger(__name__)


async def get_tenant_webhook(tenant_id, db):
    # we want data that should not be in TenantWebhookRead
    # (private wallet key information)
    _q = select(TenantWebhook).where(TenantWebhook.tenant_id == tenant_id)
    _rec = await db.execute(_q)
    item = _rec.scalars().one_or_none()
    if not item:
        raise DoesNotExist(
            f"{TenantWebhook.__name__}<tenant_id:{tenant_id}> does not exist"
        )
    return item


async def post_tenant_webhook(
    topic: str, payload: dict, wallet_id: uuid.UUID, db: AsyncSession
):
    # save webhook record to the DB
    _t_repo = TenantsRepository(db_session=db)
    tenant = await _t_repo.get_by_wallet_id(wallet_id)

    webhook = await get_tenant_webhook(tenant.id, db)

    _msg_repo = TenantWebhookMsgsRepository(db_session=db)
    in_webhook_msg = TenantWebhookMsgCreate(
        tenant_id=tenant.id,
        msg_id=uuid.uuid4(),
        payload=json.dumps(payload),
        state="PROCESSING",
        sequence=1,
    )
    if not webhook:
        in_webhook_msg.state = "NOT_POSTED"
    out_webhook_msg = await _msg_repo.create(in_webhook_msg)

    if not webhook:
        return

    in_upd_webhook = TenantWebhookMsgUpdate(
        id=out_webhook_msg.id,
    )
    in_q_webhook = None

    try:
        (state, status, response) = await call_tenant_lob_app(out_webhook_msg, webhook)
        logger.warn(f"Webhook call returns with: {state} {status} {response}")
        in_upd_webhook.state = state
        in_upd_webhook.response_code = status  # TODO
        in_upd_webhook.response = response
    except Exception as e:
        # log the error and try again later
        in_upd_webhook.state = "ERROR"
        in_upd_webhook.response_code = 500  # TODO
        in_upd_webhook.response = str(e)

        # TODO spin up a thread to retry
        in_q_webhook = TenantWebhookMsgCreate(
            tenant_id=tenant.id,
            msg_id=out_webhook_msg.msg_id,
            payload=out_webhook_msg.payload,
            state="RETRY",
            sequence=out_webhook_msg.sequence + 1,
        )
    try:
        _ = await _msg_repo.update(in_upd_webhook)
        if in_q_webhook:
            _ = await _msg_repo.create(in_q_webhook)
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


async def call_tenant_lob_app(webhook_msg: TenantWebhookMsg, webhook: TenantWebhook):
    # call the tenant LOB webhook url

    webhook_url = webhook.webhook_url
    webhook_api_key = webhook.webhook_key

    headers = get_tenant_headers(webhook_api_key)

    async with ClientSession() as client_session:
        logger.warn(
            f"Calling LOB {webhook_url} with {webhook_api_key} {webhook_msg.payload}"
        )
        resp_text = None
        try:
            resp = await client_session.request(
                "POST",
                webhook_url,
                json=webhook_msg.payload,
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
