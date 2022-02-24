import json
import logging
import uuid

from fastapi import APIRouter, Depends, Security, HTTPException, Request
from fastapi.openapi.models import APIKey
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from starlette import status

from api.core.config import settings
from api.core.utils import check_password
from api.db.errors import DoesNotExist
from api.db.models import Tenant
from api.endpoints.dependencies.db import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_tenant(tenant_id, db):
    # we want data that should not be in TenantRead (private wallet information)
    tenant_q = select(Tenant).where(Tenant.id == tenant_id)
    tenant_rec = await db.execute(tenant_q)
    tenant = tenant_rec.scalars().one_or_none()
    if not tenant:
        raise DoesNotExist(f"{Tenant.__name__}<id:{tenant_id}> does not exist")
    return tenant


api_key_header = APIKeyHeader(
    name=settings.TRACTION_WEBHOOK_URL_API_KEY_NAME, auto_error=False
)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    return api_key_header


@router.post("/webhook/{tenant_id}", status_code=status.HTTP_200_OK)
async def receive_webhook(
    tenant_id: uuid.UUID,
    request: Request,
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    tenant = await get_tenant(tenant_id, db)
    try:
        # request.json() is supposed to be json, but returns str :(
        payload = json.loads(await request.json())
    except Exception:
        # could not parse json
        payload = await request.body()

    # we expect a key in the header, so we should match see if that matches
    # in production LOB, we would not be using the wallet_key
    # it is just simpler to do so in this application.
    if not check_password(str(tenant.wallet_key), api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate webhook key",
        )

    return {"message": f"got webhook for {tenant.name}", "payload": payload}
