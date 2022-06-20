import logging
from uuid import UUID

from api.db.models.v1.tenant_configuration import TenantConfiguration
from api.db.models.v1.tenant_permissions import TenantPermissions
from api.db.session import async_session
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

    payload_dict = payload.dict(exclude_unset=True)
    # update it...
    await TenantConfiguration.update_by_id(tenant_id, payload_dict)

    return await get_tenant_configuration(tenant_id, wallet_id)


async def stored_message_content(tenant_id: UUID, content: str) -> str | None:
    async with async_session() as db:
        config = await TenantConfiguration.get_by_id(db, tenant_id)
        permissions = await TenantPermissions.get_by_id(db, tenant_id)
    logger.info(f"config = {config}")
    logger.info(f"permissions = {permissions}")
    logger.info(f"config store_messages= {config.store_messages}")
    logger.info(f"permissions store_messages= {permissions.store_messages}")
    if permissions.store_messages and config.store_messages:
        logger.info(f"returning {content}")
        return content

    return None
