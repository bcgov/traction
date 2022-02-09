import uuid
from datetime import datetime
from typing import Optional, List

from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class SandboxBase(BaseModel):
    tag: Optional[str] = Field(nullable=True)


class Sandbox(SandboxBase, BaseTable, table=True):
    tenants: List["Tenant"] = Relationship(back_populates="sandbox")  # noqa: F821
    students: List["Student"] = Relationship(back_populates="sandbox")  # noqa: F821


class SandboxCreate(SandboxBase):
    tag: Optional[str] = None


class SandboxUpdate(SandboxBase):
    id: uuid.UUID
    tag: Optional[str] = None


class SandboxRead(SandboxBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tag: Optional[str] = None
