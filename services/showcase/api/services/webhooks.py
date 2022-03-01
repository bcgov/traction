import logging
import random

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Tenant
from api.db.models.tenant import TenantUpdate
from api.db.repositories import TenantRepository
from api.services import traction

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

        # TODO: remove this, only for one-time demo
        # now that we are an issuer, let's create a schema/creddefn
        version = format(
            "%d.%d.%d"
            % (
                random.randint(1, 101),
                random.randint(1, 101),
                random.randint(1, 101),
            )
        )
        schema = {
            "schema_name": "degree schema",
            "schema_version": version,
            "attributes": ["student_id", "name", "date", "degree", "age"],
        }
        tag = f"degree_{version}"
        resp = await traction.tenant_create_schema(
            wallet_id=tenant.wallet_id,
            wallet_key=tenant.wallet_key,
            schema=schema,
            cred_def_tag=tag,
        )
        logger.info(f"create schema/cred def resp={resp}")
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

        # from here you could now issue a credential
        # using the above example  (degree schema)
        # and the cred_def_id...
        #
        # conns = await traction.get_connections(
        #     wallet_id=tenant.wallet_id, wallet_key=tenant.wallet_key, alias="Alice"
        # )
        # logger.info(conns)
        # if conns and len(conns) == 1:
        #     alice = conns[0]
        #     logger.info(alice)
        #     attrs = [
        #         {"name": "student_id", "value": "AS1234567"},
        #         {"name": "name", "value": "Alice Smith"},
        #         {"name": "date", "value": "2022-02-28"},
        #         {"name": "degree", "value": "Maths"},
        #         {"name": "age", "value": "24"}
        #     ]
        #     credential = await traction.tenant_issue_credential(
        #         wallet_id=tenant.wallet_id,
        #         wallet_key=tenant.wallet_key,
        #         connection_id=alice["connection_id"],
        #         alias=alice["alias"],
        #         cred_def_id=payload["cred_def_id"],
        #         attributes=attrs,
        #     )
        # logger.info(credential)
    return True


async def handle_webhook(tenant: Tenant, topic: str, payload: dict, db: AsyncSession):
    logger.info(f"handle_webhook(tenant = {tenant.name}, topic = {topic})")
    if "issuer" == topic:
        return await handle_issuer(tenant, payload, db)
    if "schema" == topic:
        return await handle_schema(tenant, payload, db)

    return False
