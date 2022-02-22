import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from acapy_client.api.multitenancy_api import MultitenancyApi
from acapy_client.model.create_wallet_request import CreateWalletRequest

from api.api_client_utils import get_api_client

from api.core.config import settings
from api.db.errors import AlreadyExists
from api.db.models.tenant import TenantCreate
from api.db.models.tenant_webhook import TenantWebhookCreate
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository
from api.db.repositories.tenants import TenantsRepository
from api.endpoints.models.innkeeper import CheckInRequest, CheckInResponse


# TODO not sure if these should be global or per-request
multitenancy_api = MultitenancyApi(api_client=get_api_client())


async def create_new_tenant(
    payload: CheckInRequest, db: AsyncSession
) -> CheckInResponse:
    _repo = TenantsRepository(db_session=db)
    existing = await _repo.get_by_name(name=payload.name)
    if existing:
        raise AlreadyExists(f"Tenant already exists with name '{existing.name}'")
    else:
        # Call ACAPY
        wallet_key = str(uuid.uuid4())
        wallet_name = str(uuid.uuid4())
        webhook_url = settings.TRACTION_TENANT_WEBHOOK_URL
        if settings.ACAPY_WEBHOOK_URL_API_KEY and 0 < len(
            settings.ACAPY_WEBHOOK_URL_API_KEY
        ):
            webhook_url = f"{webhook_url}#{settings.ACAPY_WEBHOOK_URL_API_KEY}"
        data = {
            "label": payload.name,
            "wallet_key": wallet_key,
            "wallet_name": wallet_name,
            "wallet_type": "indy",
            "wallet_dispatch_type": "default",
            "wallet_webhook_urls": [
                webhook_url,
            ],
        }
        wallet_request = CreateWalletRequest(**data)
        wallet_response = multitenancy_api.multitenancy_wallet_post(
            **{"body": wallet_request}
        )
        if wallet_response:
            # save acapy generated wallet_id
            wallet_id = wallet_response.wallet_id

            in_tenant = TenantCreate(
                **payload.dict(),
                is_active=True,
                wallet_id=wallet_id,
            )
            out_tenant = await _repo.create(in_tenant)
            webhook_url = None

            if payload.webhook_url:
                _wh_repo = TenantWebhooksRepository(db_session=db)
                wh = TenantWebhookCreate(
                    webhook_url=payload.webhook_url, tenant_id=out_tenant.id
                )
                out_wh = await _wh_repo.create(wh)
                webhook_url = out_wh.webhook_url

            return CheckInResponse(
                id=out_tenant.id,
                name=out_tenant.name,
                wallet_id=out_tenant.wallet_id,
                wallet_key=wallet_key,
                webhook_url=webhook_url,
            )
        else:
            # what to return or throw here?
            return
