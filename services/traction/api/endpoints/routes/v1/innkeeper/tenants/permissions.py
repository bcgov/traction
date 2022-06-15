import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.endpoints.models.v1.tenant import (
    TenantPermissionsGetResponse,
    UpdateTenantPermissionsPayload,
    UpdateTenantPermissionsResponse,
)
from api.services.v1 import innkeeper_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/permissions",
    status_code=status.HTTP_200_OK,
    response_model=TenantPermissionsGetResponse,
)
async def get_tenant_permissions(
    request: Request,
    tenant_id: UUID,
) -> TenantPermissionsGetResponse:

    item = await innkeeper_service.get_tenant_permissions(tenant_id)

    links = []  # TODO: determine links

    return TenantPermissionsGetResponse(item=item, links=links)


@router.put(
    "/permissions",
    status_code=status.HTTP_200_OK,
    response_model=UpdateTenantPermissionsResponse,
)
async def update_tenant_permissions(
    request: Request,
    tenant_id: UUID,
    payload: UpdateTenantPermissionsPayload,
) -> UpdateTenantPermissionsResponse:

    item = await innkeeper_service.update_tenant_permissions(tenant_id, payload)

    links = []  # TODO: determine links

    return UpdateTenantPermissionsResponse(item=item, links=links)
