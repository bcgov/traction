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

    # faber line of business data for student degree credentials
    degree: Optional[str] = Field(default=None, nullable=True)
    age: Optional[int] = Field(default=None, nullable=True)
    student_id: Optional[str] = Field(default=None, nullable=True)
    date: Optional[datetime] = Field(default=None, nullable=True)

    # track invitation information
    # this is for this LOB to track this entity in Traction
    invitation_state: Optional[str] = Field(default=None, nullable=True)
    connection_id: Optional[uuid.UUID] = Field(default=None)

    # for matching this student with their traction tenant
    # this would not be in this LOB data at all!!!
    # the entity/person/business that this record represents
    # would be tracking this in their system/data
    wallet_id: Optional[uuid.UUID] = None
    alias: Optional[str] = Field(default=None, nullable=True)


class Student(StudentBase, BaseTable, table=True):
    __table_args__ = (UniqueConstraint("name", "sandbox_id"),)

    sandbox: Optional["Sandbox"] = Relationship(back_populates="students")  # noqa: F821

    sandbox_id: uuid.UUID = Field(foreign_key="sandbox.id")
    wallet_id: uuid.UUID = Field(default=None, nullable=True)


class StudentCreate(StudentBase):
    pass


class StudentRead(StudentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    degree: Optional[str] = None
    age: Optional[int] = None
    student_id: Optional[str] = None
    date: Optional[datetime] = None


class StudentUpdate(StudentBase):
    name: Optional[str] = None


# FACTORIES


class StudentCreateFactory(ModelFactory):
    __model__ = StudentCreate

    name = Use(Faker().name)
    degree = None
    age = None
    student_id = None
    date = None
    wallet_id = None
    alias = None
    invitation_state = None
    connection_id = None
