import uuid
from uuid import UUID

from api.core.config import settings
from api.db.errors import AlreadyExists, DoesNotExist
from api.db.models import Tenant
from api.db.models.tenant_issuer import TenantIssuerCreate
from api.db.models.v1.tenant_permissions import TenantPermissions
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenants import TenantsRepository
from api.db.session import async_session
from api.endpoints.models.v1.errors import IdNotMatchError
from api.endpoints.models.v1.innkeeper import (
    TenantPermissionsItem,
    UpdateTenantPermissionsPayload,
    CheckInItem,
    CheckInPayload,
)

from acapy_client.api.multitenancy_api import MultitenancyApi
from acapy_client.model.create_wallet_request import CreateWalletRequest

from api.api_client_utils import get_api_client
from api.endpoints.models.v1.tenant import TenantItem
from api.services.v1 import tenant_service

multitenancy_api = MultitenancyApi(api_client=get_api_client())


def tenant_permissions_to_item(db_item: TenantPermissions) -> TenantPermissionsItem:
    item = TenantPermissionsItem(**db_item.dict())
    return item


async def get_tenant_permissions(
    tenant_id: UUID,
) -> TenantPermissionsItem:

    async with async_session() as db:
        db_item = await TenantPermissions.get_by_id(db, tenant_id)

    item = tenant_permissions_to_item(db_item)
    return item


async def update_tenant_permissions(
    tenant_id: UUID,
    payload: UpdateTenantPermissionsPayload,
) -> TenantPermissionsItem:

    async with async_session() as db:
        await TenantPermissions.get_by_id(db, tenant_id)

    # payload tenant id must match parameter
    if tenant_id != payload.tenant_id:
        raise IdNotMatchError(
            code="tenant_permissions.update.id-not-match",
            title="Tenant Permissions ID mismatch",
            detail=f"Tenant ID in payload <{payload.tenant_id}> does not match Tenant ID requested <{tenant_id}>",  # noqa: E501
        )

    payload_dict = payload.dict(exclude_unset=True)
    # payload isn't the same as the db... move fields around
    del payload_dict["tenant_id"]
    # update it...
    await TenantPermissions.update_by_id(tenant_id, payload_dict)

    return await get_tenant_permissions(tenant_id)


async def check_in_tenant(payload: CheckInPayload) -> CheckInItem:
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        existing = await tenant_repo.get_by_name(payload.name)

    if existing:
        raise AlreadyExists(f"Tenant already exists with name '{existing.name}'")

    # Call ACAPY
    wallet_key = str(uuid.uuid4())
    wallet_name = str(uuid.uuid4())
    webhook_url = settings.TRACTION_TENANT_WEBHOOK_URL
    if settings.ACAPY_WEBHOOK_URL_API_KEY and 0 < len(
        settings.ACAPY_WEBHOOK_URL_API_KEY
    ):
        webhook_url = f"{webhook_url}#{settings.ACAPY_WEBHOOK_URL_API_KEY}"
        data = {
            "label": payload.name,
            "wallet_key": wallet_key,
            "wallet_name": wallet_name,
            "wallet_type": "indy",
            "wallet_dispatch_type": "default",
            "wallet_webhook_urls": [
                webhook_url,
            ],
        }
        wallet_request = CreateWalletRequest(**data)
        wallet_response = multitenancy_api.multitenancy_wallet_post(
            **{"body": wallet_request}
        )
        if wallet_response:
            # save acapy generated wallet_id
            wallet_id = wallet_response.wallet_id
            tenant = Tenant(
                **payload.dict(),
                is_active=True,
                wallet_id=wallet_id,
            )
            async with async_session() as db:
                db.add(tenant)
                await db.commit()

            return CheckInItem(
                id=tenant.id,
                name=tenant.name,
                wallet_id=tenant.wallet_id,
                wallet_key=wallet_key,
            )
        else:
            # what to return or throw here?
            return
    else:
        # improperly configured... what to return or throw here?
        return


async def make_issuer(tenant_id: UUID) -> TenantItem:
    # lets update their permissions so they can act like an issuer
    perms = UpdateTenantPermissionsPayload(
        tenant_id=tenant_id,
        endorser_approval=True,
        create_schema_templates=True,
        create_credential_templates=True,
        issue_credentials=True,
    )
    await update_tenant_permissions(tenant_id, perms)

    # now we need to kick off the public did process
    # TODO: update the public did process!!

    # kick off the process of promoting this tenant to "issuer"
    # TODO: remove all this v0 code
    async with async_session() as db:
        tenant_repo = TenantsRepository(db_session=db)
        tenant = await tenant_repo.get_by_id(tenant_id)
    try:
        async with async_session() as db:
            issuer_repo = TenantIssuersRepository(db_session=db)
            await issuer_repo.get_by_wallet_id(tenant.wallet_id)
    except DoesNotExist:
        new_issuer = TenantIssuerCreate(
            tenant_id=tenant.id,
            wallet_id=tenant.wallet_id,
        )
        await issuer_repo.create(new_issuer)

    issuer = await tenant_service.get_tenant(tenant_id, tenant.wallet_id)
    return issuer
