import logging

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.core.config import settings

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.verifier import (
    PresentationRequestTemplateListParameters,
    PresentationRequestTemplateListResponse,
    CreatePresentationRequestTemplatePayload,
    GetPresentationRequestTemplateResponse,
)
from api.endpoints.routes.v1.link_utils import build_list_links

from api.services.v1 import verifier_service

from api.endpoints.models.v1.governance import (
    TemplateStatusType,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PresentationRequestTemplateListResponse,
)
async def list_presentation_request_templates(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    name: str | None = None,
    status: TemplateStatusType | None = None,
    external_reference_id: str | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
) -> PresentationRequestTemplateListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = PresentationRequestTemplateListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        name=name,
        deleted=deleted,
        status=status,
        tags=tags,
        external_reference_id=external_reference_id,
    )
    items, total_count = await verifier_service.list_presentation_request_templates(
        tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return PresentationRequestTemplateListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post("/", status_code=status.HTTP_200_OK)
async def create_presentation_request_template(
    payload: CreatePresentationRequestTemplatePayload,
) -> GetPresentationRequestTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await verifier_service.create_presentation_request_template(
        tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO

    return GetPresentationRequestTemplateResponse(item=item, links=links)
