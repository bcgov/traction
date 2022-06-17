from typing import List
import logging
from re import Pattern, compile
from uuid import UUID
from acapy_client.model.indy_proof_req_attr_spec import IndyProofReqAttrSpec
from acapy_client.model.indy_proof_req_pred_spec import IndyProofReqPredSpec
from acapy_client.model.indy_proof_request import IndyProofRequest

from acapy_client.model.v10_presentation_send_request_request import (
    V10PresentationSendRequestRequest,
)


from sqlalchemy import update
from sqlalchemy.exc import DBAPIError


from api.tasks.tasks import (
    Task,
    TractionTaskType,
    TRACTION_TASK_PREFIX,
    TRACTION_SEND_PRESENT_PROOF_REQ_PATTERN,
)
from api.db.models import Tenant
from api.db.models.v1.contact import Contact
from api.endpoints.models.credentials import ProofReqAttr, ProofRequest
from api.endpoints.models.v1.verifier import VerifierPresentationStatusType
from api.db.session import async_session

from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from api.api_client_utils import get_api_client

from api.db.models.v1.verifier_presentation import VerifierPresentation


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

    def _get_db_model_class(self):
        return VerifierPresentation

    def _get_id_from_payload(self, payload):
        spp_t_id = payload["verifier_presentation_id"]
        return spp_t_id

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")

        # update state from pending to 'starting'
        contact = None
        async with async_session() as db:
            contact = await Contact.get_by_id(db, tenant.id, payload["contact_id"])
            vpr = await VerifierPresentation.get_by_id(
                db, tenant.id, self._get_id_from_payload(payload)
            )
            VerifierPresentation.update_by_id(
                vpr.verifier_presentation_id,
                values={"status": VerifierPresentationStatusType.STARTING},
            )

        data = {
            "body": V10PresentationSendRequestRequest(
                connection_id=str(contact.connection_id),
                proof_request=convert_to_IndyProofRequest(payload["proof_request"]),
            )
        }

        resp = present_proof_api.present_proof_send_request_post(**data)
        values = {"pres_exch_id": resp["presentation_exchange_id"]}

        VerifierPresentation.update_by_id(
            self._get_id_from_payload(self, payload), values=values
        )

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
            f"contact_id = {payload['contact_id']}, payload = {payload['proof_request']}"  # noqa: E501
        )

        # weak validation of payload
        required_payload_keys = [
            "verifier_presentation_id",
            "contact_id",
            "proof_request",
        ]

        payload_keys = payload.keys()
        if not all(req_key in payload_keys for req_key in required_payload_keys):
            raise Exception(
                f"Invalid payload, {cls.__name__}.assign expects payload with keys={required_payload_keys}"  # noqa: E501
            )

        await cls._assign(tenant_id, wallet_id, payload)
        pass


def convert_to_IndyProofRequest(proof_request: ProofRequest):
    logger.warning(proof_request)

    conv_request_preds = {
        a.name: IndyProofReqPredSpec(**a.__dict__)
        for a in proof_request.requested_predicates
    }
    conv_request_attrs = _convert_to_IndyProofReqAttrSpec(
        proof_request.requested_attributes
    )
    openapi_proof_request = IndyProofRequest(
        requested_attributes=conv_request_attrs,
        requested_predicates=conv_request_preds,
        name="TBD, will be passed later",
        version="1.0.0",
        non_revoked={},
    )

    return openapi_proof_request


def _convert_to_IndyProofReqAttrSpec(attrs: List[ProofReqAttr]):
    conv_request_attrs = {}
    for i, a in enumerate(attrs):
        attr = IndyProofReqAttrSpec()
        if a.name:
            attr.name = a.name
        if a.names:
            attr.names = a.names
        if a.non_revoked:
            attr.non_revoked = a.non_revoked
        if a.restrictions:
            attr.restrictions = a.restrictions

        conv_request_attrs["attr_" + str(i)] = attr

    return conv_request_attrs
