import urllib
import uuid
from typing import Optional

import pydantic
from aiohttp import ClientSession
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.core.config import settings
from api.db.errors import DoesNotExist
from api.db.models.related import SandboxReadPopulated
from api.db.models.sandbox import (
    SandboxCreate,
    Sandbox,
)
from api.db.models.student import StudentCreate
from api.db.models.tenant import TenantCreate, Tenant
from api.db.repositories import SandboxRepository, StudentRepository, TenantRepository
from api.services import traction_urls as t_urls


class CheckInResponse(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID
    webhook_url: Optional[str] = None


class InviteStudentRequest(pydantic.BaseModel):
    student_id: uuid.UUID


class InviteStudentResponse(pydantic.BaseModel):
    student_id: uuid.UUID
    connection_id: uuid.UUID
    invitation: dict


async def get_auth_headers(
    wallet_id: Optional[uuid.UUID] = None, wallet_key: Optional[uuid.UUID] = None
):
    username = str(wallet_id) if wallet_id else settings.TRACTION_API_ADMIN_USER
    password = str(wallet_key) if wallet_key else settings.TRACTION_API_ADMIN_KEY
    token_url = t_urls.TENANT_TOKEN if wallet_id else t_urls.INNKEEPER_TOKEN

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "username": username,
        "password": password,
        "grant_type": "",
        "scope": "",
    }

    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=token_url,
            data=data,
            headers=headers,
        ) as response:
            resp = await response.json()
            token = resp["access_token"]
            return {
                "accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            }


async def create_traction_tenant(name: str) -> CheckInResponse:
    auth_headers = await get_auth_headers()
    # name and webhook_url
    data = {
        "name": name,
        "webhook_url": f"{settings.SHOWCASE_ENDPOINT}/api/v1/webhook",
    }
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=t_urls.INNKEEPER_CHECKIN,
            json=data,
            headers=auth_headers,
        ) as response:
            resp = await response.json()
            return CheckInResponse(**resp)


async def create_new_sandbox(
    payload: SandboxCreate, db: AsyncSession
) -> SandboxReadPopulated:
    # create a sandbox
    sandbox_repo = SandboxRepository(db_session=db)
    tenants_repo = TenantRepository(db_session=db)
    student_repo = StudentRepository(db_session=db)
    sandbox = await sandbox_repo.create(payload)

    # create tenants
    await create_new_tenant(sandbox, tenants_repo, "Alice")
    await create_new_tenant(sandbox, tenants_repo, "Faber")
    await create_new_tenant(sandbox, tenants_repo, "Acme")

    # build data set for this sandbox
    student = StudentCreate(
        name="Alice",
        sandbox_id=sandbox.id,
    )
    await student_repo.create(student)

    return await sandbox_repo.get_by_id_populated(sandbox.id)


async def create_new_tenant(sandbox: Sandbox, repo: TenantRepository, name: str):
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
    return await repo.create(tenant)


async def create_invitation_for_student(
    sandbox_id: uuid.UUID,
    tenant_id: uuid.UUID,
    payload: InviteStudentRequest,
    db: AsyncSession,
) -> InviteStudentResponse:

    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise DoesNotExist(f"{Tenant.__name__}<id:{tenant_id}> does not exist")

    # we want data that should not be in TenantRead (private wallet information)
    tenant_q = (
        select(Tenant)
        .where(Tenant.id == tenant_id)
        .where(Tenant.sandbox_id == sandbox_id)
    )
    tenant_rec = await db.execute(tenant_q)
    tenant = tenant_rec.scalars().one_or_none()
    if not tenant:
        raise DoesNotExist(f"{Tenant.__name__}<id:{tenant_id}> does not exist")

    # check payload, check student exists
    student_repo = StudentRepository(db_session=db)
    student = await student_repo.get_by_id_in_sandbox(sandbox_id, payload.student_id)

    # call Traction to create an invitation...
    auth_headers = await get_auth_headers(
        wallet_id=tenant.wallet_id, wallet_key=tenant.wallet_key
    )
    # no body...
    data = {}
    query_params = urllib.parse.urlencode(
        {"alias": student.name, "invitation_type": "didexchange/1.0"}
    )
    url = f"{t_urls.TENANT_CREATE_INVITATION}?{query_params}"
    # TODO: error handling calling Traction
    async with ClientSession() as client_session:
        async with await client_session.post(
            url=url,
            json=data,
            headers=auth_headers,
        ) as response:
            resp = await response.json()
            return InviteStudentResponse(
                student_id=student.id,
                connection_id=uuid.UUID(resp["connection_id"]),
                invitation=resp["invitation"],
            )
