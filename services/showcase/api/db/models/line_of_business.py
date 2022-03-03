import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship

from api.db.models.base import BaseModel, BaseTable


class LobBase(BaseModel):
    name: str = Field(nullable=False)
    webhook_url: Optional[str] = Field(nullable=True)
    sandbox_id: Optional[uuid.UUID] = None

    traction_issue_enabled: Optional[bool] = Field(nullable=False)
    public_did: Optional[str] = Field(nullable=True)
    cred_def_id: Optional[str] = Field(nullable=True)


class Lob(LobBase, BaseTable, table=True):
    __tablename__ = "line_of_business"

    wallet_id: uuid.UUID = Field(default=None, nullable=False)
    wallet_key: uuid.UUID = Field(default=None, nullable=False)
    sandbox: Optional["Sandbox"] = Relationship(back_populates="lobs")  # noqa: F821

    # optional else, required on save
    sandbox_id: uuid.UUID = Field(foreign_key="sandbox.id")


class LobCreate(LobBase):
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID


class LobUpdate(LobBase):
    id: uuid.UUID
    name: Optional[str] = None
    webhook_url: Optional[str] = None


class LobRead(LobBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    webhook_url: Optional[str] = None
    name: str
    # including these for now
    # only to simplify testing
    # TODO: remove these from READ!
    wallet_id: uuid.UUID
    wallet_key: uuid.UUID
