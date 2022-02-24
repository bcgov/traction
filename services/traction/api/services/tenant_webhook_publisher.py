import json
import logging
import uuid

from aiohttp import ClientSession
from sqlalchemy import select

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.models import TenantWebhook
from api.db.models.tenant import TenantRead
from api.db.models.tenant_webhook_msg import (
    TenantWebhookMsgCreate,
    TenantWebhookMsgUpdate,
    TenantWebhookMsg,
)
from api.db.repositories.tenant_webhook_msgs import TenantWebhookMsgsRepository
from api.db.repositories.tenants import TenantsRepository
from api.endpoints.models.webhooks import (
    WEBHOOK_LISTENER_PATTERN,
)


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


async def publish_event(
    tenant: TenantRead, webhook: TenantWebhook, profile: Profile, event: Event
):

    _msg_repo = TenantWebhookMsgsRepository(db_session=profile.db)
    in_webhook_msg = TenantWebhookMsgCreate(
        tenant_id=tenant.id,
        msg_id=uuid.uuid4(),
        payload=json.dumps(event.payload),
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


def should_publish_event(webhook: TenantWebhook, event: Event):
    if (
        webhook is None
        or event is None
        or webhook.config is None
        or webhook.config == {}
    ):
        return False

    # ok, is this event type in webhook config?
    if webhook.config["acapy"]:
        return True

    return False


async def handle_tenant_events(profile: Profile, event: Event):
    _t_repo = TenantsRepository(db_session=profile.db)
    tenant = await _t_repo.get_by_wallet_id(profile.wallet_id)
    webhook = await get_tenant_webhook(tenant.id, profile.db)
    # does this tenant have a webhook?
    # and do they want this event?
    if should_publish_event(webhook, event):
        await publish_event(tenant, webhook, profile, event)

    pass


def subscribe_all_events():
    # subscribe to everything
    # we then check the tenant webhook config to see if the event is to be published.
    settings.EVENT_BUS.subscribe(WEBHOOK_LISTENER_PATTERN, handle_tenant_events)
