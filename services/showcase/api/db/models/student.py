import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class StudentBase(BaseModel):
    name: str = Field(index=True, nullable=False)


class Student(StudentBase, BaseTable, table=True):
    pass


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StudentUpdate(StudentBase):
    name: Optional[str] = None
