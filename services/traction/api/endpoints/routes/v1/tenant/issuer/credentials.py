import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.services.v1 import issuer_service

from api.db.models.v1.contact import Contact
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db


from api.endpoints.models.tenant_workflow import (
    TenantWorkflowStateType,
)

from api.endpoints.models.v1.issuer import (
    CredentialsListResponse,
    CredentialItem,
    GetCredentialResponse,
    IssueCredentialPayload,
    RevokeSchemaPayload,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=CredentialsListResponse)
async def get_issued_credentials(
    state: TenantWorkflowStateType | None = None,
    cred_issue_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> CredentialsListResponse:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    data = await issuer_service.get_issued_credentials(
        db, tenant_id, wallet_id, None, cred_issue_id, state
    )
    # TODO: v0 compatibility, service should do this after v0 is decommissioned
    resp_data = [
        CredentialItem(
            **d.__dict__,
            contact_id=d.credential.contact_id,
            credential_id=d.credential.id,
            status="v0",  # v0
            state=d.credential.issue_state,  # v0
            created_at=d.workflow.created_at,
            updated_at=d.workflow.updated_at,
        )
        for d in data
    ]

    response = CredentialsListResponse(
        items=resp_data, count=len(data), total=len(data)
    )

    return response


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=GetCredentialResponse
)
async def issue_new_credential(
    payload: IssueCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> GetCredentialResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    # Use connection ID for v0 compatability.
    contact = await Contact.get_by_id(
        db,
        tenant_id,
        contact_id=payload.contact_id,
        deleted=False,
    )
    data = await issuer_service.issue_new_credential(
        db,
        tenant_id,
        wallet_id,
        payload.cred_protocol,
        payload.credential,
        payload.cred_def_id,
        contact.connection_id,
        None,
    )
    # TODO: v0 compatibility, service should do this after v0 is decommissioned
    response = CredentialItem(
        **data.__dict__,
        credential_id=data.credential.id,
        status="v0",  # v0
        state=data.credential.issue_state,  # v0
        created_at=data.workflow.created_at,
        updated_at=data.workflow.updated_at,
        alias="v0",  # alias is none, CredentialItem won't allow none
        contact_id=payload.contact_id,  # v0
    )

    return response


@router.post(
    "/revoke",
    status_code=status.HTTP_201_CREATED,
    response_model=GetCredentialResponse,
)
async def revoke_issued_credential(
    payload: RevokeSchemaPayload,
    db: AsyncSession = Depends(get_db),
) -> GetCredentialResponse:
    """
    write a revocation entry to the revocation registry.
    And, if an active connection exists, notify the holder
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    return await issuer_service.revoke_issued_credential(
        db,
        tenant_id,
        wallet_id,
        payload.cred_issue_id,
        payload.rev_reg_id,
        payload.cred_rev_id,
        payload.comment,
    )
