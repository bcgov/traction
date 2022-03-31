import uuid
import datetime
from typing import Optional
import json

import pydantic
from fastapi import HTTPException
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from api.db.errors import DoesNotExist
from api.db.models.job_applicant import ApplicantCreate, ApplicantCreateFactory
from api.db.models.out_of_band import OutOfBandCreate
from api.db.models.related import SandboxReadPopulated
from api.db.models.sandbox import (
    SandboxCreate,
    Sandbox,
    Governance,
    SchemaDef,
)
from api.db.models.student import StudentCreate, StudentCreateFactory
from api.db.models.line_of_business import LobCreate, Lob
from api.db.repositories import SandboxRepository, StudentRepository, LobRepository
from api.db.repositories.job_applicant import ApplicantRepository
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


class InviteApplicantRequest(pydantic.BaseModel):
    applicant_id: uuid.UUID


class InviteApplicantResponse(pydantic.BaseModel):
    applicant_id: uuid.UUID
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
    lobs_repo = LobRepository(db_session=db)
    applicant_repo = ApplicantRepository(db_session=db)
    student_repo = StudentRepository(db_session=db)
    if not payload.governance:
        schema_def = SchemaDef(
            name="Education Degree",
            attributes=["student_id", "name", "date", "degree", "age"],
        )
        payload.governance = Governance(
            schema_def=schema_def,
        )

    sandbox = await sandbox_repo.create(payload)

    # create traction tenants for our lobs
    alice = await create_new_line_of_business(sandbox, lobs_repo, "Alice", issuer=False)
    await create_new_line_of_business(sandbox, lobs_repo, "Faber", issuer=True)
    await create_new_line_of_business(sandbox, lobs_repo, "Acme", issuer=False)

    # build data set for this sandbox

    # Alice Smith is our known student at Faber...
    # This degree data will be issued as a credential by Faber to Alice
    student = StudentCreate(
        name="Alice Smith",
        sandbox_id=sandbox.id,
        wallet_id=alice.wallet_id,
        alias=alice.name,
        age=24,
        degree="Maths",
        student_id="AS1234567",
        date=datetime.datetime(2021, 6, 24),
    )
    await student_repo.create(student)

    # The same Alice Smith is going to apply to Acme
    # The degree data will be populated through presentation exchanges
    # between Alice's traction tenant and Acme's traction tenant
    # Acme will update their LOB data after exchange
    applicant = ApplicantCreate(
        name="Alice Smith",
        sandbox_id=sandbox.id,
        wallet_id=alice.wallet_id,
        alias=alice.name,
        degree=None,
        date=None,
    )
    await applicant_repo.create(applicant)

    # make 5 random students
    rand_students = StudentCreateFactory.batch(5, sandbox_id=sandbox.id)
    for s in rand_students:
        if s.name == "Alice Smith":
            continue
        await student_repo.create(s)

    # make 5 random job applicants
    rand_applicants = ApplicantCreateFactory.batch(5, sandbox_id=sandbox.id)
    for s in rand_applicants:
        if s.name == "Alice Smith":
            continue
        await applicant_repo.create(s)

    return await sandbox_repo.get_by_id_populated(sandbox.id)


async def get_sandbox(sandbox_id, db) -> Sandbox:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise DoesNotExist(f"{Sandbox.__name__}<id:{sandbox_id}> does not exist")
    return sandbox


async def get_line_of_business(sandbox, lob_id, db) -> Lob:
    # we want data that should not be in LobRead (private wallet information)
    _q = select(Lob).where(Lob.id == lob_id).where(Lob.sandbox_id == sandbox.id)
    _rec = await db.execute(_q)
    entity = _rec.scalars().one_or_none()
    if not entity:
        raise DoesNotExist(f"{Lob.__name__}<id:{lob_id}> does not exist")
    return entity


async def create_new_line_of_business(
    sandbox: Sandbox, repo: LobRepository, name: str, issuer: bool = False
):
    # create tenant in traction, then we use their wallet id and key
    resp = await traction.create_tenant(name=f"{name.lower()}-{str(sandbox.id)[0:7]}")
    traction_tenant = CheckInResponse(**resp)

    # create our lob in db
    new_lob = LobCreate(
        name=name.capitalize(),
        wallet_id=traction_tenant.wallet_id,
        wallet_key=traction_tenant.wallet_key,
        webhook_url=traction_tenant.webhook_url,
        sandbox_id=sandbox.id,
        traction_issue_enabled=issuer,
    )
    lob = await repo.create(new_lob)

    resp = await traction.create_tenant_webhook(lob)
    read = TenantWebhookRead(**resp)
    lob.webhook_url = read.webhook_url

    if issuer:
        await traction.innkeeper_make_issuer(traction_tenant.id)

    return await repo.update(lob)


