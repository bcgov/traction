import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantWebhookBase(BaseModel):
    wallet_id: uuid.UUID = Field(nullable=False)
    msg_id: uuid.UUID = Field(nullable=False)
    webhook_url: str = Field(nullable=False)
    payload: str = Field(nullable=False)
    # if the hook fails, record the response and the state as Failed
    state: str = Field(nullable=False)
    response_code: int = Field(nullable=True, default=None)
    response: str = Field(nullable=True, default=None)
    # if we re-send, create a new record and increment the sequence no
    sequence: int = Field(nullable=False, default=1)


class TenantWebhook(TenantWebhookBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class TenantWebhookCreate(TenantWebhookBase):
    pass


class TenantWebhookRead(TenantWebhookBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantWebhookUpdate(BaseModel):
    id: uuid.UUID
    state: str = Field(nullable=False, default=False)
    response_code: int = Field(nullable=True, default=False)
    response: str = Field(nullable=True, default=False)
