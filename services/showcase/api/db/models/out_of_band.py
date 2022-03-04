import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class OutOfBandBase(BaseModel):
    msg_type: str = Field(nullable=False)
    msg: dict = Field(default={}, sa_column=Column(JSON))
    sender_id: uuid.UUID = None
    recipient_id: uuid.UUID = None
    sandbox_id: uuid.UUID = None
    action: Optional[str] = Field(nullable=True)


class OutOfBand(OutOfBandBase, BaseTable, table=True):
    __tablename__ = "out_of_band"

    # optional else, required on save
    sender_id: uuid.UUID = Field(foreign_key="line_of_business.id")
    recipient_id: uuid.UUID = Field(foreign_key="line_of_business.id")
    sandbox_id: uuid.UUID = Field(foreign_key="sandbox.id")

    # relationships
    sender: Optional["Lob"] = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "primaryjoin": "OutOfBand.sender_id==Lob.id",
            "lazy": "joined",
        }
    )
    recipient: Optional["Lob"] = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "primaryjoin": "OutOfBand.recipient_id==Lob.id",
            "lazy": "joined",
        }
    )

    class Config:
        arbitrary_types_allowed = True


class OutOfBandCreate(OutOfBandBase):
    pass


class OutOfBandRead(OutOfBandBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OutOfBandUpdate(OutOfBandBase):
    name: Optional[str] = None
    sender_id: Optional[uuid.UUID]
    recipient_id: Optional[uuid.UUID]
    sandbox_id: Optional[uuid.UUID]
