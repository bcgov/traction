import logging

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.endpoints.models.v1.tenant import (
    TenantConfigurationGetResponse,
    UpdateTenantConfigurationPayload,
    UpdateTenantConfigurationResponse,
)
from api.services.v1 import tenant_configuration_service as service
from api.endpoints.dependencies.tenant_security import get_from_context

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/configuration",
    status_code=status.HTTP_200_OK,
    response_model=TenantConfigurationGetResponse,
)
async def get_tenant_configuration(
    request: Request,
) -> TenantConfigurationGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await service.get_tenant_configuration(tenant_id, wallet_id)

    links = []  # TODO: determine links

    return TenantConfigurationGetResponse(item=item, links=links)


@router.put(
    "/configuration",
    status_code=status.HTTP_200_OK,
    response_model=UpdateTenantConfigurationResponse,
)
async def update_tenant_configuration(
    request: Request,
    payload: UpdateTenantConfigurationPayload,
) -> UpdateTenantConfigurationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await service.update_tenant_configuration(tenant_id, wallet_id, payload)

    links = []  # TODO: determine links

    return UpdateTenantConfigurationResponse(item=item, links=links)
