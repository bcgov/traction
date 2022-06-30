import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.endpoints.models.v1.tenant import TenantGetResponse
from api.services.v1 import innkeeper_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/{tenant_id}/make-issuer",
    status_code=status.HTTP_200_OK,
    response_model=TenantGetResponse,
)
async def initialize_issuer(
    request: Request,
    tenant_id: UUID,
) -> TenantGetResponse:

    item = await innkeeper_service.make_issuer(
        tenant_id,
    )

    links = []  # TODO: determine useful links for /make-issuer

    return TenantGetResponse(item=item, links=links)
