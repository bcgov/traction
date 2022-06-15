from uuid import UUID

from api.db.models.v1.tenant_permissions import TenantPermissions
from api.db.session import async_session
from api.endpoints.models.v1.errors import IdNotMatchError
from api.endpoints.models.v1.tenant import (
    TenantPermissionsItem,
    UpdateTenantPermissionsPayload,
)


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

    payload_dict = payload.dict()
    # payload isn't the same as the db... move fields around
    del payload_dict["tenant_id"]
    # update it...
    await TenantPermissions.update_by_id(tenant_id, payload_dict)

    return await get_tenant_permissions(tenant_id)
