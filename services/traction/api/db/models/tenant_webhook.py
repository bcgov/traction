import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, TractionSQLModel


class TenantWebhookBase(BaseModel):
    wallet_id: uuid.UUID = Field(nullable=False)
    msg_id: uuid.UUID = Field(nullable=False)
    webhook_url: str = Field(nullable=False, default=False)
    payload: str = Field(nullable=False, default=False)
    # if the hook fails, record the response and the state as Failed
    state: str = Field(nullable=False, default=False)
    response_code: int = Field(nullable=True, default=False)
    response: str = Field(nullable=True, default=False)
    # if we re-send, create a new record and increment the sequence no
    sequence: int = Field(nullable=False, default=False)


class TenantWebhook(TenantWebhookBase, TractionSQLModel, table=True):
    # This is the class that represents the table
    # all fields from TractionSQLModel and TenantBase are inherited
    pass


class TenantWebhookCreate(TenantWebhookBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class TenantWebhookRead(TenantWebhookBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantWebhookUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from TenantWebhookBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    state: str = Field(nullable=False, default=False)
    response_code: int = Field(nullable=True, default=False)
    response: str = Field(nullable=True, default=False)
