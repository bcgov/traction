import logging
import json

from sqlalchemy.ext.asyncio import AsyncSession

from api.api_client_utils import get_api_client
from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.repositories.tenant_connections import TenantConnectionsRepository
from api.db.models.tenant_connection import TenantConnectionUpdate, TenantConnectionRead
from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.connections import (
    ConnectionStateType,
    ConnectionRoleType,
)
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WebhookTopicType,
)
from api.services.connections import (
    create_invitation,
    receive_invitation,
)
from api.services.base import BaseWorkflow


from acapy_client.api.connection_api import ConnectionApi


logger = logging.getLogger(__name__)

connection_api = ConnectionApi(api_client=get_api_client())


class ConnectionWorkflow(BaseWorkflow):
    """Workflow to setup a tenant connection."""

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
        connection_repo = TenantConnectionsRepository(db_session=profile.db)
        if webhook_message["topic"] == "connections":
            try:
                tenant_connection = (
                    await connection_repo.get_by_wallet_and_connection_id(
                        profile.wallet_id,
                        webhook_message["payload"]["connection_id"],
                    )
                )
                return tenant_connection.workflow_id
            except DoesNotExist:
                # no related workflow so ignore, for now ...
                return None
        else:
            return None

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `ConnectionWorkflow` instance.

        Args:
            session: The Askar profile session instance to use
        """
        super(ConnectionWorkflow, self).__init__(db, tenant_workflow)
        self._connection_repo = TenantConnectionsRepository(db_session=db)

    @property
    def connection_repo(self) -> TenantConnectionsRepository:
        """Accessor for connection_repo instance."""
        return self._connection_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        wallet_id = get_from_context("TENANT_WALLET_ID")
        tenant_connection = await self.connection_repo.get_by_workflow_id(
            wallet_id, self.tenant_workflow.id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        logger.debug(f">>> start workflow run_step() with: {self.tenant_workflow}")
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "in_progress"
            await self.start_workflow()

            # first step is to initiate the connection
            if tenant_connection.connection_role == ConnectionRoleType.inviter:
                tenant_connection = await self.initiate_conn_invitation(
                    tenant_connection
                )

            elif tenant_connection.connection_role == ConnectionRoleType.invitee:
                tenant_connection = await self.initiate_conn_request(tenant_connection)

            else:
                # ignore for now
                pass

        # if workflow is "in_progress" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of webhook, so need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.in_progress:
            webhook_topic = webhook_message["topic"]
            logger.debug(f">>> run in_progress workflow for topic: {webhook_topic}")
            if webhook_topic == WebhookTopicType.connections:
                if webhook_message["payload"].get("state"):
                    # check for state of "active"
                    webhook_state = webhook_message["payload"]["state"]
                    logger.debug(f">>> checking for webhook_state: {webhook_state}")
                    # update our status
                    tenant_connection = await self.update_connection_state(
                        tenant_connection, webhook_state
                    )
                    if (
                        webhook_state == ConnectionStateType.active
                        or webhook_state == ConnectionStateType.completed
                    ):
                        logger.info(
                            f">>> sending connection active: {tenant_connection}"
                        )
                        await self.workflow_notifier.issuer_workflow_connection_active(
                            tenant_connection
                        )

                        # finish off our workflow
                        await self.complete_workflow()

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow

    async def initiate_conn_invitation(
        self, tenant_connection: TenantConnectionRead
    ) -> TenantConnectionRead:
        logger.debug(">>> initiate connection invitation ...")
        invitation = create_invitation(
            tenant_connection.alias, tenant_connection.connection_protocol
        )
        update_connection = TenantConnectionUpdate(
            id=tenant_connection.id,
            workflow_id=tenant_connection.workflow_id,
            connection_state=ConnectionStateType.invitation,
            connection_protocol=tenant_connection.connection_protocol,
            connection_id=invitation.connection_id,
            invitation=json.dumps(invitation.invitation),
            invitation_url=invitation.invitation_url,
        )
        tenant_connection = await self.connection_repo.update(update_connection)
        return tenant_connection

    async def initiate_conn_request(
        self, tenant_connection: TenantConnectionRead
    ) -> TenantConnectionRead:
        logger.debug(">>> initiate connection request ...")
        invitation = receive_invitation(
            alias=tenant_connection.alias,
            payload=json.loads(tenant_connection.invitation),
            their_public_did=tenant_connection.their_public_did,
        )
        update_connection = TenantConnectionUpdate(
            id=tenant_connection.id,
            workflow_id=tenant_connection.workflow_id,
            connection_state=ConnectionStateType.request,
            connection_id=invitation.connection_id,
            invitation=tenant_connection.invitation,
        )
        tenant_connection = await self.connection_repo.update(update_connection)
        return tenant_connection

    async def update_connection_state(
        self, tenant_connection: TenantConnectionRead, state: str
    ) -> TenantConnectionRead:
        logger.debug(f">>> updating state to {state}")
        update_connection = TenantConnectionUpdate(
            id=tenant_connection.id,
            workflow_id=self.tenant_workflow.id,
            connection_state=state,
            connection_protocol=tenant_connection.connection_protocol,
            connection_id=tenant_connection.connection_id,
            invitation=tenant_connection.invitation,
            invitation_url=tenant_connection.invitation_url,
            their_public_did=tenant_connection.their_public_did,
        )
        tenant_connection = await self.connection_repo.update(update_connection)
        return tenant_connection
