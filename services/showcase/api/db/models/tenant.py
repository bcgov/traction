import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class TenantBase(BaseModel):
    name: str = Field(nullable=False)
    webhook_url: Optional[str] = Field(nullable=True)
    sandbox_id: Optional[uuid.UUID] = Field(default=None, foreign_key="sandbox.id")


class Tenant(TenantBase, BaseTable, table=True):
    wallet_id: uuid.UUID = Field(default=None, nullable=False)
    wallet_key: uuid.UUID = Field(default=None, nullable=False)
    sandbox: Optional["Sandbox"] = Relationship(back_populates="tenants")  # noqa: F821


class TenantCreate(TenantBase):
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID


class TenantUpdate(TenantBase):
    id: uuid.UUID
    name: Optional[str] = None
    webhook_url: Optional[str] = None


class TenantRead(TenantBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    webhook_url: Optional[str] = None
    name: str
    # including these for now
    # only to simplify testing
    # TODO: remove these from READ!
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID
