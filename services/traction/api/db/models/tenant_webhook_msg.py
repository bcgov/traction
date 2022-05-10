import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantWebhookMsgBase(BaseModel):
    msg_id: uuid.UUID = Field(nullable=False)
    payload: str = Field(nullable=False)
    # if the hook fails, record the response and the state as Failed
    state: str = Field(nullable=False)
    response_code: int = Field(nullable=True, default=None)
    response: str = Field(nullable=True, default=None)
    # if we re-send, create a new record and increment the sequence no
    sequence: int = Field(nullable=False, default=1)
    # alembic issue, this should not optional, but this is inherited and side-effects of
    # changing this is unknown
    tenant_id: Optional[uuid.UUID] = Field(default=None, foreign_key="tenant.id")


class TenantWebhookMsg(TenantWebhookMsgBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class TenantWebhookMsgCreate(TenantWebhookMsgBase):
    pass


class TenantWebhookMsgRead(TenantWebhookMsgBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantWebhookMsgUpdate(BaseModel):
    id: uuid.UUID
    state: str = Field(nullable=False, default=False)
    response_code: int = Field(nullable=True, default=False)
    response: str = Field(nullable=True, default=False)
