import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field
from sqlalchemy import Column, func, text, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSON, ARRAY

from api.db.models.base import BaseModel


class Contact(BaseModel, table=True):

    contact_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)

    alias: str = Field(nullable=False, index=True)
    status: str = Field(nullable=False)

    ping_enabled: bool = Field(nullable=False, default=False)
    last_response_at: datetime = Field(nullable=True)

    external_reference_id: str = Field(nullable=True)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    contact_info: dict = Field(default={}, sa_column=Column(JSON))

    deleted: bool = Field(nullable=False, default=False)
    # acapy data ---
    connection_id: uuid.UUID = Field(nullable=False)
    connection_alias: str = Field(nullable=False)
    public_did: str = Field(nullable=True)
    role: str = Field(nullable=False, index=True)
    state: str = Field(nullable=False)
    connection: dict = Field(default={}, sa_column=Column(JSON))
    invitation: dict = Field(default={}, sa_column=Column(JSON))
    # --- acapy data

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


class ContactHistory(BaseModel, table=True):
    __tablename__ = "contact_history"

    contact_history_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)

    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
