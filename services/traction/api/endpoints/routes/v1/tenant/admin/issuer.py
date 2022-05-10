import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db
from api.services.tenant_workflows import create_workflow

from api.db.repositories.tenant_issuers import TenantIssuersRepository

from api.endpoints.models.tenant_workflow import TenantWorkflowTypeType
from api.endpoints.models.v1.admin import AdminTenantIssueRead

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/make-issuer", status_code=status.HTTP_200_OK, response_model=AdminTenantIssueRead
)
async def init_issuer(db: AsyncSession = Depends(get_db)) -> AdminTenantIssueRead:
    # TODO: update to use a v1 style response, not v0 classes
    """
    If the innkeeper has authorized your tenant to become an issuer, initialize
    here to write a endorsed public did the configured Hyperledger-Indy service
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    issuer_repo = TenantIssuersRepository(db_session=db)
    # create workflow and update issuer record
    await create_workflow(
        wallet_id,
        TenantWorkflowTypeType.issuer,
        db,
    )
    # get updated issuer info (should have workflow id and connection_id)
    tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)

    return tenant_issuer
