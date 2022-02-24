import importlib
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from starlette_context import context

from api.core.config import settings
from api.core.event_bus import Event
from api.core.profile import Profile
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
)
from api.services.IssuerWorkflow import IssuerWorkflow
from api.services.SchemaWorkflow import SchemaWorkflow


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
        tenant_workflow = await next_workflow_step(db, tenant_workflow=tenant_workflow)

    return tenant_workflow


def instantiate_workflow_class(db: AsyncSession, tenant_workflow: TenantWorkflowRead):
    """Create an instance of a workflow class."""
    workflow_type = tenant_workflow.workflow_type
    module_name, class_name = workflow_type.rsplit(".", 1)
    WorkflowClass = getattr(importlib.import_module(module_name), class_name)
    instance = WorkflowClass(db, tenant_workflow)
    return instance


async def next_workflow_step(
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

    workflow = instantiate_workflow_class(db, tenant_workflow)

    # ping workflow to execute next step
    tenant_workflow = await workflow.run_step(webhook_message=webhook_message)

    return tenant_workflow


async def handle_issuer_worklflow_events(profile: Profile, event: Event):
    # find related workflow
    logger.warn(f">>> find issuer workflow for {profile} {event}")
    try:
        workflow_id = await IssuerWorkflow.find_workflow_id(profile, event.payload)
        logger.warn(f"    ... {workflow_id}")
        if workflow_id:
            await next_workflow_step(
                profile.db,
                workflow_id=workflow_id,
                webhook_message=event.payload,
            )
        else:
            return
    except DoesNotExist:
        # no related workflow so ignore, for now ...
        return


async def handle_schema_worklflow_events(profile: Profile, event: Event):
    # find related workflow
    logger.warn(f">>> find schema workflow for {profile} {event}")
    try:
        workflow_id = await SchemaWorkflow.find_workflow_id(profile, event.payload)
        logger.warn(f"    ... {workflow_id}")
        if workflow_id:
            await next_workflow_step(
                profile.db,
                workflow_id=workflow_id,
                webhook_message=event.payload,
            )
        else:
            return
    except DoesNotExist:
        # no related workflow so ignore, for now ...
        return


def subscribe_workflow_events():
    settings.EVENT_BUS.subscribe(
        WEBHOOK_CONNECTIONS_LISTENER_PATTERN, handle_issuer_worklflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_ENDORSE_LISTENER_PATTERN, handle_issuer_worklflow_events
    )
    settings.EVENT_BUS.subscribe(
        WEBHOOK_ENDORSE_LISTENER_PATTERN, handle_schema_worklflow_events
    )
