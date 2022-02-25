import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette_context import context

from api.db.errors import DoesNotExist
from api.db.models.issue_credential import (
    IssueCredentialRead,
)
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository

from api.endpoints.dependencies.db import get_db
from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialType,
)


router = APIRouter()
logger = logging.getLogger(__name__)


def get_from_context(name: str):
    result = context.get(name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error not authenticated",
        )
    return result


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
    credential: dict,
    cred_def_id: str | None = None,
    connection_id: str | None = None,
    alias: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    return None


@router.get("/", response_model=List[dict])
async def get_credentials(db: AsyncSession = Depends(get_db)):
    return []
