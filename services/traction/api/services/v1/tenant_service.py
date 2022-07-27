import logging
from uuid import UUID

from api.db.errors import DoesNotExist
from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenants import TenantsRepository
from api.db.session import async_session
from api.endpoints.models.tenant_workflow import TenantWorkflowTypeType
from api.endpoints.models.v1.admin import PublicDIDStateType
from api.endpoints.models.v1.errors import (
    IncorrectStatusError,
    NotAnIssuerError,
)
from api.endpoints.models.v1.tenant import (
    TenantItem,
    IssuerStatus,
    PublicDIDStatus,
)
from api.services.tenant_workflows import create_workflow
from api.tasks.public_did_task import RegisterPublicDIDTask

logger = logging.getLogger(__name__)


def tenant_issuer_to_tenant_fields(tenant_issuer: TenantIssuerRead):
    issuer = False
    issuer_status = IssuerStatus.none
    public_did = tenant_issuer.public_did
    public_did_status = PublicDIDStatus.none
    if PublicDIDStateType.public == tenant_issuer.public_did_state:
        issuer = True
        issuer_status = IssuerStatus.active
        public_did_status = PublicDIDStatus.public
    elif PublicDIDStateType.requested == tenant_issuer.public_did_state:
        issuer_status = IssuerStatus.requested
        public_did_status = PublicDIDStatus.requested
    elif PublicDIDStateType.endorsed == tenant_issuer.public_did_state:
        issuer_status = IssuerStatus.endorsed
        public_did_status = PublicDIDStatus.endorsed
    elif PublicDIDStateType.published == tenant_issuer.public_did_state:
        issuer_status = IssuerStatus.active
        public_did_status = PublicDIDStatus.published

    return issuer, issuer_status, public_did, public_did_status


def db_to_tenant_item(
    db_tenant: TenantRead, tenant_issuer: TenantIssuerRead | None = None
) -> TenantItem:
    logger.info(db_tenant)
    logger.info(tenant_issuer)
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

    if tenant_issuer:
        # for now, base this on the public did state
        # when we change up the workflow
        # (tenant can request public did, tenant requests issuer)
        # this will get simplified, right now mashup of v0 stuff...
        (
            issuer,
            issuer_status,
            public_did,
            public_did_status,
        ) = tenant_issuer_to_tenant_fields(tenant_issuer)
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
        tenant_issuer = None
        try:
            issuer_repo = TenantIssuersRepository(db_session=db)
            tenant_issuer = await issuer_repo.get_by_tenant_id(tenant_id)
        except DoesNotExist:
            # this is ok, they haven't started the v0 issuer process
            pass

    item = db_to_tenant_item(db_tenant, tenant_issuer)

    return item


async def make_issuer(
    tenant_id: UUID,
    wallet_id: UUID,
) -> TenantItem:
    async with async_session() as db:
        try:
            issuer_repo = TenantIssuersRepository(db_session=db)
            tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)
        except DoesNotExist:
            # raise an error, let caller know that innkeeper hasn't started the flow yet
            raise IncorrectStatusError(
                code="tenant.issuer.innkeeper-not-approved",
                title="Tenant Issuer - Innkeeper not approved",
                detail="Innkeeper has to approve the Issuer process before tenant can make themselves an issuer.",  # noqa: E501
            )

        # create workflow and update issuer record
        # await create_workflow(
        #     tenant_issuer.wallet_id,
        #     TenantWorkflowTypeType.issuer,
        #     db,
        # )

    await RegisterPublicDIDTask.assign(tenant_id, wallet_id, {})

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
