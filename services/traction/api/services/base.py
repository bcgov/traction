import logging
import importlib
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import context

from api.core.event_bus import Event
from api.core.profile import Profile
from api.db.errors import DoesNotExist
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
    TenantWorkflowUpdate,
)
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
    TenantWorkflowStateType,
)
from api.services.tenant_workflow_notifier import TenantWorkflowNotifier

logger = logging.getLogger(__name__)


def instantiate_workflow_class(workflow_type: TenantWorkflowTypeType):
    """Create an instance of a workflow class."""
    module_name, class_name = workflow_type.rsplit(".", 1)
    WorkflowClass = getattr(importlib.import_module(module_name), class_name)
    return WorkflowClass


def instantiate_workflow_class_instance(
    db: AsyncSession, tenant_workflow: TenantWorkflowRead
):
    """Create an instance of a workflow class."""
    workflow_type = tenant_workflow.workflow_type
    WorkflowClass = instantiate_workflow_class(workflow_type)
    instance = WorkflowClass(db, tenant_workflow)
    return instance


class BaseWorkflow:
    """Base class for workflows."""

    @classmethod
    async def handle_workflow_events(cls, profile: Profile, event: Event):
        raise NotImplementedError()

    @classmethod
    async def find_workflow_id(cls, profile: Profile, webhook_message: dict):
        raise NotImplementedError()

    @classmethod
    async def next_workflow_step(
        cls,
        db: AsyncSession,
        workflow_id: UUID = None,
        tenant_workflow: TenantWorkflowRead = None,
        webhook_message: dict = None,
    ) -> TenantWorkflowRead:
        """Poke the workflow to run the next step."""
        workflow_repo = TenantWorkflowsRepository(db_session=db)

        if not tenant_workflow:
            if workflow_id:
                tenant_workflow = await workflow_repo.get_by_id(workflow_id)

        if not tenant_workflow:
            raise DoesNotExist(f"Workflow not found for {workflow_id}")

        # check if our tenant is in context
        context_bearer_token = (context.get("TENANT_WALLET_TOKEN"),)
        if (not context_bearer_token) or (
            not context_bearer_token == tenant_workflow.wallet_bearer_token
        ):
            context["TENANT_WALLET_TOKEN"] = tenant_workflow.wallet_bearer_token

        workflow = instantiate_workflow_class_instance(db, tenant_workflow)

        # ping workflow to execute next step
        tenant_workflow = await workflow.run_step(webhook_message=webhook_message)

        return tenant_workflow

    def __init__(self, db: AsyncSession, tenant_workflow: TenantWorkflowRead):
        """
        Initialize a new `SchemaWorkflow` instance.
        """
        self._db = db
        self._tenant_workflow = tenant_workflow
        self._workflow_repo = TenantWorkflowsRepository(db_session=db)
        self._workflow_notifier = TenantWorkflowNotifier(db=db)

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

    @property
    def workflow_notifier(self) -> TenantWorkflowNotifier:
        """Accessor for workflow_notifier instance."""
        return self._workflow_notifier

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
