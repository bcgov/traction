import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.services.v1 import issuer_service
from api.services.v1.issuer_service import IssueCredentialData

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db


from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialPreview,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/credentials", response_model=List[IssueCredentialData])
async def get_issued_credentials(
    state: TenantWorkflowStateType | None = None,
    workflow_id: str | None = None,
    cred_issue_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[IssueCredentialData]:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    return issuer_service.get_issued_credentials(
        db, tenant_id, wallet_id, workflow_id, cred_issue_id, state
    )


@router.post("/credentials", status_code=status.HTTP_201_CREATED)
async def issue_new_credential(
    cred_protocol: IssueCredentialProtocolType,
    credential: CredentialPreview,
    cred_def_id: str | None = None,
    connection_id: str | None = None,
    alias: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> IssueCredentialData:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    return issuer_service.issue_new_credential(
        db,
        tenant_id,
        wallet_id,
        cred_protocol,
        credential,
        cred_def_id,
        connection_id,
        alias,
    )


@router.post("/credentials/revoke", status_code=status.HTTP_201_CREATED)
async def revoke_issued_credential(
    cred_issue_id: str | None = None,
    rev_reg_id: str | None = None,
    cred_rev_id: str | None = None,
    comment: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> IssueCredentialData:
    """
    write an entry to the revocation registry
    and notify the holder if an active connection exists
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    return issuer_service.revoke_issued_credential(
        db,
        tenant_id,
        wallet_id,
        cred_issue_id,
        rev_reg_id,
        cred_rev_id,
        comment,
    )
