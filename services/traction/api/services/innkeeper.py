import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.tenant import Tenant, TenantRead
from api.services.v1.acapy_service import multitenancy_api

logger = logging.getLogger(__name__)


async def hard_delete_tenant(tenant: TenantRead, db: AsyncSession):
    q = select(Tenant).where(Tenant.id == tenant.id)
    result = await db.execute(q)
    db_tenant = result.scalar_one()
    if not db_tenant:
        raise Exception

    response = multitenancy_api.multitenancy_wallet_wallet_id_remove_post(
        str(db_tenant.wallet_id)
    )
    logger.warn(f"wallet_id = {db_tenant.wallet_id} has been hard deleted")

    # this is just to so we can reuse the name...
    db_tenant.name = f"(deleted {db_tenant.name})-{db_tenant.wallet_id}"
    db_tenant.is_active = False
    db.add(db_tenant)
    await db.commit()
    return response
