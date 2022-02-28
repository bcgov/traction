import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import UniqueConstraint

from sqlmodel import Field, Relationship
from pydantic_factories import ModelFactory, Use
from faker import Faker
from api.db.models.base import BaseModel, BaseTable


class StudentBase(BaseModel):
    name: str = Field(index=True, nullable=False)
    sandbox_id: uuid.UUID = None


class Student(StudentBase, BaseTable, table=True):
    __table_args__ = (UniqueConstraint("name", "sandbox_id"),)

    sandbox: Optional["Sandbox"] = Relationship(back_populates="students")  # noqa: F821

    # optional else, required on save
    sandbox_id: uuid.UUID = Field(foreign_key="sandbox.id")


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
