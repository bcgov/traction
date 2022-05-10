import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db

from api.db.repositories.tenant_issuers import TenantIssuersRepository

from api.endpoints.models.v1.admin import AdminTenantIssueRead

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/self", status_code=status.HTTP_200_OK, response_model=AdminTenantIssueRead
)
async def get_tenant_information(
    db: AsyncSession = Depends(get_db),
) -> AdminTenantIssueRead:
    # TODO: create a specific model object for this...
    """
    check state of tenant and state of public did.
    """
    # copied from v0
    wallet_id = get_from_context("TENANT_WALLET_ID")
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)

    response = AdminTenantIssueRead(**tenant_issuer.__dict__)

    return response
