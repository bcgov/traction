from uuid import UUID
import requests
import logging
from re import Pattern

from acapy_client.api.ledger_api import LedgerApi
from acapy_client.api.wallet_api import WalletApi
from acapy_client.model.did_create import DIDCreate
from api.api_client_utils import get_api_client
from api.core.config import settings

from api.endpoints.models.tenant_issuer import PublicDIDStateType
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.models.tenant_issuer import TenantIssuerUpdate, TenantIssuerRead

from api.db.models.tenant import Tenant

# from api.db.models.v1.tenant import Tenant2
# from api.db.models.v1.tenant_issuer import TenantIssuer
from api.db.session import async_session


from api.tasks.base_tasks import (
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
    def __init__(self):
        self._issuer_repo = TenantIssuersRepository
        super(RegisterPublicDIDTask, self).__init__()

    @staticmethod
    def _listener_pattern() -> Pattern[str]:
        return TRACTION_REGISTER_PUBLIC_DID_PATTERN

    @staticmethod
    def _event_topic() -> str:
        return TRACTION_TASK_PREFIX + TractionTaskType.register_public_did

    def _get_db_model_class(self):
        return Tenant

    def _get_id_from_payload(self, payload):
        self.logger.info(f"> _get_id_from_payload ->> {payload.keys()}")
        rpd_t_id = payload["tenant_id"]
        return rpd_t_id

    async def _perform_task(self, tenant: Tenant, payload: dict):
        self.logger.info("> _perform_task()")

        tenant_issuer = None
        async with async_session() as db:
            tenant_issuer = await self._issuer_repo(db).get_by_tenant_id(tenant.id)

        if tenant_issuer.public_did_state != "N/A":
            raise Exception("TenantIssuer already has a public did")

        await self.initiate_public_did(tenant_issuer)

    # TODO delete this method when default behaviour works.
    async def _handle_perform_task_error(
        self, tenant: Tenant, payload: dict, exc: Exception
    ):
        self.logger.warning("> _handle_perform_task_error()")
        self.logger.warning(
            "> error detail not saved as columns do not exist on Tenant"
        )
        self.logger.error(str(exc))
        # old tenant model doesn't have columns to update
        pass

    @classmethod
    async def assign(
        cls,
        tenant_id: UUID,
        wallet_id: UUID,
        payload: dict,
    ):

        await cls._assign(tenant_id, wallet_id, payload)
        pass

    async def initiate_public_did(self, tenant_issuer: TenantIssuerRead) -> None:
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

    async def create_local_did(
        self, tenant_issuer: TenantIssuerRead
    ) -> (TenantIssuerRead, dict):
        self.logger.warn("> create_public_did:")

        data = {"body": DIDCreate()}
        did_result = wallet_api.wallet_did_create_post(**data)
        connection_state = tenant_issuer.endorser_connection_state
        update_issuer = TenantIssuerUpdate(
            id=tenant_issuer.id,
            workflow_id=tenant_issuer.workflow_id,
            endorser_connection_id=tenant_issuer.endorser_connection_id,
            endorser_connection_state=connection_state,
            public_did=did_result.result.did,
            public_did_state=PublicDIDStateType.private,
        )
        async with async_session() as db:
            tenant_issuer = await self._issuer_repo(db).update(update_issuer)
        return (tenant_issuer, did_result)

    async def initiate_public_did_workflow(
        self, tenant_issuer: TenantIssuerRead, did_result: dict
    ) -> TenantIssuerRead:
        self.logger.warn("> initiate_public_did_workflow:")
        data = {"alias": tenant_issuer.tenant_id}
        ledger_api.ledger_register_nym_post(
            did_result.result.did,
            did_result.result.verkey,
            **data,
        )
        connection_state = tenant_issuer.endorser_connection_state
        update_issuer = TenantIssuerUpdate(
            id=tenant_issuer.id,
            workflow_id=tenant_issuer.workflow_id,
            endorser_connection_id=tenant_issuer.endorser_connection_id,
            endorser_connection_state=connection_state,
            public_did=tenant_issuer.public_did,
            public_did_state=PublicDIDStateType.requested,
        )
        async with async_session() as db:
            tenant_issuer = await self._issuer_repo(db).update(update_issuer)
        return tenant_issuer

    async def create_public_did(
        self, tenant_issuer: TenantIssuerRead, did_result: dict
    ) -> TenantIssuerRead:
        self.logger.warn("> create_public_did:")
        genesis_url = settings.ACAPY_GENESIS_URL
        did_registration_url = genesis_url.replace("genesis", "register")
        data = {
            "did": did_result.result.did,
            "verkey": did_result.result.verkey,
            "alias": str(tenant_issuer.tenant_id),
        }
        requests.post(did_registration_url, json=data)

        # now make it public, endorser signs this txn
        # TODO if endorser doesn't automatically sign txn's, this will become
        # async, could sit 'pending' forever
        did_result = wallet_api.wallet_did_public_post(did_result.result.did)

        connection_state = tenant_issuer.endorser_connection_state
        update_issuer = TenantIssuerUpdate(
            id=tenant_issuer.id,
            workflow_id=tenant_issuer.workflow_id,
            endorser_connection_id=tenant_issuer.endorser_connection_id,
            endorser_connection_state=connection_state,
            public_did=tenant_issuer.public_did,
            public_did_state=PublicDIDStateType.public,
        )

        async with async_session() as db:
            tenant_issuer = await self._issuer_repo(db).update(update_issuer)
        return (tenant_issuer, did_result)
