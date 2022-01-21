from sqlalchemy import asc, desc
from uuid import UUID
from sqlalchemy.dialects.postgresql import UUID as SA_UUID
from sqlalchemy import UniqueConstraint, Column, String, DateTime, text
from datetime import datetime

from sqlmodel import SQLModel,Field

#shared between pydantic and SQLAlchemy models
class TenantBase(SQLModel):
    name: str
    wallet_id: UUID
    created_at: datetime = Field(default_factory=datetime.now())
    #sqlmodel.Field() doesn't have auto-update columns yet.
    updated_at: datetime = Field(sa_column=Column(
        DateTime(),
        nullable=False,
        default=datetime.now(),
        onupdate=datetime.now()
    ))

# SQLAlchemy Models, to be saved in DB
class Tenant(TenantBase, table=True):
    id : UUID = Field(sa_column=Column(SA_UUID(as_uuid=True),
        server_default=text("public.gen_random_uuid()"),
        primary_key=True,
    ))
    is_active: bool

# Pydantic Models, for everything else
class TenantCreate(TenantBase):
    pass