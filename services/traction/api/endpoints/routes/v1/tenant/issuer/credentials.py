import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.background import BackgroundTasks
from starlette.requests import Request

from api.core.config import settings
from api.endpoints.routes.v1.link_utils import build_list_links
from api.services.v1 import issuer_service

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.issuer import (
    IssuerCredentialStatusType,
    IssuerCredentialListResponse,
    IssuerCredentialListParameters,
    OfferNewCredentialPayload,
    OfferNewCredentialResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=IssuerCredentialListResponse
)
async def list_issuer_credentials(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    name: str | None = None,
    cred_def_id: str | None = None,
    credential_template_id: UUID | None = None,
    external_reference_id: str | None = None,
    status: IssuerCredentialStatusType | None = None,
    acapy: bool | None = None,
    deleted: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> IssuerCredentialListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = IssuerCredentialListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        name=name,
        deleted=deleted,
        cred_def_id=cred_def_id,
        credential_template_id=credential_template_id,
        external_reference_id=external_reference_id,
        status=status,
        acapy=acapy,
    )
    items, total_count = await issuer_service.list_issuer_credentials(
        db, tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return IssuerCredentialListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post("/", status_code=status.HTTP_200_OK)
async def offer_new_credential(
    payload: OfferNewCredentialPayload,
    background_tasks: BackgroundTasks,
    save_in_traction: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> OfferNewCredentialResponse:
    """Offer New Credential.

    This will create a new Issuer Credential record and kick off the offer/issuance
    process.

    The target Contact for this offer is set with either contact_id (Traction Contact
    ID) or connection_id (underlying AcaPy connection id for the contact).

    The Credential Template for this offer is set with either credential_template_id
    (Traction Credential Template ID) or cred_def_id (the underlying ledger id for the
    credential definition).

    save_in_traction: when True, store the credential data in Traction. Default is False
    """

    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.offer_new_credential(
        db, tenant_id, wallet_id, payload=payload, save_in_traction=save_in_traction
    )
    background_tasks.add_task(
        issuer_service.send_credential_offer_task,
        db=db,
        tenant_id=tenant_id,
        issuer_credential_id=item.issuer_credential_id,
    )
    links = []  # TODO

    return OfferNewCredentialResponse(item=item, links=links)
