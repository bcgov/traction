import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantBase(BaseModel):
    __table_args__ = (UniqueConstraint("name"), UniqueConstraint("wallet_id"))

    name: str = Field(index=True, nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    is_active: bool = Field(nullable=False, default=False)
    wallet_token: Optional[str] = Field(nullable=True)


class Tenant(TenantBase, BaseTable, table=True):
    # This is the class that represents the table
    # this will have id, created_at, updated_at from BaseTable
    # and fields from TenantBase
    # this should fully represent the table
    pass


class TenantCreate(TenantBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    pass


class TenantRead(TenantBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from TenantBase,
    # so no need to worry about accidentally updating id or other fields
    name: Optional[str] = None
    is_active: Optional[bool] = None
