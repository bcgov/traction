import logging
from uuid import UUID
from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel


from api.api_client_utils import get_api_client

from api.endpoints.dependencies.tenant_security import get_from_context
from api.services.tenant_workflows import create_workflow

from api.db.errors import DoesNotExist
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository

from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
)
from api.db.models.issue_credential import (
    IssueCredentialCreate,
    IssueCredentialRead,
    IssueCredentialUpdate,
)
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.endpoints.models.credentials import (
    IssueCredentialProtocolType,
    CredentialType,
    CredentialStateType,
    CredentialRoleType,
    CredentialPreview,
)
from acapy_client.model.revoke_request import RevokeRequest
from acapy_client.api.revocation_api import RevocationApi
from api.services.connections import (
    get_connection_with_alias,
)
from api.services.base import BaseWorkflow
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
    TenantWorkflowStateType,
)

logger = logging.getLogger(__name__)
revoc_api = RevocationApi(api_client=get_api_client())


class IssueCredentialData(BaseModel):
    credential: IssueCredentialRead | None = None
    workflow: TenantWorkflowRead | None = None


async def get_issued_credentials(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    workflow_id: UUID,
    cred_issue_id: UUID,
    state: TenantWorkflowStateType | None = None,
) -> List[IssueCredentialData]:
    issue_repo = IssueCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    issue_creds = []
    if workflow_id:
        issue_cred = await issue_repo.get_by_workflow_id(wallet_id, workflow_id)
        issue_creds = [
            issue_cred,
        ]
    elif cred_issue_id:
        issue_cred = await issue_repo.get_by_id(cred_issue_id)
        issue_creds = [
            issue_cred,
        ]
    else:
        issue_creds = await issue_repo.find_by_wallet_id_and_role(
            wallet_id, CredentialRoleType.issuer
        )
    issues = []
    for issue_cred in issue_creds:
        tenant_workflow = None
        if issue_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(issue_cred.workflow_id)
            except DoesNotExist:
                pass
        if (
            (not state)
            or (not tenant_workflow and state == TenantWorkflowStateType.pending)
            or (tenant_workflow and state == tenant_workflow.workflow_state)
        ):
            issue = IssueCredentialData(
                credential=issue_cred,
                workflow=tenant_workflow,
            )
            issues.append(issue)

    return issues


async def issue_new_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    cred_protocol: IssueCredentialProtocolType,
    credential: CredentialPreview,
    cred_def_id: str | None = None,
    connection_id: str | None = None,
    alias: str | None = None,
):
    if not connection_id:
        existing_connection = get_connection_with_alias(alias)
        if not existing_connection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Error alias {alias} does not exist",
            )
        connection_id = existing_connection.connection_id

    if cred_protocol == IssueCredentialProtocolType.v20:
        raise NotImplementedError()  # TODO
    cred_type = CredentialType.anoncreds

    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    issue_repo = IssueCredentialsRepository(db_session=db)

    issue_cred = IssueCredentialCreate(
        tenant_id=tenant_id,
        wallet_id=wallet_id,
        connection_id=connection_id,
        cred_type=cred_type,
        cred_protocol=cred_protocol,
        cred_def_id=cred_def_id,
        credential=credential.toJSON(),
        issue_role=CredentialRoleType.issuer,
        issue_state=CredentialStateType.pending,
    )
    issue_cred = await issue_repo.create(issue_cred)

    tenant_workflow = await create_workflow(
        wallet_id,
        TenantWorkflowTypeType.issue_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    issue_update = IssueCredentialUpdate(
        id=issue_cred.id,
        workflow_id=tenant_workflow.id,
        issue_state=issue_cred.issue_state,
    )
    issue_cred = await issue_repo.update(issue_update)
    logger.debug(f">>> Updated issue_cred: {issue_cred}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db, tenant_workflow=tenant_workflow
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    issue_cred = await issue_repo.get_by_id(issue_cred.id)
    logger.debug(f">>> Updated (final) issue_cred: {issue_cred}")

    issue = IssueCredentialData(
        credential=issue_cred,
        workflow=tenant_workflow,
    )

    return issue


async def revoke_issued_credential(
    db: AsyncSession,
    tenant_id: UUID,
    wallet_id: UUID,
    cred_issue_id: UUID,
    rev_reg_id: UUID,
    cred_rev_id: UUID,
    comment: str,
):
    issue_repo = IssueCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    issue_cred = None
    if cred_issue_id:
        issue_cred = await issue_repo.get_by_id(cred_issue_id)
    else:
        issue_cred = await issue_repo.get_by_cred_rev_reg_id(
            wallet_id, rev_reg_id, cred_rev_id
        )
    if not (
        issue_cred.issue_state == CredentialStateType.done
        or issue_cred.issue_state == CredentialStateType.credential_acked
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot revoke, credential is in state {issue_cred.issue_state}.",
        )

    # no fancy workflow stuff, just revoke
    rev_req = RevokeRequest(
        comment=comment if comment else "",
        connection_id=str(issue_cred.connection_id),
        rev_reg_id=issue_cred.rev_reg_id,
        cred_rev_id=issue_cred.cred_rev_id,
        publish=True,
        notify=True,
    )
    data = {"body": rev_req}
    revoc_api.revocation_revoke_post(**data)

    update_issue = IssueCredentialUpdate(
        id=issue_cred.id,
        workflow_id=issue_cred.workflow_id,
        cred_exch_id=issue_cred.cred_exch_id,
        issue_state=CredentialStateType.credential_revoked,
    )
    issue_cred = await issue_repo.update(update_issue)
    tenant_workflow = await workflow_repo.get_by_id(issue_cred.workflow_id)

    issue = IssueCredentialData(
        credential=issue_cred,
        workflow=tenant_workflow,
    )
