import uuid
from typing import Optional

import pydantic
from aiohttp import ClientSession
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.config import settings
from api.db.models.sandbox import (
    SandboxCreate,
    SandboxReadWithTenants,
    Sandbox,
    TenantCreate,
)
from api.db.repositories.sandboxes import SandboxesRepository
from api.db.repositories.tenants import TenantsRepository


class CheckInResponse(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID
    webhook_url: Optional[str] = None


async def get_token():
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": settings.TRACTION_API_ADMIN_USER,
        "password": settings.TRACTION_API_ADMIN_KEY,
        "grant_type": "",
        "scope": "",
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=f"{settings.TRACTION_ENDPOINT}/innkeeper/token",
            data=data,
            headers=headers,
        ) as response:
            resp = await response.json()
            return resp["access_token"]


async def create_traction_tenant(name: str) -> CheckInResponse:
    token = await get_token()
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    # name and webhook_url
    data = {
        "name": name,
        "webhook_url": f"{settings.SHOWCASE_ENDPOINT}/webhook",
    }
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=f"{settings.TRACTION_ENDPOINT}/innkeeper/v1/check-in",
            json=data,
            headers=headers,
        ) as response:
            resp = await response.json()
            return CheckInResponse(**resp)


async def create_new_sandbox(
    payload: SandboxCreate, db: AsyncSession
) -> SandboxReadWithTenants:
    # create a sandbox
    sandbox_repo = SandboxesRepository(db_session=db)
    tenants_repo = TenantsRepository(db_session=db)
    sandbox = await sandbox_repo.create(payload)

    # create tenants
    await create_new_tenant(sandbox, tenants_repo, "Alice")
    await create_new_tenant(sandbox, tenants_repo, "Faber")
    await create_new_tenant(sandbox, tenants_repo, "Acme")

    return await sandbox_repo.get_by_id(sandbox.id)


async def create_new_tenant(sandbox: Sandbox, repo: TenantsRepository, name: str):
    # create tenant in traction, then we use their wallet id and key
    traction_tenant = await create_traction_tenant(
        f"{name.lower()}-{str(sandbox.id)[0:7]}"
    )
    # create tenants in db
    tenant = TenantCreate(
        name=name.capitalize(),
        wallet_id=traction_tenant.wallet_id,
        wallet_key=traction_tenant.wallet_key,
        webhook_url=traction_tenant.webhook_url,
        sandbox_id=sandbox.id,
    )
    await repo.create(tenant)
