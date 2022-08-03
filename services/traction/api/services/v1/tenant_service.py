import logging
from uuid import UUID


from api.core.profile import Profile

from api.db.models.tenant import TenantRead
from api.db.models.v1.tenant_job import TenantJobType, TenantJob, TenantJobStatusType
from api.db.repositories.tenants import TenantsRepository
from api.db.session import async_session
from api.endpoints.models.v1.errors import (
    NotAnIssuerError,
    IncorrectStatusError,
)
from api.endpoints.models.v1.tenant import (
    TenantItem,
    IssuerStatus,
    PublicDIDStatus,
)
from api.jobs import MakeIssuerJob, EndorserConnectionJob, RegisterPublicDidJob

logger = logging.getLogger(__name__)


def tenant_job_status_to_issuer_status(tenant_job_issuer: TenantJob):
    issuer_status = IssuerStatus.none
    issuer = False
    if tenant_job_issuer.status == TenantJobStatusType.active:
        issuer = True
        issuer_status = IssuerStatus.active
    elif tenant_job_issuer.status == TenantJobStatusType.requested:
        issuer_status = IssuerStatus.requested
    elif tenant_job_issuer.status == TenantJobStatusType.approved:
        issuer_status = IssuerStatus.approved
    elif tenant_job_issuer.status == TenantJobStatusType.processing:
        issuer_status = IssuerStatus.processing
    elif tenant_job_issuer.status == TenantJobStatusType.denied:
        issuer_status = IssuerStatus.denied
    elif tenant_job_issuer.status == TenantJobStatusType.error:
        issuer_status = IssuerStatus.error
    return issuer_status, issuer


def tenant_job_status_to_did_status(tenant_job_did: TenantJob):
    public_did = None
    public_did_status = PublicDIDStatus.none
    if tenant_job_did.status == TenantJobStatusType.active:
        public_did_status = PublicDIDStatus.public
        public_did = tenant_job_did.data["did"]
    elif tenant_job_did.status == TenantJobStatusType.requested:
        public_did_status = PublicDIDStatus.requested
    elif tenant_job_did.status == TenantJobStatusType.approved:
        public_did_status = PublicDIDStatus.approved
    elif tenant_job_did.status == TenantJobStatusType.processing:
        public_did_status = PublicDIDStatus.processing
    elif tenant_job_did.status == TenantJobStatusType.denied:
        public_did_status = PublicDIDStatus.denied
    elif tenant_job_did.status == TenantJobStatusType.error:
        public_did_status = PublicDIDStatus.error
    return public_did_status, public_did


def issue_credentials_flow_to_tenant_fields(
    tenant_job_endorser: TenantJob,
    tenant_job_did: TenantJob,
    tenant_job_issuer: TenantJob,
):
    issuer_status, issuer = tenant_job_status_to_issuer_status(tenant_job_issuer)
    public_did_status, public_did = tenant_job_status_to_did_status(tenant_job_did)
    return issuer, issuer_status, public_did, public_did_status


def db_to_tenant_item(
    db_tenant: TenantRead,
    tenant_job_endorser: TenantJob,
    tenant_job_did: TenantJob,
    tenant_job_issuer: TenantJob,
) -> TenantItem:
    logger.info(db_tenant)

    result = TenantItem(
        tenant_id=db_tenant.id,
        wallet_id=db_tenant.wallet_id,
        created_at=db_tenant.created_at,
        updated_at=db_tenant.updated_at,
        name=db_tenant.name,
        deleted=not db_tenant.is_active,
        issuer=False,
        issuer_status=IssuerStatus.none,
        public_did=None,
        public_did_status=PublicDIDStatus.none,
    )

    (
        issuer,
        issuer_status,
        public_did,
        public_did_status,
    ) = issue_credentials_flow_to_tenant_fields(
        tenant_job_endorser, tenant_job_did, tenant_job_issuer
    )
    result.issuer = issuer
    result.issuer_status = issuer_status
    result.public_did = public_did
    result.public_did_status = public_did_status

    return result


async def get_tenant(
    tenant_id: UUID,
    wallet_id: UUID,
    deleted: bool | None = False,
) -> TenantItem:
    """Get Tenant.

    Find and return a Traction Tenant by ID.

    Args:
      tenant_id: Traction ID of tenant making the call
      deleted: When True, return Tenant if marked as deleted

    Returns: The Traction Tenant

    Raises:
      NotFoundError: if the Tenant cannot be found by ID and deleted flag
    """
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        db_tenant = await tenant_repo.get_by_id(tenant_id)
        tenant_job_issuer = await TenantJob.get_for_tenant(
            db, tenant_id, TenantJobType.issuer
        )
        tenant_job_did = await TenantJob.get_for_tenant(
            db, tenant_id, TenantJobType.public_did
        )
        tenant_job_endorser = await TenantJob.get_for_tenant(
            db, tenant_id, TenantJobType.endorser
        )

    item = db_to_tenant_item(
        db_tenant, tenant_job_endorser, tenant_job_did, tenant_job_issuer
    )

    return item


async def handle_make_issuer_job(
    tenant_id: UUID,
    wallet_id: UUID,
):
    async with async_session() as db:
        tenant_job_issuer = await TenantJob.get_for_tenant(
            db, tenant_id, TenantJobType.issuer
        )

    if tenant_job_issuer.status == TenantJobStatusType.default:
        # TODO: add proper back and forth flow for approval...
        # until we figure out the best flow, if the innkeeper has not approved
        # then we raise an error like before.
        raise IncorrectStatusError(
            code="tenant.issuer.innkeeper-not-approved",
            title="Tenant Issuer - Innkeeper not approved",
            detail="Innkeeper has to approve the Issuer process before tenant can make themselves an issuer.",  # noqa: E501
        )
    elif tenant_job_issuer.status == TenantJobStatusType.approved:
        # start the job and it's dependencies
        profile = Profile(tenant_id=tenant_id, wallet_id=wallet_id, db=None)
        job = MakeIssuerJob(profile)
        await job.start([EndorserConnectionJob, RegisterPublicDidJob])


async def make_issuer(
    tenant_id: UUID,
    wallet_id: UUID,
) -> TenantItem:
    # get the flows, if approved, then start processing...
    await handle_make_issuer_job(tenant_id, wallet_id)

    return await get_tenant(tenant_id, wallet_id)


async def is_issuer(
    tenant_id: UUID, wallet_id: UUID, raise_error: bool | None = False
) -> str:
    tenant = await get_tenant(tenant_id, wallet_id)
    public_did = tenant.public_did

    if raise_error and tenant.public_did_status is not PublicDIDStatus.public:
        raise NotAnIssuerError(
            code="tenant.issuer.not-allowed",
            title="Tenant is not an Issuer",
            detail="Tenant is not an Issuer and cannot write schemas or credential definitions to the ledger.",  # noqa: E501
            links=[],  # TODO: add link to make issuer
        )

    return public_did
