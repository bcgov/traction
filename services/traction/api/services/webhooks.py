import json
import random
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.tenant_webhook import (
    TenantWebhookCreate,
    TenantWebhookUpdate,
    TenantWebhook,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository


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
        connection_id=payload.get("connection_id"),
        payload=json.dumps(payload),
        state="NEW",
        sequence=1,
    )
    out_webhook = await _wh_repo.create(in_webhook)

    try:
        await call_tenant_lob_app(out_webhook)
        in_upd_webhook = TenantWebhookUpdate(
            id=out_webhook.id,
            state="OK",
            response_code=200,  # TODO
            response="TODO",
        )
        _ = await _wh_repo.update(in_upd_webhook)
    except Exception:
        # log the error and try again later
        in_upd_webhook = TenantWebhookUpdate(
            id=out_webhook.id,
            state="ERROR",
            response_code=500,  # TODO
            response="TODO",
        )
        _ = await _wh_repo.update(in_upd_webhook)
        in_q_webhook = TenantWebhookCreate(
            wallet_id=out_webhook.wallet_id,
            msg_id=out_webhook.msg_id,
            webhook_url=out_webhook.webhook_url,
            connection_id=out_webhook.connection_id,
            payload=out_webhook.payload,
            state="NEW",
            sequence=out_webhook.sequence + 1,
        )
        _ = await _wh_repo.create(in_q_webhook)


async def call_tenant_lob_app(webhook: TenantWebhook):
    # TODO call the webhook url
    if 50 < random.randint(1, 100):
        raise Exception("Fail sometimes!")
    pass
