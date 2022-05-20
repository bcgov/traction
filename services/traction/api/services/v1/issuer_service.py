import logging
from uuid import UUID
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.v1.contact import Contact

from api.db.repositories.issue_credentials import IssueCredentialsRepository

from api.endpoints.models.v1.issuer import (
    CredentialItem,
    IssueCredentialPayload,
    RevokeSchemaPayload,
)

from api.services.v0.issuer_service import (
    get_issued_credentials as _v0_get_issued_credentials,
    issue_new_credential as _v0_issue_new_credential,
    revoke_issued_credential as _v0_revoke_issued_credential,
)

logger = logging.getLogger(__name__)


async def list_issued_credentials(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
) -> [List[CredentialItem], int]:
    # TODO: add parameters, query to get total count and return page data only
    # TODO v0 decomission and merge with natural endpoint
    data = await _v0_get_issued_credentials(db, tenant_id, wallet_id, None, None, None)
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

    return resp_data, len(resp_data)


async def issue_new_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    payload: IssueCredentialPayload,
) -> CredentialItem:

    contact = await Contact.get_by_id(
        db,
        tenant_id,
        contact_id=payload.contact_id,
        deleted=False,
    )
    # TODO v0 decomission and merge with natural endpoint
    data = await _v0_issue_new_credential(
        db,
        tenant_id,
        wallet_id,
        payload.cred_protocol,
        payload.credential,
        payload.cred_def_id,
        contact.connection_id,
        None,
    )

    return CredentialItem(
        **data.__dict__,
        credential_id=data.credential.id,
        status="v0",  # v0
        state=data.credential.issue_state,  # v0
        created_at=data.workflow.created_at,
        updated_at=data.workflow.updated_at,
        contact_id=payload.contact_id,  # v0
    )


async def revoke_issued_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    credential_id: UUID,
    payload: RevokeSchemaPayload,
) -> CredentialItem:
    issue_repo = IssueCredentialsRepository(db_session=db)
    cred = await issue_repo.get_by_id(credential_id)

    data = await _v0_revoke_issued_credential(
        db,
        tenant_id,
        wallet_id,
        credential_id,
        cred.rev_reg_id,
        cred.cred_rev_id,
        payload.comment,
    )

    return CredentialItem(
        **data.__dict__,
        credential_id=data.credential.id,
        status="v0",  # v0
        state=data.credential.issue_state,  # v0
        created_at=data.workflow.created_at,
        updated_at=data.workflow.updated_at,
        contact_id=cred.contact_id,  # v0
    )
