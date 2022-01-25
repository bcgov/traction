import uuid
import requests
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.db.errors import AlreadyExists
from api.db.repositories.access_keys import AccessKeysRepository
from api.db.repositories.tenants import TenantsRepository
from api.models.schema.access_keys import InAccessKeySchema
from api.models.schema.tenants import (
    RequestCheckInSchema,
    ResponseCheckInSchema,
    InTenantSchema,
)
from api import acapy_utils as au
from api.password_utils import hash_password


async def create_new_tenant(
    payload: RequestCheckInSchema, db: AsyncSession
) -> ResponseCheckInSchema:
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
        }
        response = requests.post(url=url, headers=au.get_acapy_headers(), json=data)
        if response.ok:
            r_json = response.json()
            # save acapy generated wallet_id
            wallet_id = r_json["wallet_id"]

            # need a transaction here, and if fails should delete wallet from acapy
            in_tenant = InTenantSchema(
                **payload.dict(),
                is_active=True,
                wallet_id=wallet_id,
                wallet_key=wallet_key,
            )
            out_tenant = await _repo.create(in_tenant)

            tenant_api_key = str(uuid.uuid4())
            ak_repo = AccessKeysRepository(db_session=db)
            in_ak = InAccessKeySchema(
                tenant_id=out_tenant.id,
                password=hash_password(tenant_api_key),
                is_admin=False,
                is_active=True,
            )

            await ak_repo.create(in_ak)

            return ResponseCheckInSchema(
                id=out_tenant.id,
                name=out_tenant.name,
                wallet_id=wallet_id,
                wallet_name=wallet_name,
                wallet_key=wallet_key,
                tenant_api_key=tenant_api_key,
            )
        else:
            # what to return or throw here?
            return
