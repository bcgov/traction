import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.services.v1 import issuer_service

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.issuer import (
    CredentialsListResponse,
    GetCredentialResponse,
    IssueCredentialPayload,
    RevokeSchemaPayload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=CredentialsListResponse)
async def list_issued_credentials(
    db: AsyncSession = Depends(get_db),
) -> CredentialsListResponse:
    # TODO: search and paging parameters...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    items, total_count = await issuer_service.list_issued_credentials(
        db, tenant_id, wallet_id
    )

    links = []  # TODO: set the paging links

    return CredentialsListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=GetCredentialResponse
)
async def issue_new_credential(
    payload: IssueCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> GetCredentialResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.issue_new_credential(db, tenant_id, wallet_id, payload)

    links = []  # TODO: set the links for issue new credential

    return GetCredentialResponse(item=item, links=links)


@router.post(
    "/<credential_id>/revoke",
    status_code=status.HTTP_201_CREATED,
    response_model=GetCredentialResponse,
)
async def revoke_issued_credential(
    credential_id: UUID,
    payload: RevokeSchemaPayload,
    db: AsyncSession = Depends(get_db),
) -> GetCredentialResponse:
    """
    write a revocation entry to the revocation registry.
    And, if an active connection exists, notify the holder
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.revoke_issued_credential(
        db,
        tenant_id,
        wallet_id,
        credential_id,
        payload,
    )

    links = []  # TODO: set the links for revoke credential

    return GetCredentialResponse(item=item, links=links)
