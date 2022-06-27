import logging

from aiohttp import ClientSession

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.models import Tenant
from api.db.models.v1.tenant_configuration import TenantConfiguration, TenantWebhookLog
from api.db.session import async_session
from api.endpoints.models.webhooks import (
    WEBHOOK_LISTENER_PATTERN,
    TRACTION_EVENT_LISTENER_PATTERN,
)

logger = logging.getLogger(__name__)


async def create_log(
    tenant: Tenant, config: TenantConfiguration, event: Event
) -> TenantWebhookLog:
    logger.info(f"> create_log({tenant.id},{config.webhook_url},{event.topic})")
    async with async_session() as db:
        db_item = TenantWebhookLog(
            tenant_id=tenant.id,
            topic=event.topic,
            payload=event.payload,
            webhook_url=config.webhook_url,
            webhook_key=config.webhook_key,
        )
        db.add(db_item)
        await db.commit()
        result = await db.get(TenantWebhookLog, db_item.tenant_webhook_log_id)
    logger.info(f"< create_log(): {result.tenant_webhook_log_id}")
    return result


async def update_or_delete_log(
    log: TenantWebhookLog, state: str, status: int, detail: str | None
):
    if state == "OK":
        # TODO: discuss... should we delete success or update?
        async with async_session() as db:
            await db.delete(log)
            await db.commit()
    else:
        values = {"http_status": status, "http_error_status_detail": detail}
        await TenantWebhookLog.update_by_id(log.tenant_webhook_log_id, values)


def get_tenant_headers(webhook_api_key: str) -> dict:
    """Return HTTP headers required for tenant lob webhook call."""

    headers = {"accept": "application/json", "Content-Type": "application/json"}
    if webhook_api_key:
        headers["X-API-Key"] = webhook_api_key
    return headers


async def call_tenant_lob_app(configuration: TenantConfiguration, payload: dict):
    logger.info("> call_tenant_lob_app()")
    # call the tenant LOB webhook url

    webhook_url = configuration.webhook_url
    webhook_api_key = configuration.webhook_key

    headers = get_tenant_headers(webhook_api_key)

    async with ClientSession() as client_session:
        logger.debug(f"Calling LOB {webhook_url} with {webhook_api_key} {payload}")
        resp_text = None
        try:
            resp = await client_session.request(
                "POST",
                webhook_url,
                json=payload,
                headers=headers,
            )
            logger.debug("Post-processing LOB request")
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

        logger.info("< call_tenant_lob_app()")
        return (resp_state, resp_status, resp_text)


async def publish_event(tenant: Tenant, config: TenantConfiguration, event: Event):
    logger.info("> publish_event()")
    webhook_log = await create_log(tenant, config, event)
    try:
        (state, status, response) = await call_tenant_lob_app(config, event.payload)
        logger.debug(f"Webhook call returns with: {state} {status} {response}")
    except Exception as e:
        # log the error and try again later...
        # TODO: re-attempt push to webhook
        status = 500
        response = str(e)

    await update_or_delete_log(webhook_log, state, status, response)
    logger.info("< publish_event()")


async def handle_tenant_events(profile: Profile, event: Event):
    async with async_session() as db:
        tenant = await db.get(Tenant, profile.tenant_id)
        config = await TenantConfiguration.get_by_id(db, profile.tenant_id)
    if tenant is not None and config.webhook_key is not None:
        # TODO: check tenant webhook configuration, publish only if they want it
        await publish_event(tenant, config, event)


def subscribe_webhook_events():
    # subscribe to everything
    # we then check the tenant webhook config to see if the event is to be published.
    settings.EVENT_BUS.subscribe(WEBHOOK_LISTENER_PATTERN, handle_tenant_events)
    settings.EVENT_BUS.subscribe(TRACTION_EVENT_LISTENER_PATTERN, handle_tenant_events)
