import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.core.config import settings
from api.endpoints.models.v1.holder import (
    HolderCredentialStatusType,
    HolderCredentialListParameters,
    HolderCredentialListResponse,
)
from api.endpoints.routes.v1.link_utils import build_list_links

from api.endpoints.dependencies.tenant_security import get_from_context
from api.services.v1 import holder_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=HolderCredentialListResponse
)
async def list_holder_credentials(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    name: str | None = None,
    contact_id: UUID | None = None,
    schema_id: str | None = None,
    cred_def_id: str | None = None,
    external_reference_id: str | None = None,
    status: HolderCredentialStatusType | None = None,
    acapy: bool | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
) -> HolderCredentialListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = HolderCredentialListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        name=name,
        deleted=deleted,
        contact_id=contact_id,
        schema_id=schema_id,
        cred_def_id=cred_def_id,
        external_reference_id=external_reference_id,
        status=status,
        acapy=acapy,
        tags=tags,
    )
    items, total_count = await holder_service.list_holder_credentials(
        tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return HolderCredentialListResponse(
        items=items, count=len(items), total=total_count, links=links
    )
