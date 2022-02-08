import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class SandboxBase(BaseModel):
    tag: Optional[str] = Field(nullable=True)


class Sandbox(SandboxBase, BaseTable, table=True):
    tenants: List["Tenant"] = Relationship(back_populates="sandbox")


# Because of the relationships, we put the child tables here (avoid circular imports)


class TenantBase(BaseModel):
    name: str = Field(nullable=False)
    webhook_url: Optional[str] = Field(nullable=True)
    sandbox_id: Optional[uuid.UUID] = Field(default=None, foreign_key="sandbox.id")


class Tenant(TenantBase, BaseTable, table=True):
    wallet_id: uuid.UUID = Field(default=None, nullable=False)
    wallet_key: uuid.UUID = Field(default=None, nullable=False)
    sandbox: Optional[Sandbox] = Relationship(back_populates="tenants")


# now let's list out the create and read resources, we can define what we want loaded
# in the parent/child relationships


class SandboxCreate(SandboxBase):
    tag: Optional[str] = None


class TenantCreate(TenantBase):
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID


class SandboxUpdate(SandboxBase):
    id: uuid.UUID
    tag: Optional[str] = None


class TenantUpdate(TenantBase):
    id: uuid.UUID
    webhook_url: Optional[str] = None


# the read classes are where we pay close attention to the relationships
# and data load


class SandboxRead(SandboxBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tag: Optional[str] = None


class TenantRead(TenantBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    webhook_url: Optional[str] = None
    name: str


class TenantReadWithSandbox(TenantRead):
    sandbox: SandboxRead = None


class SandboxReadWithTenants(SandboxRead):
    tenants: List[TenantRead] = None
