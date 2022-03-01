import logging

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Tenant
from api.db.models.tenant import TenantUpdate
from api.db.repositories import TenantRepository

logger = logging.getLogger(__name__)


async def handle_issuer(tenant: Tenant, payload: dict, db: AsyncSession):
    logger.info(f"handle_issuer({payload})")
    # {
    # 'status': 'completed',
    # 'public_did': 'MS614YmscauME1eqjFCioa',
    # 'public_did_state': 'public'
    # }
    if payload["status"] == "completed" and payload["public_did_state"] == "public":
        repo = TenantRepository(db_session=db)
        tenant.issuer_enabled = True
        upd = TenantUpdate(**tenant.dict())
        await repo.update(upd)

    return True


async def handle_schema(tenant: Tenant, payload: dict, db: AsyncSession):
    logger.info(f"handle_schema({payload})")
    # {
    # 'status': 'completed',
    # 'schema_id': 'MS614YmscauME1eqjFCioa:2:sherman_002:0.0.2',
    # 'cred_def_id': 'MS614YmscauME1eqjFCioa:3:CL:160656:demo_002',
    # 'cred_def_state': 'completed',
    # 'cred_def_tag': 'demo_002'
    # }
    if payload["status"] == "completed":
        repo = TenantRepository(db_session=db)
        tenant.issuer_schema_success = payload["schema_id"] is not None
        tenant.issuer_cred_def_success = payload["cred_def_state"] == "completed"
        upd = TenantUpdate(
            **tenant.dict(),
        )
        await repo.update(upd)
    return True


async def handle_webhook(tenant: Tenant, topic: str, payload: dict, db: AsyncSession):
    logger.info(f"handle_webhook(tenant = {tenant.name}, topic = {topic})")
    if "issuer" == topic:
        return await handle_issuer(tenant, payload, db)
    if "schema" == topic:
        return await handle_schema(tenant, payload, db)

    return False
