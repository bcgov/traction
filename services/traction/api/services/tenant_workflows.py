import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import context

from api.core.config import settings
from api.db.errors import DoesNotExist
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
    TenantWorkflowCreate,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
    TenantWorkflowStateType,
)
from api.endpoints.models.webhooks import (
    WEBHOOK_CONNECTIONS_LISTENER_PATTERN,
    WEBHOOK_ENDORSE_LISTENER_PATTERN,
    WEBHOOK_ISSUE_LISTENER_PATTERN,
    WEBHOOK_PRESENT_LISTENER_PATTERN,
    WEBHOOK_PROBLEM_REPORT_LISTENER_PATTERN,
    WEBHOOK_REVOC_NOTIFY_LISTENER_PATTERN,
)
from api.services.base import BaseWorkflow
from api.services.ConnectionWorkflow import ConnectionWorkflow
from api.services.IssuerWorkflow import IssuerWorkflow
from api.services.SchemaWorkflow import SchemaWorkflow
from api.services.IssueCredentialWorkflow import IssueCredentialWorkflow
from api.services.PresentCredentialWorkflow import PresentCredentialWorkflow


logger = logging.getLogger(__name__)


async def create_workflow(
    wallet_id: UUID,
    workflow_type: TenantWorkflowTypeType,
    db: AsyncSession,
    error_if_wf_exists: bool = True,
    start_workflow: bool = True,
) -> TenantWorkflowRead:
    """Create (and optionally start) a new workflow."""
    workflow_repo = TenantWorkflowsRepository(db_session=db)

    if error_if_wf_exists:
        try:
            existing_wf = await workflow_repo.find_by_wallet_id_and_type(
                wallet_id, workflow_type
            )
            if existing_wf and 0 < len(existing_wf):
                # we get here so it is an error
                raise Exception(
                    f"Error workflow for {wallet_id} {workflow_type} already exists"
                )
        except DoesNotExist:
            # workflow doesn't exist is what we want
            pass

    new_workflow = TenantWorkflowCreate(
        wallet_id=wallet_id,
        workflow_type=workflow_type,
        workflow_state=TenantWorkflowStateType.pending,
        wallet_bearer_token=context.get("TENANT_WALLET_TOKEN"),
    )
    tenant_workflow = await workflow_repo.create(new_workflow)

    if start_workflow:
        tenant_workflow = await BaseWorkflow.next_workflow_step(
            db, tenant_workflow=tenant_workflow
        )

    return tenant_workflow


def subscribe_workflow_events():
    settings.EVENT_BUS.subscribe(
        WEBHOOK_CONNECTIONS_LISTENER_PATTERN, ConnectionWorkflow.handle_workflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_CONNECTIONS_LISTENER_PATTERN, IssuerWorkflow.handle_workflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_ENDORSE_LISTENER_PATTERN, IssuerWorkflow.handle_workflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_ENDORSE_LISTENER_PATTERN, SchemaWorkflow.handle_workflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_ISSUE_LISTENER_PATTERN, IssueCredentialWorkflow.handle_workflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_PROBLEM_REPORT_LISTENER_PATTERN,
        IssueCredentialWorkflow.handle_workflow_events,
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_REVOC_NOTIFY_LISTENER_PATTERN,
        IssueCredentialWorkflow.handle_workflow_events,
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_PRESENT_LISTENER_PATTERN,
        PresentCredentialWorkflow.handle_workflow_events,
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_PROBLEM_REPORT_LISTENER_PATTERN,
        PresentCredentialWorkflow.handle_workflow_events,
    )
