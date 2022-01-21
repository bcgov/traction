from turtle import update
from extensions import db
from sqlalchemy import asc, desc
from sqlalchemy.dialects.postgresql import UUID
from config import Config
from datetime import datetime

from sqlmodel import SQLModel,Field

#shared between pydantic and SQLAlchemy models
class TenantBase(SQLModel):
    name: str
    wallet_id: UUID
    created_at: datetime = Field(default_factory=db.func.now())
    updated_at: datetime = Field(default_factory=db.func.now(), update=db.func.now())

# SQLAlchemy Models, to be saved in DB
class Tenant(TenantBase, table=True):
    id : int = Field(default=None, primary_key=True)
    is_active: bool

# Pydantic Models, for everything else
class TenantCreate(TenantBase):
    pass