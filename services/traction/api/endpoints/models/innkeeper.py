from typing import Optional
from uuid import UUID

from api.db.models.base import BaseSchema


class CheckInRequest(BaseSchema):
    name: str
    webhook_url: Optional[str] = None


class CheckInResponse(BaseSchema):
    id: UUID
    name: str
    wallet_id: UUID
    wallet_key: UUID
    webhook_url: Optional[str] = None
