import uuid
from datetime import datetime
from typing import Optional, List

import pydantic
from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class SchemaDef(pydantic.BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    version: Optional[str] = None
    attributes: Optional[List[str]] = []


class Governance(pydantic.BaseModel):
    schema_def: Optional[SchemaDef] = None
    cred_def_id: Optional[str] = None
    cred_def_tag: Optional[str] = None


class SandboxBase(BaseModel):
    tag: Optional[str] = Field(nullable=True)
    governance: dict = Field(default={}, sa_column=Column(JSON))


class Sandbox(SandboxBase, BaseTable, table=True):
    lobs: List["Lob"] = Relationship(back_populates="sandbox")  # noqa: F821
    students: List["Student"] = Relationship(back_populates="sandbox")  # noqa: F821
    applicants: List["Applicant"] = Relationship(back_populates="sandbox")  # noqa: F821


class SandboxCreate(SandboxBase):
    tag: Optional[str] = None
    governance: Optional[Governance] = None


class SandboxUpdate(SandboxBase):
    id: uuid.UUID
    tag: Optional[str] = None
    governance: Optional[Governance] = None


class SandboxRead(SandboxBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tag: Optional[str] = None
    governance: Optional[Governance] = None
