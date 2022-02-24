import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship
from pydantic_factories import ModelFactory, Use
from faker import Faker
from api.db.models.base import BaseModel, BaseTable


class StudentBase(BaseModel):
    name: str = Field(index=True, nullable=False)
    sandbox_id: Optional[uuid.UUID] = Field(default=None, foreign_key="sandbox.id")


class Student(StudentBase, BaseTable, table=True):
    sandbox: Optional["Sandbox"] = Relationship(back_populates="students")  # noqa: F821


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class StudentUpdate(StudentBase):
    name: Optional[str] = None


# FACTORIES


class StudentCreateFactory(ModelFactory):
    __model__ = StudentCreate

    name = Use(Faker().first_name)
