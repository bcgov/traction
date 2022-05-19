import uuid
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from acapy_client.api.multitenancy_api import MultitenancyApi
from acapy_client.model.create_wallet_request import CreateWalletRequest

from api.api_client_utils import get_api_client

from api.core.config import settings
from api.db.errors import AlreadyExists
from api.db.models.tenant import Tenant, TenantCreate, TenantRead
from api.db.repositories.tenants import TenantsRepository
from api.endpoints.models.innkeeper import CheckInRequest, CheckInResponse


# TODO not sure if these should be global or per-request
multitenancy_api = MultitenancyApi(api_client=get_api_client())
logger = logging.getLogger(__name__)


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

            return CheckInResponse(
                id=out_tenant.id,
                name=out_tenant.name,
                wallet_id=out_tenant.wallet_id,
                wallet_key=wallet_key,
            )
        else:
            # what to return or throw here?
            return


async def hard_delete_tenant(tenant: TenantRead, db: AsyncSession):
    q = select(Tenant).where(Tenant.id == tenant.id)
    result = await db.execute(q)
    db_tenant = result.scalar_one()
    if not tenant:
        raise Exception

    response = multitenancy_api.multitenancy_wallet_wallet_id_remove_post(
        str(tenant.wallet_id)
    )
    logger.warn(f"wallet_id = {tenant.wallet_id} has been hard deleted")

    await db.delete(db_tenant)
    await db.commit()
    return response
