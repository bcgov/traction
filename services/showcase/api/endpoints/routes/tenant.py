import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.related import TenantReadWithSandbox
from api.endpoints.dependencies.db import get_db
from api.db.repositories.tenant import TenantRepository
from api.services import sandbox

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/tenants",
    status_code=status.HTTP_200_OK,
    response_model=List[TenantReadWithSandbox],
)
async def get_tenants(
    sandbox_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[TenantReadWithSandbox]:
    # this should take some query params, sorting and paging params...
    repo = TenantRepository(db_session=db)
    items = await repo.get_in_sandbox(sandbox_id)
    return items


@router.get(
    "/tenants/{tenant_id}",
    status_code=status.HTTP_200_OK,
    response_model=TenantReadWithSandbox,
)
async def get_tenant(
    sandbox_id: UUID,
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TenantReadWithSandbox:
    repo = TenantRepository(db_session=db)
    item = await repo.get_by_id_with_sandbox(sandbox_id, tenant_id)
    return item


@router.post(
    "/tenants/{tenant_id}/create-invitation/student",
    status_code=status.HTTP_200_OK,
    response_model=sandbox.InviteStudentResponse,
)
async def create_invitation_for_student(
    sandbox_id: UUID,
    tenant_id: UUID,
    payload: sandbox.InviteStudentRequest,
    db: AsyncSession = Depends(get_db),
) -> sandbox.InviteStudentResponse:
    return await sandbox.create_invitation_for_student(
        sandbox_id=sandbox_id, tenant_id=tenant_id, payload=payload, db=db
    )
