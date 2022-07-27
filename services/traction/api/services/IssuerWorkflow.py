import logging
import requests
import time

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.models.tenant_issuer import TenantIssuerUpdate, TenantIssuerRead
from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.connections import (
    ConnectionStateType,
)
from api.endpoints.models.tenant_issuer import PublicDIDStateType

from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.connections import (
    receive_invitation,
)
from api.services.base import BaseWorkflow


from acapy_client.api.connection_api import ConnectionApi
from acapy_client.api.endorse_transaction_api import EndorseTransactionApi
from acapy_client.api.ledger_api import LedgerApi
from acapy_client.api.wallet_api import WalletApi
from acapy_client.model.did_create import DIDCreate


logger = logging.getLogger(__name__)

connection_api = ConnectionApi(api_client=get_api_client())
endorse_api = EndorseTransactionApi(api_client=get_api_client())
ledger_api = LedgerApi(api_client=get_api_client())
wallet_api = WalletApi(api_client=get_api_client())


class IssuerWorkflow(BaseWorkflow):
    """Workflow to setup a tenant's Issuer configuration."""

    @classmethod
    async def handle_workflow_events(cls, profile: Profile, event: Event):
        # find related workflow
        try:
            workflow_id = await cls.find_workflow_id(profile, event.payload)
            if workflow_id:
                await cls.next_workflow_step(
                    profile.db,
                    workflow_id=workflow_id,
                    webhook_message=event.payload,
                )
            else:
                return
        except DoesNotExist:
            # no related workflow so ignore, for now ...
            return

    @classmethod
    async def find_workflow_id(cls, profile: Profile, webhook_message: dict):
        # find related workflow
        issuer_repo = TenantIssuersRepository(db_session=profile.db)
        if webhook_message["topic"] == "connections":
            try:
                tenant_issuer = (
                    await issuer_repo.get_by_wallet_and_endorser_connection_id(
                        profile.wallet_id,
                        webhook_message["payload"]["connection_id"],
                    )
                )
                return tenant_issuer.workflow_id
            except DoesNotExist:
                # no related workflow so ignore, for now ...
                return None
        elif webhook_message["topic"] == "endorse_transaction":
            # TODO when we need to handle the DID publishing
            return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `IssuerWorkflow` instance.

        Args:
            session: The Askar profile session instance to use
        """
        super(IssuerWorkflow, self).__init__(db, tenant_workflow)
        self._issuer_repo = TenantIssuersRepository(db_session=db)

    @property
    def issuer_repo(self) -> TenantIssuersRepository:
        """Accessor for issuer_repo instance."""
        return self._issuer_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        tenant_issuer = await self.issuer_repo.get_by_wallet_id(
            self.tenant_workflow.wallet_id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        logger.debug(f">>> start workflow run_step() with: {self.tenant_workflow}")
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            # first step is to initiate the connection to the Endorser
            tenant_issuer = await self.initiate_connection(tenant_issuer)

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            webhook_topic = webhook_message["topic"]
            process_public_did = False
            complete_workflow = False
            logger.debug(f">>> run in_progress workflow for topic: {webhook_topic}")
            if webhook_topic == WebhookTopicType.connections:
                (process_public_did, tenant_issuer) = await self.process_connection(
                    tenant_issuer, webhook_message
                )

            elif webhook_topic == WebhookTopicType.endorse_transaction:
                # TODO once we need to handle endorsements
                pass

            else:
                logger.warn(f">>> ignoring topic for now: {webhook_topic}")

            if complete_workflow:
                # finish off our workflow
                await self.complete_workflow()
                await self.workflow_notifier.issuer_workflow_completed(tenant_issuer)

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def initiate_connection(
        self, tenant_issuer: TenantIssuerRead
    ) -> TenantIssuerRead:
        logger.debug(">>> initiate connection to endorser ...")
        endorser_alias = settings.ENDORSER_CONNECTION_ALIAS
        endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
        connection = receive_invitation(
            endorser_alias, their_public_did=endorser_public_did
        )
        # add the endorser connection id to our tenant issuer setup
        update_issuer = TenantIssuerUpdate(
            id=tenant_issuer.id,
            workflow_id=self.tenant_workflow.id,
            endorser_connection_id=connection.connection_id,
            endorser_connection_state=connection.state,
        )
        tenant_issuer = await self.issuer_repo.update(update_issuer)
        return tenant_issuer

    async def process_connection(
        self, tenant_issuer: TenantIssuerRead, webhook_message: dict
    ) -> (bool, TenantIssuerRead):
        # check if we need to update the connection state in our issuer record
        process_public_did = False
        connection_state = webhook_message["payload"]["state"]
        connection_id = webhook_message["payload"]["connection_id"]
        # only do this on a state change to prevent a double-tap
        if not connection_state == tenant_issuer.endorser_connection_state:
            update_issuer = TenantIssuerUpdate(
                id=tenant_issuer.id,
                workflow_id=tenant_issuer.workflow_id,
                endorser_connection_id=tenant_issuer.endorser_connection_id,
                endorser_connection_state=connection_state,
            )
            tenant_issuer = await self.issuer_repo.update(update_issuer)

            if (
                connection_state == ConnectionStateType.active
                or connection_state == ConnectionStateType.completed
            ):
                self.update_connection_metadata(connection_id)
                process_public_did = True
        return process_public_did, tenant_issuer

    def update_connection_metadata(self, connection_id: str):
        logger.debug(f">>> checking for metadata on connection: {connection_id}")
        conn_meta_data = connection_api.connections_conn_id_metadata_get(connection_id)
        add_meta_data = True
        if "transaction-jobs" in conn_meta_data.results:
            if "transaction_my_job" in conn_meta_data.results["transaction-jobs"]:
                add_meta_data = False

        if add_meta_data:
            logger.debug(f">>> add metadata to endorser connection: {connection_id}")
            # TODO - pause here to prevent race condition with endorser
            # (error if both update endorser role at the same time)
            time.sleep(1)

            # attach some meta-data to the connection
            # TODO verify response from each call ...
            data = {"transaction_my_job": "TRANSACTION_AUTHOR"}
            endorse_api.transactions_conn_id_set_endorser_role_post(
                connection_id, **data
            )
            endorser_alias = settings.ENDORSER_CONNECTION_ALIAS
            endorser_public_did = settings.ACAPY_ENDORSER_PUBLIC_DID
            data = {"endorser_name": endorser_alias}
            endorse_api.transactions_conn_id_set_endorser_info_post(
                connection_id, endorser_public_did, **data
            )
