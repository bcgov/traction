import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantWebhookConfig(BaseModel):
    acapy: bool = Field(default=False)


class TenantWebhookBase(BaseModel):
    webhook_url: str = Field(nullable=False)
    config: dict = Field(default={}, sa_column=Column(JSON))
    tenant_id: uuid.UUID = Field(nullable=False, foreign_key="tenant.id")


class TenantWebhook(TenantWebhookBase, BaseTable, table=True):
    # This is the class that represents the table
    webhook_key: str = Field(nullable=True)


class TenantWebhookCreate(TenantWebhookBase):
    webhook_key: Optional[str] = None
    config: Optional[TenantWebhookConfig] = None
    tenant_id: uuid.UUID


class TenantWebhookRead(TenantWebhookBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    config: Optional[TenantWebhookConfig] = None
    tenant_id: uuid.UUID


class TenantWebhookUpdate(BaseModel):
    id: uuid.UUID
    webhook_url: str
    webhook_key: Optional[str] = None
    config: Optional[TenantWebhookConfig] = None
