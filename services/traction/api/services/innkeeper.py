import uuid
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.db.errors import AlreadyExists
from api.db.models.tenant import TenantCreate
from api.db.repositories.tenants import TenantsRepository
from api.endpoints.models.innkeeper import CheckInRequest, CheckInResponse
from api import acapy_utils as au


async def create_new_tenant(
    payload: CheckInRequest, db: AsyncSession
) -> CheckInResponse:
    _repo = TenantsRepository(db_session=db)
    existing = await _repo.get_by_name(name=payload.name)
    if existing:
        raise AlreadyExists(f"Tenant already exists with name '{existing.name}'")
    else:
        # Call ACAPY
        url = f"{settings.ACAPY_ADMIN_URL}/multitenancy/wallet"
        wallet_key = str(uuid.uuid4())
        wallet_name = str(uuid.uuid4())
        data = {
            "label": payload.name,
            "wallet_key": wallet_key,
            "wallet_name": wallet_name,
            "wallet_type": "indy",
            "wallet_dispatch_type": "both",
            "wallet_webhook_urls": [settings.TRACTION_TENANT_WEBHOOK_URL,],
        }
        response = requests.post(url=url, headers=au.get_acapy_headers(), json=data)
        if response.ok:
            r_json = response.json()
            # save acapy generated wallet_id
            wallet_id = r_json["wallet_id"]

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
