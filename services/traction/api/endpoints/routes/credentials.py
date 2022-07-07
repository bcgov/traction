import logging
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


from api.api_client_utils import get_api_client
from api.db.errors import DoesNotExist
from api.db.models.issue_credential import (
    IssueCredentialUpdate,
)
from api.db.models.present_credential import (
    PresentCredentialRead,
    PresentCredentialUpdate,
)
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.issue_credentials import IssueCredentialsRepository
from api.db.repositories.present_credentials import PresentCredentialsRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository


from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.credentials import (
    CredentialRoleType,
    PresentationRoleType,
    CredPrecisForProof,
    CredPresentation,
)
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
    TenantWorkflowStateType,
)
from api.services.tenant_workflows import create_workflow
from api.services.base import BaseWorkflow

from acapy_client.api.credentials_api import CredentialsApi
from acapy_client.api.present_proof_v1_0_api import PresentProofV10Api
from acapy_client.api.revocation_api import RevocationApi
from api.services.v0.issuer_service import IssueCredentialData


router = APIRouter()
logger = logging.getLogger(__name__)

creds_api = CredentialsApi(api_client=get_api_client())
pres_cred_v10_api = PresentProofV10Api(api_client=get_api_client())
revoc_api = RevocationApi(api_client=get_api_client())


class PresentCredentialData(BaseModel):
    presentation: PresentCredentialRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.get("/holder/offer", response_model=List[IssueCredentialData])
