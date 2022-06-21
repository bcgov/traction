import logging
from uuid import UUID

from api.db.models.v1.tenant_configuration import TenantConfiguration
from api.db.models.v1.tenant_permissions import TenantPermissions
from api.db.session import async_session
from api.endpoints.models.v1.errors import StoragePermissionsError
from api.endpoints.models.v1.tenant import (
    TenantConfigurationItem,
    UpdateTenantConfigurationPayload,
)

logger = logging.getLogger(__name__)


def tenant_configuration_to_item(
    db_item: TenantConfiguration,
) -> TenantConfigurationItem:
    item = TenantConfigurationItem(**db_item.dict())
    return item


async def get_tenant_configuration(
    tenant_id: UUID,
    wallet_id: UUID,
) -> TenantConfigurationItem:

    async with async_session() as db:
        db_item = await TenantConfiguration.get_by_id(db, tenant_id)

    item = tenant_configuration_to_item(db_item)
    return item


async def update_tenant_configuration(
    tenant_id: UUID,
    wallet_id: UUID,
    payload: UpdateTenantConfigurationPayload,
) -> TenantConfiguration:

    async with async_session() as db:
        await TenantConfiguration.get_by_id(db, tenant_id)

    # do not allow enabling storage if innkeeper has not approved
    await check_storage_permissions(tenant_id, payload)
    # update set fields...
    payload_dict = payload.dict(exclude_unset=True)
    await TenantConfiguration.update_by_id(tenant_id, payload_dict)

    return await get_tenant_configuration(tenant_id, wallet_id)


async def stored_message_content(tenant_id: UUID, content: str) -> str | None:
    async with async_session() as db:
        config = await TenantConfiguration.get_by_id(db, tenant_id)
        permissions = await TenantPermissions.get_by_id(db, tenant_id)
    if permissions.store_messages and config.store_messages:
        return content

    return None


async def check_storage_permissions(
    tenant_id: UUID, payload: UpdateTenantConfigurationPayload
):
    async with async_session() as db:
        permissions = await TenantPermissions.get_by_id(db, tenant_id)

    error_fields = []

    if not permissions.store_messages and payload.store_messages:
        error_fields.append("store_messages")

    if not permissions.store_issuer_credentials and payload.store_issuer_credentials:
        error_fields.append("store_issuer_credentials")

    if len(error_fields) > 0:
        raise StoragePermissionsError(
            code="tenant_configuration.storage-not-enabled",
            title="Storage Configuration not enabled",
            detail=f"Innkeeper permission required before enabling storage flags {error_fields}.",  # noqa: E501
        )
