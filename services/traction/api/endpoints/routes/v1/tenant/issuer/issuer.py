import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db
from api.services.tenant_workflows import create_workflow

from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.db.models.tenant_issuer import TenantIssuerRead

from api.db.models.tenant_workflow import TenantWorkflowRead
from api.endpoints.models.tenant_workflow import TenantWorkflowTypeType

router = APIRouter()
logger = logging.getLogger(__name__)


class TenantIssuerData(BaseModel):
    issuer: TenantIssuerRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.post("/initalize", status_code=status.HTTP_200_OK)
async def init_issuer(db: AsyncSession = Depends(get_db)):
    """
    If the innkeeper has authorized your tenant to become an issuer, initialize
    here to write a endorsed public did the configured Hyperledger-Indy service
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    tenant_workflow = None
    if tenant_issuer.workflow_id:
        tenant_workflow = await workflow_repo.get_by_id(tenant_issuer.workflow_id)

    else:
        # create workflow and update issuer record
        tenant_workflow = await create_workflow(
            wallet_id,
            TenantWorkflowTypeType.issuer,
            db,
        )
        # get updated issuer info (should have workflow id and connection_id)
        tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)

    # issuer = TenantIssuerData(
    #     issuer=tenant_issuer,
    #     workflow=tenant_workflow,
    # )

    return tenant_issuer