async def holder_get_offer_credentials(
    state: TenantWorkflowStateType | None = None,
    workflow_id: str | None = None,
    cred_issue_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[IssueCredentialData]:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
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
            wallet_id, CredentialRoleType.holder
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


@router.post("/holder/accept_offer", response_model=IssueCredentialData)
async def holder_accept_credential(
    cred_issue_id: str,
    db: AsyncSession = Depends(get_db),
) -> IssueCredentialData:
    # holder has to accept a credential offer
    issue_repo = IssueCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    issue_cred = await issue_repo.get_by_id(cred_issue_id)
    if issue_cred.workflow_id:
        tenant_workflow = None
        if issue_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(issue_cred.workflow_id)
            except DoesNotExist:
                pass
        issue = IssueCredentialData(
            credential=issue_cred,
            workflow=tenant_workflow,
        )
        return issue

    tenant_workflow = await create_workflow(
        issue_cred.wallet_id,
        TenantWorkflowTypeType.issue_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    issue_update = IssueCredentialUpdate(
        id=issue_cred.id,
        workflow_id=tenant_workflow.id,
        cred_exch_id=issue_cred.cred_exch_id,
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


@router.post("/holder/reject_offer", response_model=IssueCredentialData)
async def holder_reject_credential(
    cred_issue_id: str,
    db: AsyncSession = Depends(get_db),
) -> IssueCredentialData:
    # holder has to accept a credential offer
    issue_repo = IssueCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    issue_cred = await issue_repo.get_by_id(cred_issue_id)
    if issue_cred.workflow_id:
        tenant_workflow = None
        if issue_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(issue_cred.workflow_id)
            except DoesNotExist:
                pass
        issue = IssueCredentialData(
            credential=issue_cred,
            workflow=tenant_workflow,
        )
        return issue

    tenant_workflow = await create_workflow(
        issue_cred.wallet_id,
        TenantWorkflowTypeType.issue_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    issue_update = IssueCredentialUpdate(
        id=issue_cred.id,
        workflow_id=tenant_workflow.id,
        cred_exch_id=issue_cred.cred_exch_id,
        issue_state=issue_cred.issue_state,
    )
    issue_cred = await issue_repo.update(issue_update)
    logger.debug(f">>> Updated issue_cred: {issue_cred}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db,
        tenant_workflow=tenant_workflow,
        with_error=True,
        with_error_msg="Credential rejected.",
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


@router.get("/holder/request", response_model=List[PresentCredentialData])
async def holder_get_presentation_requests(
    state: TenantWorkflowStateType | None = None,
    workflow_id: str | None = None,
    pres_req_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[PresentCredentialData]:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    present_repo = PresentCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    present_creds = []
    if workflow_id:
        present_cred = await present_repo.get_by_workflow_id(wallet_id, workflow_id)
        present_creds = [
            present_cred,
        ]
    elif pres_req_id:
        present_cred = await present_repo.get_by_id(pres_req_id)
        present_creds = [
            present_cred,
        ]
    else:
        present_creds = await present_repo.find_by_wallet_id_and_role(
            wallet_id, PresentationRoleType.holder
        )
    logger.warn(f">>> queued present_creds: {present_creds}")
    presentations = []
    for present_cred in present_creds:
        tenant_workflow = None
        if present_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(
                    present_cred.workflow_id
                )
            except DoesNotExist:
                pass
        if (
            (not state)
            or (not tenant_workflow and state == TenantWorkflowStateType.pending)
            or (tenant_workflow and state == tenant_workflow.workflow_state)
        ):
            present = PresentCredentialData(
                presentation=present_cred,
                workflow=tenant_workflow,
            )
            presentations.append(present)
    return presentations


@router.get("/holder/creds-for-request", response_model=List[CredPrecisForProof])
async def holder_get_creds_for_pres_request(
    pres_req_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[PresentCredentialData]:
    present_repo = PresentCredentialsRepository(db_session=db)
    present_cred = await present_repo.get_by_id(pres_req_id)
    creds = pres_cred_v10_api.present_proof_records_pres_ex_id_credentials_get(
        str(present_cred.pres_exch_id)
    )
    cred_precis = []
    for cred in creds:
        cred_precis.append(
            CredPrecisForProof(
                cred_info=cred.get("cred_info"),
                interval=cred.get("interval"),
                presentation_referents=cred.get("presentation_referents"),
            )
        )
    return cred_precis


@router.post("/holder/present-credential", response_model=PresentCredentialData)
async def holder_present_credential(
    pres_req_id: str,
    presentation: CredPresentation,
    db: AsyncSession = Depends(get_db),
) -> PresentCredentialData:
    # holder has to present their credential(s)
    present_repo = PresentCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    present_cred = await present_repo.get_by_id(pres_req_id)
    if present_cred.workflow_id:
        tenant_workflow = None
        if present_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(
                    present_cred.workflow_id
                )
            except DoesNotExist:
                pass
        present = PresentCredentialData(
            presentation=present_cred,
            workflow=tenant_workflow,
        )
        return present

    tenant_workflow = await create_workflow(
        present_cred.wallet_id,
        TenantWorkflowTypeType.present_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    present_update = PresentCredentialUpdate(
        id=present_cred.id,
        workflow_id=tenant_workflow.id,
        present_state=TenantWorkflowStateType.pending,
        pres_exch_id=present_cred.pres_exch_id,
        presentation=presentation.toJSON(),
    )
    present_cred = await present_repo.update(present_update)
    logger.debug(f">>> Updated present_cred: {present_cred}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db, tenant_workflow=tenant_workflow
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    present_cred = await present_repo.get_by_id(present_cred.id)
    logger.debug(f">>> Updated (final) present_cred: {present_cred}")

    present = PresentCredentialData(
        presentation=present_cred,
        workflow=tenant_workflow,
    )

    return present


@router.post("/holder/reject-request", response_model=PresentCredentialData)
async def holder_reject_presentation_request(
    pres_req_id: str,
    db: AsyncSession = Depends(get_db),
) -> PresentCredentialData:
    # holder has to present their credential(s)
    present_repo = PresentCredentialsRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    present_cred = await present_repo.get_by_id(pres_req_id)
    if present_cred.workflow_id:
        tenant_workflow = None
        if present_cred.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(
                    present_cred.workflow_id
                )
            except DoesNotExist:
                pass
        present = PresentCredentialData(
            presentation=present_cred,
            workflow=tenant_workflow,
        )
        return present

    tenant_workflow = await create_workflow(
        present_cred.wallet_id,
        TenantWorkflowTypeType.present_cred,
        db,
        error_if_wf_exists=False,
        start_workflow=False,
    )
    logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
    present_update = PresentCredentialUpdate(
        id=present_cred.id,
        workflow_id=tenant_workflow.id,
        present_state=TenantWorkflowStateType.pending,
        pres_exch_id=present_cred.pres_exch_id,
    )
    present_cred = await present_repo.update(present_update)
    logger.debug(f">>> Updated present_cred: {present_cred}")

    # start workflow
    tenant_workflow = await BaseWorkflow.next_workflow_step(
        db,
        tenant_workflow=tenant_workflow,
        with_error=True,
        with_error_msg="Credential request rejected.",
    )
    logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

    # get updated issuer info (should have workflow id etc.)
    present_cred = await present_repo.get_by_id(present_cred.id)
    logger.debug(f">>> Updated (final) present_cred: {present_cred}")

    present = PresentCredentialData(
        presentation=present_cred,
        workflow=tenant_workflow,
    )

    return present


@router.get("/holder/", response_model=List[dict])
async def holder_get_credentials(db: AsyncSession = Depends(get_db)) -> List[dict]:
    cred_results = creds_api.credentials_get()
    creds = []
    for cred in cred_results.results:
        credential = {
            "attrs": cred.attrs,
            "cred_def_id": cred.cred_def_id,
            "cred_rev_id": cred.cred_rev_id,
            "referent": cred.referent,
            "rev_reg_id": cred.rev_reg_id,
            "schema_id": cred.schema_id,
        }
        creds.append(credential)

    return creds
