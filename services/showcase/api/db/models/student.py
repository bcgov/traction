import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field

from api.db.models.base import BaseModel, TractionSQLModel


class StudentBase(BaseModel):
    name: str = Field(index=True, nullable=False)


class Student(StudentBase, TractionSQLModel, table=True):
    # This is the class that represents the table
    # all fields from TractionSQLModel and TenantBase are inherited
    pass


class StudentCreate(StudentBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class StudentRead(StudentBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StudentUpdate(StudentBase):
    # This is our update interface
    # This does NOT inherit from TenantBase,
    # so no need to worry about accidentally updating id or other fields
    name: Optional[str] = None
