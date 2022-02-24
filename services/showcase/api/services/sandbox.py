import uuid
from typing import Optional

import pydantic
from fastapi import HTTPException
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.db.errors import DoesNotExist
from api.db.models.out_of_band import OutOfBandCreate
from api.db.models.related import SandboxReadPopulated
from api.db.models.sandbox import (
    SandboxCreate,
    Sandbox,
)
from api.db.models.student import StudentCreate, StudentCreateFactory
from api.db.models.tenant import TenantCreate, Tenant, TenantUpdate
from api.db.repositories import SandboxRepository, StudentRepository, TenantRepository
from api.db.repositories.out_of_band import OutOfBandRepository

from api.services import traction


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


class AcceptInvitationRequest(pydantic.BaseModel):
    sender_id: uuid.UUID
    invitation: dict


class AcceptInvitationResponse(pydantic.BaseModel):
    sender_id: uuid.UUID
    connection_id: uuid.UUID


class TenantWebhookRead(pydantic.BaseModel):
    id: uuid.UUID
    config: dict
    webhook_url: str


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

    # make 5 random students
    rand_students = StudentCreateFactory.batch(5, sandbox_id=sandbox.id)
    for s in rand_students:
        if s.name == "Alice":
            continue
        await student_repo.create(s)

    return await sandbox_repo.get_by_id_populated(sandbox.id)


async def get_sandbox(sandbox_id, db) -> Sandbox:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise DoesNotExist(f"{Sandbox.__name__}<id:{sandbox_id}> does not exist")
    return sandbox


async def get_tenant(sandbox, tenant_id, db):
    # we want data that should not be in TenantRead (private wallet information)
    tenant_q = (
        select(Tenant)
        .where(Tenant.id == tenant_id)
        .where(Tenant.sandbox_id == sandbox.id)
    )
    tenant_rec = await db.execute(tenant_q)
    tenant = tenant_rec.scalars().one_or_none()
    if not tenant:
        raise DoesNotExist(f"{Tenant.__name__}<id:{tenant_id}> does not exist")
    return tenant


async def create_new_tenant(sandbox: Sandbox, repo: TenantRepository, name: str):
    # create tenant in traction, then we use their wallet id and key
    resp = await traction.create_tenant(name=f"{name.lower()}-{str(sandbox.id)[0:7]}")
    traction_tenant = CheckInResponse(**resp)

    # create tenants in db
    new_tenant = TenantCreate(
        name=name.capitalize(),
        wallet_id=traction_tenant.wallet_id,
        wallet_key=traction_tenant.wallet_key,
        webhook_url=traction_tenant.webhook_url,
        sandbox_id=sandbox.id,
    )
    tenant = await repo.create(new_tenant)

    resp = await traction.create_tenant_webhook(tenant)
    read = TenantWebhookRead(**resp)
    upd_tenant = TenantUpdate(
        webhook_url=read.webhook_url,
        id=tenant.id,
        name=tenant.name,
        sandbox_id=tenant.sandbox_id,
    )
    return await repo.update(upd_tenant)


async def create_invitation_for_student(
    sandbox_id: uuid.UUID,
    tenant_id: uuid.UUID,
    payload: InviteStudentRequest,
    db: AsyncSession,
) -> InviteStudentResponse:
    sandbox = await get_sandbox(sandbox_id, db)

    tenant = await get_tenant(sandbox, tenant_id, db)

    # check payload, check student exists
    student_repo = StudentRepository(db_session=db)
    student = await student_repo.get_by_id_in_sandbox(sandbox_id, payload.student_id)

    # do a quick check for existing connection...
    check_resp = await traction.get_connections(
        tenant.wallet_id, tenant.wallet_key, student.name
    )
    if len(check_resp) > 0:
        detail = f"{tenant.name} has an existing connection with {student.name}."
        if check_resp[0]["state"] == "invitation":
            detail = f"{tenant.name} has created and invitation for {student.name}."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    resp = await traction.create_invitation(
        tenant.wallet_id, tenant.wallet_key, student.name
    )

    # bit of a hack here...
    # Student and their Tenant have the same name...
    recipient_q = (
        select(Tenant)
        .where(Tenant.name == student.name)
        .where(Tenant.sandbox_id == sandbox_id)
    )
    recipient_rec = await db.execute(recipient_q)
    recipient_tenant = recipient_rec.scalars().one_or_none()
    if recipient_tenant:
        oob_repo = OutOfBandRepository(db_session=db)
        oob = OutOfBandCreate(
            sandbox_id=sandbox_id,
            sender_id=tenant.id,
            recipient_id=recipient_tenant.id,
            msg_type="Invitation",
            msg=resp["invitation"],
        )
        await oob_repo.create(oob)

    return InviteStudentResponse(
        student_id=student.id,
        connection_id=uuid.UUID(resp["connection_id"]),
        invitation=resp["invitation"],
    )


async def accept_invitation(
    sandbox_id: uuid.UUID,
    tenant_id: uuid.UUID,
    payload: AcceptInvitationRequest,
    db: AsyncSession,
) -> AcceptInvitationResponse:
    sandbox = await get_sandbox(sandbox_id, db)

    recipient = await get_tenant(sandbox, tenant_id, db)

    # for showcase demo, we know the tenant is in our db
    # in the real world, then sender will be completely external
    sender = await get_tenant(sandbox, payload.sender_id, db)

    # do a quick check for existing connection with this alias...
    check_resp = await traction.get_connections(
        recipient.wallet_id, recipient.wallet_key, sender.name
    )
    if len(check_resp) > 0:
        detail = f"{recipient.name} has an existing connection with {sender.name}."
        if check_resp[0]["state"] == "invitation":
            detail = f"{recipient.name} has created and invitation for {sender.name}."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    resp = await traction.accept_invitation(
        recipient.wallet_id, recipient.wallet_key, sender.name, payload.invitation
    )

    # the sender and recipient should start getting webhook updates about
    # changes in connection state...

    return AcceptInvitationResponse(
        sender_id=sender.id,
        connection_id=uuid.UUID(resp["connection_id"]),
    )
