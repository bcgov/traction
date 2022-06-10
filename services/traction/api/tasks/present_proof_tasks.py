import logging
from re import Pattern, compile
from enum import Enum
from ssl import VerifyFlags
from uuid import UUID
from acapy_client.model.indy_proof_req_attr_spec import IndyProofReqAttrSpec
from acapy_client.model.indy_proof_req_pred_spec import IndyProofReqPredSpec
from acapy_client.model.indy_proof_request import IndyProofRequest

from acapy_client.model.v10_presentation_create_request_request import (
    V10PresentationCreateRequestRequest,
)
from acapy_client.model.v10_presentation_send_request_request import (
    V10PresentationSendRequestRequest,
)

from pkg_resources import require
from requests import request

from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError


from api.tasks.tasks import Task, TractionTaskType
from api.db.models import Tenant
from api.db.models.v1.contact import Contact
from api.endpoints.models.credentials import ProofRequest
from api.db.session import async_session

from acapy_client.api.issue_credential_v1_0_api import IssueCredentialV10Api
from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from api.api_client_utils import get_api_client

from api.db.models.v1.presentation_requests import VerifierPresentationRequest

TRACTION_TASK_PREFIX = "traction::TASK::"


TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN = compile(
    f"^{TRACTION_TASK_PREFIX}{TractionTaskType.send_present_proof_req}(.*)?$"
)

present_proof_api = PresentProofV10Api(api_client=get_api_client())

logger = logging.getLogger(__name__)


def get_logger(cls):
    return logging.getLogger(cls.__name__)


class SendPresentProofTask(Task):
    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.send_present_proof_req

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")

        # update state from pending to 'starting'
        # vpr =
        # call acapy
        contact = None
        async with async_session() as db:
            contact = await Contact.get_by_id(db, tenant.id, payload["contact_id"])
            vpr = await VerifierPresentationRequest.get_by_id(
                db, tenant.id, payload["v_presentation_request_id"]
            )
            vpr.status = "starting"
            db.add(vpr)
            await db.commit()

        data = {
            "body": V10PresentationSendRequestRequest(
                connection_id=str(contact.connection_id),
                proof_request=convert_to_IndyProofRequest(payload["proof_request"]),
            )
        }

        resp = present_proof_api.present_proof_send_request_post(**data)
        self.logger.warn(resp)
        values = {"pres_exch_id": resp["presentation_exchange_id"]}

        q = (
            update(VerifierPresentationRequest)
            .where(
                VerifierPresentationRequest.v_presentation_request_id
                == payload["v_presentation_request_id"]
            )
            .values(values)
        )
        async with async_session() as db:
            try:
                await db.execute(q)
            except DBAPIError:
                await db.rollback()
                self.logger.error(exc_info=1)
            else:
                await db.commit()
        pass

    @classmethod
    async def assign(
        cls,
        tenant_id: UUID,
        wallet_id: UUID,
        payload: dict,
    ):
        get_logger(cls).info("> _assign()")
        get_logger(cls).debug(f"tenant_id = {tenant_id}")
        get_logger(cls).debug(f"wallet_id = {wallet_id}")
        get_logger(cls).debug(
            f"contact_id = {payload['contact_id']}, payload = {payload['proof_request']}"
        )

        # weak validation of payload
        required_payload_keys = [
            "v_presentation_request_id",
            "contact_id",
            "proof_request",
        ]

        payload_keys = payload.keys()
        if not all(req_key in payload_keys for req_key in required_payload_keys):
            raise Exception(
                f"Invalid payload, {cls.__name__}.assign expects payload with keys={required_payload_keys}"
            )

        await cls._assign(tenant_id, wallet_id, payload)
        pass


def convert_to_IndyProofRequest(proof_request: ProofRequest):
    logger.warning(proof_request)

    conv_request_attrs = {
        a.name: IndyProofReqAttrSpec(
            name=a.name,
            # names=a.names,
            non_revoked=a.non_revoked,
            restrictions=a.restrictions,
            _check_type=False,
        )
        for a in proof_request.requested_attributes
    }

    conv_request_preds = {
        a.name: IndyProofReqPredSpec(**a.__dict__)
        for a in proof_request.requested_predicates
    }

    logger.warning(conv_request_attrs)
    openapi_proof_request = IndyProofRequest(
        requested_attributes=conv_request_attrs, requested_predicates=conv_request_preds
    )

    logger.warning(openapi_proof_request)

    return openapi_proof_request
