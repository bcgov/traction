from uuid import UUID
import requests
import logging
from re import Pattern

from acapy_client.api.ledger_api import LedgerApi
from acapy_client.api.wallet_api import WalletApi
from acapy_client.model.did_create import DIDCreate
from api.api_client_utils import get_api_client
from api.core.config import settings
from api.db.models import Tenant

from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.tenant_issuer import PublicDIDStateType

from api.db.models.v1.tenant import Tenant2
from api.db.models.v1.tenant_issuer import TenantIssuer
from api.db.session import async_session
from api.db.models.v1.contact import Contact


from api.tasks.tasks import (
    Task,
    TractionTaskType,
    TRACTION_TASK_PREFIX,
    TRACTION_REGISTER_PUBLIC_DID_PATTERN,
)

# from api.services.IssuerWorkflow import IssuerWorkflow

ledger_api = LedgerApi(api_client=get_api_client())
wallet_api = WalletApi(api_client=get_api_client())


def get_logger(cls):
    return logging.getLogger(cls.__name__)


class RegisterPublicDIDTask(Task):
    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_REGISTER_PUBLIC_DID_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.register_public_did

    def _get_db_model_class(self):
        return TenantIssuer

    def _get_id_from_payload(self, payload):
        self.logger.info(f"> _get_id_from_payload ->> {payload.keys()}")
        rpd_t_id = payload["tenant_id"]
        return rpd_t_id

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")
        self.initiate_public_did(tenant)

    @classmethod
    async def assign(
        cls,
        tenant_id: UUID,
        wallet_id: UUID,
        payload: dict,
    ):
        # weak validation of payload
        # required_payload_keys = [
        #     "verifier_presentation_id",
        #     "contact_id",
        #     "proof_request",
        # ]

        # payload_keys = payload.keys()
        # if not all(req_key in payload_keys for req_key in required_payload_keys):
        #     raise Exception(
        #         f"Invalid payload, {cls.__name__}.assign expects payload with keys={required_payload_keys}"  # noqa: E501
        #     )

        await cls._assign(tenant_id, wallet_id, payload)
        pass

    async def initiate_public_did(self, tenant: Tenant) -> None:
        self.logger.warn("> initiate_public_did:")

        # onto the next phase!  create our DID and make it public
        (tenant_issuer, did_result) = await self.create_local_did(tenant_issuer)

        # post to the ledger (this will be an endorser operation)
        # (just ignore the response for now)
        try:
            tenant_issuer = await self.initiate_public_did_workflow(
                tenant_issuer, did_result
            )
        except Exception:
            # TODO this is a hack (for now) - aca-py 0.7.3 doesn't
            # supportthe endorser protocol for this transaction, it
            # will be in the next release (0.7.4 or whatever)
            tenant_issuer = await self.create_public_did(tenant_issuer, did_result)
        return

    async def create_public_did(self, tenant: Tenant, did_result: dict) -> None:
        self.logger.warn("calling > create_public_did:")

        genesis_url = settings.ACAPY_GENESIS_URL
        did_registration_url = genesis_url.replace("genesis", "register")
        data = {
            "did": did_result.result.did,
            "verkey": did_result.result.verkey,
            "alias": str(tenant.tenant_id),
        }
        requests.post(did_registration_url, json=data)

        # now make it public
        did_result = wallet_api.wallet_did_public_post(did_result.result.did)

        TenantIssuer.update_by_id(
            tenant.tenant_id,
            {
                "public_did_state": PublicDIDStateType.public,
            },
        )
        return

    async def initiate_public_did_workflow(
        self, tenant: Tenant, did_result: dict
    ) -> None:
        self.logger.warn("calling > initiate_public_did_workflow:")
        data = {"alias": tenant.tenant_id}
        ledger_api.ledger_register_nym_post(
            did_result.result.did,
            did_result.result.verkey,
            **data,
        )
        TenantIssuer.update_by_id(
            tenant.id,
            {
                "public_did_state": PublicDIDStateType.requested,
            },
        )
        return

    async def create_local_did(self, tenant: Tenant) -> (dict):
        self.logger.warn("calling > create_local_did:")

        data = {"body": DIDCreate()}
        did_result = wallet_api.wallet_did_create_post(**data)
        TenantIssuer.update_by_id(
            tenant.tenant_id,
            {
                "public_did": did_result.result.did,
                "public_did_state": PublicDIDStateType.private,
            },
        )

        return did_result