async def create_invitation_for_student(
    sandbox_id: uuid.UUID,
    lob_id: uuid.UUID,
    payload: InviteStudentRequest,
    db: AsyncSession,
) -> InviteStudentResponse:
    sandbox = await get_sandbox(sandbox_id, db)

    lob = await get_line_of_business(sandbox, lob_id, db)

    # check payload, check student exists
    student_repo = StudentRepository(db_session=db)
    student = await student_repo.get_by_id_in_sandbox(sandbox_id, payload.student_id)

    if student.connection_id:
        detail = f"{lob.name} has an existing connection with {student.name}."
        if student.invitation_state == "invitation":
            detail = f"{lob.name} has created and invitation for {student.name}."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    # we create an invitation for the student's wallet (traction tenant)
    resp = await traction.create_invitation(
        lob.wallet_id, lob.wallet_key, student.alias
    )

    # bit of a hack here...
    # we've set the student to track their matching traction tenant
    # this is only so we can send an out of band message that they have an invitation
    recipient_q = (
        select(Lob)
        .where(Lob.wallet_id == student.wallet_id)
        .where(Lob.sandbox_id == sandbox_id)
    )
    recipient_rec = await db.execute(recipient_q)
    recipient_lob = recipient_rec.scalars().one_or_none()
    if recipient_lob:
        oob_repo = OutOfBandRepository(db_session=db)
        oob = OutOfBandCreate(
            sandbox_id=sandbox_id,
            sender_id=lob.id,
            recipient_id=recipient_lob.id,
            msg_type="Invitation",
            msg=json.loads(resp["invitation"]),
        )
        await oob_repo.create(oob)

    student.connection_id = uuid.UUID(resp["connection_id"])
    student.invitation_state = "invitation"
    await student_repo.update(student)

    return InviteStudentResponse(
        student_id=student.id,
        connection_id=uuid.UUID(resp["connection_id"]),
        invitation=json.loads(resp["invitation"]),
    )


async def create_invitation_for_applicant(
    sandbox_id: uuid.UUID,
    lob_id: uuid.UUID,
    payload: InviteApplicantRequest,
    db: AsyncSession,
) -> InviteApplicantResponse:
    sandbox = await get_sandbox(sandbox_id, db)

    lob = await get_line_of_business(sandbox, lob_id, db)

    # check payload, check applicant exists
    _repo = ApplicantRepository(db_session=db)
    appl = await _repo.get_by_id_in_sandbox(sandbox_id, payload.applicant_id)

    if appl.connection_id:
        detail = f"{lob.name} has an existing connection with {appl.name}."
        if appl.invitation_state == "invitation":
            detail = f"{lob.name} has created and invitation for {appl.name}."
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

    # we create an invitation for the applicant's wallet (traction tenant)
    resp = await traction.create_invitation(lob.wallet_id, lob.wallet_key, appl.alias)

    # bit of a hack here...
    # we've set the applicant to track their matching traction tenant
    # this is only so we can send an out of band message that they have an invitation
    recipient_q = (
        select(Lob)
        .where(Lob.wallet_id == appl.wallet_id)
        .where(Lob.sandbox_id == sandbox_id)
    )
    recipient_rec = await db.execute(recipient_q)
    recipient_lob = recipient_rec.scalars().one_or_none()
    if recipient_lob:
        oob_repo = OutOfBandRepository(db_session=db)
        oob = OutOfBandCreate(
            sandbox_id=sandbox_id,
            sender_id=lob.id,
            recipient_id=recipient_lob.id,
            msg_type="Invitation",
            msg=json.loads(resp["invitation"]),
        )
        await oob_repo.create(oob)

    appl.connection_id = uuid.UUID(resp["connection_id"])
    appl.invitation_state = "invitation"
    await _repo.update(appl)

    return InviteApplicantResponse(
        applicant_id=appl.id,
        connection_id=uuid.UUID(resp["connection_id"]),
        invitation=json.loads(resp["invitation"]),
    )


async def accept_invitation(
    sandbox_id: uuid.UUID,
    lob_id: uuid.UUID,
    payload: AcceptInvitationRequest,
    db: AsyncSession,
) -> AcceptInvitationResponse:
    sandbox = await get_sandbox(sandbox_id, db)

    recipient = await get_line_of_business(sandbox, lob_id, db)

    # for showcase demo, we know the lob is in our db
    # in the real world, then sender will be completely external
    sender = await get_line_of_business(sandbox, payload.sender_id, db)

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


async def promote_lob_to_issuer(
    sandbox_id: uuid.UUID,
    lob_id: uuid.UUID,
    db: AsyncSession,
):
    sandbox = await get_sandbox(sandbox_id, db)
    lob = await get_line_of_business(sandbox, lob_id, db)

    # have lob register itself as issuer
    await traction.tenant_admin_issuer(lob.wallet_id, lob.wallet_key, {})

    return
