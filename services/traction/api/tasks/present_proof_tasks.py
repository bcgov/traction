import logging
from re import Pattern, compile
from enum import Enum
from ssl import VerifyFlags
from uuid import UUID
from pkg_resources import require

from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError


from api.tasks.tasks import Task, TractionTaskType
from api.db.models import Tenant
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
        vpr = VerifierPresentationRequest.get_by_id(
            payload["v_presentation_request_id"]
        )

        # call acapy
        resp = present_proof_api.present_proof_create_request_post_endpoint()
        values = {"pres_exch_id": resp["txn"]}

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
