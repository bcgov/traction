import json
import logging
import random
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Lob
from api.db.models.line_of_business import LobUpdate
from api.db.models.out_of_band import OutOfBandCreate
from api.db.repositories import (
    LobRepository,
    SandboxRepository,
    StudentRepository,
    OutOfBandRepository,
)
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
        connection = json.loads(payload["connection"])
        # student should only get an invitation from Faber
        if connection["alias"] == "Faber":
            stu_repo = StudentRepository(db_session=db)
            student = await stu_repo.get_by_alias_in_sandbox(lob.sandbox_id, lob.name)
            student.invitation_state = connection["connection_state"]
            await stu_repo.update(student)

        # applications will get invitation from Acme
        if connection["alias"] == "Acme":
            a_repo = ApplicantRepository(db_session=db)
            appl = await a_repo.get_by_alias_in_sandbox(lob.sandbox_id, lob.name)
            appl.invitation_state = connection["connection_state"]
            await a_repo.update(appl)

    except KeyError:
        logger.warn(f"KeyError: {payload}")
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

        sb_repo = SandboxRepository(db_session=db)
        sb = await sb_repo.get_by_id(lob.sandbox_id)

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
            "schema_name": sb.governance.schema_def.name,
            "schema_version": version,
            "attributes": sb.governance.schema_def.attributes,
        }
        tag = f"degree_{version}"
        await traction.tenant_create_schema(
            wallet_id=lob.wallet_id,
            wallet_key=lob.wallet_key,
            schema=schema,
            cred_def_tag=tag,
        )

        # update governance
        sb.governance.schema_def.version = version
        sb.governance.cred_def_tag = tag
        await sb_repo.update(sb)
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
        cred_def_id = payload["cred_def_id"]
        repo = LobRepository(db_session=db)
        lob.cred_def_id = cred_def_id
        upd = LobUpdate(
            **lob.dict(),
        )
        await repo.update(upd)

        sb_repo = SandboxRepository(db_session=db)
        sb = await sb_repo.get_by_id(lob.sandbox_id)
        sb.governance.schema_def.id = payload["schema_id"]
        sb.governance.cred_def_id = payload["cred_def_id"]
        await sb_repo.update(sb)

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
            # await traction.tenant_send_credential(
            #     wallet_id=lob.wallet_id,
            #     wallet_key=lob.wallet_key,
            #     present_req=present_req,
            # )
            pass

    except KeyError:
        pass
    return True


async def handle_present_proof(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_present_proof({payload})")
    try:
        presentation = payload["presentation"]
        if payload["state"] == "verified" and payload["role"] == "verifier":
            # for now, we know this is verified degree credential
            # just want to update the applicant data...
            a_repo = ApplicantRepository(db_session=db)
            applicant = await a_repo.get_by_alias_in_sandbox(lob.sandbox_id, "Alice")

            requested_proof = presentation["requested_proof"]
            revealed_attrs = requested_proof["revealed_attrs"]
            attr_1 = revealed_attrs["attr_1"]
            attr_2 = revealed_attrs["attr_2"]

            applicant.degree = attr_1["raw"]
            applicant.date = datetime.strptime(attr_2["raw"], "%d-%m-%Y")
            applicant.verified = payload["verified"]
            await a_repo.update(applicant)

            # notify frontend?

    except KeyError:
        pass
    return True


async def handle_credential_revoked(lob: Lob, payload: dict, db: AsyncSession):
    logger.info(f"handle_credential_revoked(lob={lob.name}, payload={payload})")
    try:
        # there are 2 different payloads, one for issuer and one for holder.
        # perhaps we need different topics?
        if "cred_def_id" in payload:
            # this is for the issuer...
            pass
        if "credential" in payload:
            # this is for the holder...
            # use holder lob id for both sender and recipient
            # we just want to surface a message to the holder that a credential
            # has been revoked
            payload["credential"] = json.loads(payload["credential"])
            oob_repo = OutOfBandRepository(db_session=db)
            oob = OutOfBandCreate(
                sandbox_id=lob.sandbox_id,
                sender_id=lob.id,
                recipient_id=lob.id,
                msg_type="Revocation",
                msg=payload,
            )
            await oob_repo.create(oob)

    except KeyError:
        pass

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
    # topic = "connections" is the acapy event, ignore that one
    if "connection" == topic:
        return await handle_connections(lob, payload, db)
    elif "issuer" == topic:
        return await handle_issuer(lob, payload, db)
    elif "schema" == topic:
        return await handle_schema(lob, payload, db)
    # topic = "issue_credential" is the acapy event, ignore that one
    elif "issue_cred" == topic:
        return await handle_issue_credential(lob, payload, db)
    elif "present_req" == topic:
        return await handle_presentation_request(lob, payload, db)
    elif "present_proof" == topic:
        return await handle_present_proof(lob, payload, db)
    elif "issuer_cred_rev" == topic:
        return await handle_credential_revoked(lob, payload, db)
    else:
        logger.warn(f"Ignoring event for topic {topic}")
    return False
