import logging


from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.core.config import settings
from api.endpoints.models.v1.innkeeper import (
    CheckInResponse,
    CheckInPayload,
    TenantListResponse,
    TenantListParameters,
)
from api.endpoints.models.v1.tenant import PublicDIDStatus, IssuerStatus
from api.services.v1 import innkeeper_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    status_code=status.HTTP_200_OK,
    response_model=CheckInResponse,
)
async def check_in_tenant(payload: CheckInPayload) -> CheckInResponse:
    item = await innkeeper_service.check_in_tenant(payload=payload)

    links = []  # TODO: determine useful links for /check-in

    return CheckInResponse(item=item, links=links)


@router.get("/", status_code=status.HTTP_200_OK, response_model=TenantListResponse)
async def list_tenants(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    public_did_status: PublicDIDStatus | None = None,
    issuer: bool | None = False,
    issuer_status: IssuerStatus | None = None,
    deleted: bool | None = False,
) -> TenantListResponse:

    parameters = TenantListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        public_did_status=public_did_status,
        issuer=issuer,
        issuer_status=issuer_status,
        deleted=deleted,
    )
    items, total_count = await innkeeper_service.list_tenants(parameters)

    links = []

    return TenantListResponse(
        items=items, count=len(items), total=total_count, links=links
    )
