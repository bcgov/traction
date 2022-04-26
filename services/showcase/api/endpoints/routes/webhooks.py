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
from api.db.models import Lob
from api.endpoints.dependencies.db import get_db
from api.services.webhooks import handle_webhook

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_lob(lob_id, db):
    # we want data that should not be in LobRead (private wallet information)
    _q = select(Lob).where(Lob.id == lob_id)
    _rec = await db.execute(_q)
    lob = _rec.scalars().one_or_none()
    if not lob:
        raise DoesNotExist(f"{Lob.__name__}<id:{lob_id}> does not exist")
    return lob


api_key_header = APIKeyHeader(
    name=settings.TRACTION_WEBHOOK_URL_API_KEY_NAME, auto_error=False
)


async def get_api_key(
    api_key_header: str = Security(api_key_header),
):
    return api_key_header


@router.post("/webhook/{lob_id}", status_code=status.HTTP_202_ACCEPTED)
async def receive_webhook(
    lob_id: uuid.UUID,
    request: Request,
    api_key: APIKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    lob = await get_lob(lob_id, db)
    try:
        event_data = await request.json()
    except Exception:
        # could not parse json
        event_data = await request.body()

    # we expect a key in the header, so we should match see if that matches
    # in production LOB, we would not be using the wallet_key
    # it is just simpler to do so in this application.
    if not check_password(str(lob.wallet_key), api_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate webhook key",
        )

    topic = event_data["topic"]
    handled = await handle_webhook(lob, topic, event_data["payload"], db)

    return {"topic": topic, "handled": handled}
