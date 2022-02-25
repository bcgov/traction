import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.errors import DoesNotExist
from api.db.models.issue_credential import (
    IssueCredentialCreate,
    IssueCredentialRead,
    IssueCredentialUpdate,
)
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.services.connections import (
    get_connection_with_alias,
)

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialType,
    CredentialStateType,
    CredentialRoleType,
    CredentialPreview,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
)
from api.services.tenant_workflows import create_workflow
from api.services.base import BaseWorkflow


router = APIRouter()
logger = logging.getLogger(__name__)


class IssueCredentialData(BaseModel):
    credential: IssueCredentialRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.get("/issue", response_model=List[IssueCredentialData])
async def get_issue_credentials(db: AsyncSession = Depends(get_db)):
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    issue_repo = IssueCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    issue_creds = await issue_repo.find_by_wallet_id(wallet_id)
    issues = []
    for issue_cred in issue_creds:
        tenant_workflow = None
        if issue_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(issue_cred.workflow_id)
            except DoesNotExist:
                pass
        issue = IssueCredentialData(
            credential=issue_cred,
            workflow=tenant_workflow,
        )
        issues.append(issue)
    return issues


@router.post("/issue", response_model=IssueCredentialData)
async def issue_credential(
    cred_protocol: IssueCredentialProtocolType,
    cred_type: CredentialType,
    credential: CredentialPreview,
    cred_def_id: str | None = None,
    connection_id: str | None = None,
    alias: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    if not connection_id:
        existing_connection = get_connection_with_alias(alias)
        if not existing_connection:
            raise HTTPException(
                status_code=404, detail=f"Error alias {alias} does not exist"
            )
        connection_id = existing_connection.connection_id

    if cred_protocol == IssueCredentialProtocolType.v20:
        raise NotImplementedError()  # TODO
    if cred_type == CredentialType.json_ld:
        raise NotImplementedError()  # TODO

    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    issue_repo = IssueCredentialsRepository(db_session=db)

    issue_cred = IssueCredentialCreate(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        connection_id=connection_id,
        cred_type=cred_type,
        cred_protocol=cred_protocol,
        cred_def_id=cred_def_id,
        credential=credential.toJSON(),
        issue_role=CredentialRoleType.issuer,
        issue_state=CredentialStateType.pending,
    )
    issue_cred = await issue_repo.create(issue_cred)

    tenant_workflow = await create_workflow(
        wallet_id,
        TenantWorkflowTypeType.issue_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    issue_update = IssueCredentialUpdate(
        id=issue_cred.id,
        workflow_id=tenant_workflow.id,
        issue_state=issue_cred.issue_state,
    )
    issue_cred = await issue_repo.update(issue_update)
    logger.debug(f">>> Updated issue_cred: {issue_cred}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db, tenant_workflow=tenant_workflow
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    issue_cred = await issue_repo.get_by_id(issue_cred.id)
    logger.debug(f">>> Updated (final) issue_cred: {issue_cred}")

    issue = IssueCredentialData(
        credential=issue_cred,
        workflow=tenant_workflow,
    )

    return issue


@router.get("/", response_model=List[dict])
async def get_credentials(db: AsyncSession = Depends(get_db)):
    return []
