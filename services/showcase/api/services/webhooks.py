import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Tenant

logger = logging.getLogger(__name__)


async def handle_issuer(tenant: Tenant, payload: dict, db: AsyncSession):
    logger.info(f"handle_issuer({payload})")
    return True


async def handle_schema(tenant: Tenant, payload: dict, db: AsyncSession):
    logger.info(f"handle_schema({payload})")
    return True


async def handle_webhook(tenant: Tenant, topic: str, payload: dict, db: AsyncSession):
    logger.info(f"handle_webhook(tenant = {tenant.name}, topic = {topic})")
    if "issuer" == topic:
        return await handle_issuer(tenant, payload, db)
    if "schema" == topic:
        return await handle_schema(tenant, payload, db)

    return False
