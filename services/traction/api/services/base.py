import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.profile import Profile
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
    TenantWorkflowUpdate,
)
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)


logger = logging.getLogger(__name__)


class BaseWorkflow:
    """Base class for workflows."""

    @classmethod
    async def find_workflow_id(cls, profile: Profile, webhook_message: dict):
        raise NotImplementedError()

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `SchemaWorkflow` instance.
        """
        self._db = db
        self._tenant_workflow = tenant_workflow
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
    def workflow_repo(self) -> TenantWorkflowsRepository:
        """Accessor for workflow_repo instance."""
        return self._workflow_repo

    async def run_step(self, webhook_message: dict = None) -> TenantWorkflowRead:
        raise NotImplementedError()

    async def start_workflow(self):
        # update the workflow status as "in_progress"
        logger.debug(">>> starting workflow ...")
        update_workflow = TenantWorkflowUpdate(
            id=self.tenant_workflow.id,
            workflow_state=TenantWorkflowStateType.in_progress,
            wallet_bearer_token=self.tenant_workflow.wallet_bearer_token,
        )
        self._tenant_workflow = await self.workflow_repo.update(update_workflow)

    async def complete_workflow(self):
        # finish off our workflow
        logger.debug(">>> completing workflow ...")
        update_workflow = TenantWorkflowUpdate(
            id=self.tenant_workflow.id,
            workflow_state=TenantWorkflowStateType.completed,
            wallet_bearer_token=None,
        )
        self._tenant_workflow = await self.workflow_repo.update(update_workflow)
