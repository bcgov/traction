from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.db.models.tenant_issuer import (
    TenantIssuerRead,
    TenantIssuerUpdate,
)
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
    TenantWorkflowUpdate,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)
from api.services.connections import (
    receive_invitation,
)


class IssuerWorkflow:
    """Workflow to setup a tenant's Issuer configuration."""

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `IssuerWorkflow` instance.

        Args:
            session: The Askar profile session instance to use
        """
        self._db = db
        self._tenant_workflow = tenant_workflow
        self._issuer_repo = TenantIssuersRepository(db_session=db)
        self._workflow_repo = TenantWorkflowsRepository(db_session=db)

    @property
    def db(self) -> AsyncSession:
        """Accessor for db session instance."""
        return self._db

    @property
    def tenant_workflow(self) -> TenantWorkflowRead:
        """Accessor for tenant_workflow instance."""
        return self._tenant_workflow

    @property
    def issuer_repo(self) -> TenantIssuersRepository:
        """Accessor for issuer_repo instance."""
        return self._issuer_repo

    @property
    def workflow_repo(self) -> TenantWorkflowsRepository:
        """Accessor for workflow_repo instance."""
        return self._workflow_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        tenant_issuer = await self.issuer_repo.get_by_wallet_id(
            self.tenant_workflow.wallet_id
        )

        # if workflow is "pending" then we need to start it
        # called direct from the tenant admin api so the tenant is "in context"
        if self.tenant_workflow.workflow_state == TenantWorkflowStateType.pending:
            # update the workflow status as "active"
            update_workflow = TenantWorkflowUpdate(
                id=self.tenant_workflow.id,
                workflow_state=TenantWorkflowStateType.active,
                wallet_bearer_token=self.tenant_workflow.wallet_bearer_token,
            )
            self._tenant_workflow = await self.workflow_repo.update(update_workflow)

            # first step is to initiate the connection to the Endorser
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


        # if workflow is "active" we need to check what state we are at,
        # ... and initiate the next step (if applicable)
        # called on receipt of a webhook, so we need to put the proper tenant "in context"
        elif self.tenant_workflow.workflow_state == TenantWorkflowStateType.active:
            pass

        # if workflow is "completed" or "error" then we are done
        else:
            pass

        return self.tenant_workflow
