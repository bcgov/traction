import json
import logging
import random

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Lob
from api.db.models.line_of_business import LobUpdate
from api.db.repositories import LobRepository, StudentRepository
from api.db.repositories.job_applicant import ApplicantRepository
from api.services.websockets import notifier
from api.services import traction

logger = logging.getLogger(__name__)


async def handle_connections(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_connections({payload})")

    # if we are handling a connection on behalf of a student or
    #   applicant (ie they accepted)
    # we want to track the state of the invitation.
    try:
        if payload["invitation_key"] and payload["invitation_msg_id"]:
            # student should only get an invitation from Faber
            if payload["alias"] == "Faber":
                stu_repo = StudentRepository(db_session=db)
                student = await stu_repo.get_by_alias_in_sandbox(
                    lob.sandbox_id, lob.name
                )
                student.invitation_state = payload["state"]
                await stu_repo.update(student)

            # applications will get invitation from Acme
            if payload["alias"] == "Acme":
                a_repo = ApplicantRepository(db_session=db)
                appl = await a_repo.get_by_alias_in_sandbox(lob.sandbox_id, lob.name)
                appl.invitation_state = payload["state"]
                await a_repo.update(appl)

    except KeyError:
        pass

    return True


async def handle_issuer(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_issuer({payload})")
    # {
    # 'status': 'completed',
    # 'public_did': 'MS614YmscauME1eqjFCioa',
    # 'public_did_state': 'public'
    # }
    if payload["status"] == "completed" and payload["public_did_state"] == "public":
        repo = LobRepository(db_session=db)
        lob.public_did = payload["public_did"]
        upd = LobUpdate(**lob.dict())
        await repo.update(upd)

        # TODO: remove this, only for one-time demo
        # now that we are an issuer, let's create a schema/creddefn
        version = format(
            "%d.%d.%d"
            % (
                random.randint(1, 101),
                random.randint(1, 101),
                random.randint(1, 101),
            )
        )
        schema = {
            "schema_name": "degree schema",
            "schema_version": version,
            "attributes": ["student_id", "name", "date", "degree", "age"],
        }
        tag = f"degree_{version}"
        resp = await traction.tenant_create_schema(
            wallet_id=lob.wallet_id,
            wallet_key=lob.wallet_key,
            schema=schema,
            cred_def_tag=tag,
        )
        logger.info(f"create schema/cred def resp={resp}")
    return True


async def handle_schema(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_schema({payload})")
    # {
    # 'status': 'completed',
    # 'schema_id': 'MS614YmscauME1eqjFCioa:2:sherman_002:0.0.2',
    # 'cred_def_id': 'MS614YmscauME1eqjFCioa:3:CL:160656:demo_002',
    # 'cred_def_state': 'completed',
    # 'cred_def_tag': 'demo_002'
    # }
    if payload["status"] == "completed" and payload["cred_def_state"] == "completed":
        repo = LobRepository(db_session=db)
        lob.cred_def_id = payload["cred_def_id"]
        upd = LobUpdate(
            **lob.dict(),
        )
        await repo.update(upd)

    return True


async def handle_issue_credential(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_issue_credential({payload})")
    # await traction.tenant_accept_cred_offer(
    #     wallet_id=lob.wallet_id,
    #     wallet_key=lob.wallet_key,
    #     cred_issue_id=payload["cred_issue_id"],
    # )

    return True


async def handle_presentation_request(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_presentation_request({payload})")
    try:
        present_req = json.loads(payload["present_req"])
        if (
            payload["status"] == "request_received"
            and present_req["present_role"] == "holder"
        ):
            # for now, we are just going to find the credential and respond
            # it should notify alice that her credential has been requested
            # and how to proceed.
            await traction.tenant_send_credential(
                wallet_id=lob.wallet_id,
                wallet_key=lob.wallet_key,
                present_req=present_req,
            )
        if present_req["present_role"] == "verifier":
            logger.info(f"!!!!! verifier({payload['status']})")

    except KeyError:
        pass
    return True


async def handle_present_proof(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_present_proof({payload})")
    return True


async def handle_webhook(lob: Lob, topic: str, payload: dict, db: AsyncSession):
    logger.info(f"handle_webhook(lob = {lob.name}, topic = {topic})")
    # TODO - make proper notifications to FE that are useful...
    await notifier.push(
        {
            "topic": topic,
            "payload": payload,
            "lob": {
                "sandbox_id": str(lob.sandbox_id),
                "id": str(lob.id),
                "name": lob.name,
            },
        }
    )
    if "connections" == topic:
        return await handle_connections(lob, payload, db)
    if "issuer" == topic:
        return await handle_issuer(lob, payload, db)
    if "schema" == topic:
        return await handle_schema(lob, payload, db)
    # topic = "issue_credential" is the acapy event, ignore that one
    if "issue_cred" == topic:
        return await handle_issue_credential(lob, payload, db)
    if "present_req" == topic:
        return await handle_presentation_request(lob, payload, db)
    if "present_proof" == topic:
        return await handle_present_proof(lob, payload, db)
    return False
