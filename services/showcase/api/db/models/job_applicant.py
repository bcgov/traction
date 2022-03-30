import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import UniqueConstraint

from sqlmodel import Field, Relationship
from pydantic_factories import ModelFactory, Use
from faker import Faker
from api.db.models.base import BaseModel, BaseTable


class ApplicantBase(BaseModel):
    name: str = Field(index=True, nullable=False)
    sandbox_id: uuid.UUID = None

    # acme line of business data, store results of presentation request
    # just want their degree and date of degree
    degree: Optional[str] = Field(default=None, nullable=True)
    date: Optional[datetime] = Field(default=None, nullable=True)
    verified: Optional[str] = Field(default=None, nullable=True)

    # track invitation information
    # this is for this LOB to track this entity in Traction
    invitation_state: Optional[str] = Field(default=None, nullable=True)
    connection_id: Optional[uuid.UUID] = Field(default=None)

    # for matching this applicant with their traction tenant
    # this would not be in this LOB data at all!!!
    # the entity/person/business that this record represents
    # would be tracking this in their system/data
    wallet_id: Optional[uuid.UUID] = None
    alias: Optional[str] = Field(default=None, nullable=True)


class Applicant(ApplicantBase, BaseTable, table=True):
    __tablename__ = "job_applicant"
    __table_args__ = (UniqueConstraint("name", "sandbox_id"),)

    sandbox: Optional["Sandbox"] = Relationship(  # noqa: F821
        back_populates="applicants"
    )

    sandbox_id: uuid.UUID = Field(foreign_key="sandbox.id")
    wallet_id: uuid.UUID = Field(default=None, nullable=True)


class ApplicantCreate(ApplicantBase):
    pass


class ApplicantRead(ApplicantBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    degree: Optional[str] = None
    date: Optional[datetime] = None
    verified: Optional[str] = None


class ApplicantUpdate(ApplicantBase):
    name: Optional[str] = None


# FACTORIES


class ApplicantCreateFactory(ModelFactory):
    __model__ = ApplicantCreate

    name = Use(Faker().name)
    degree = None
    verified = True
    date = None
    wallet_id = None
    alias = None
    invitation_state = None
    connection_id = None
