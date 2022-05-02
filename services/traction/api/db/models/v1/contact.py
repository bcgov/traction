"""Contact Database Tables/Models.

Models of the Traction tables for Contacts and related data.

"""
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field
from sqlalchemy import Column, func, text, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSON, ARRAY

from api.db.models.base import BaseModel


class Contact(BaseModel, table=True):
    """Contact.

    This is the model for the Contact table (postgresql specific dialects in use).
    Contacts belong to one and only one Tenant.

    Attributes:
      contact_id: Traction Contact ID
      tenant_id: Traction Tenant ID, owner of this Contact
      alias: Label or Name for the Contact, does not have to match the AcaPy Connection
        alias
      status: Business and Tenant indicator for Contact state; independent of AcaPy
        Connection state
      ping_enabled: Set to true to auto-ping the Contact
      last_response_at: Last time any interaction was made with this Contact;
        independent of ping enabled
      external_reference_id: Set by tenant to correlate this Contact with entity in
        external system
      tags: Set by tenant for arbitrary grouping of Contacts
      deleted: Contacts "soft" delete indicator.
      public_did: Represents the Contact's agent's Public DID (if any)
      role: Our role in relation to this Contact
      connection_id: Underlying AcaPy connection id
      connection_alias: Underlying AcaPy connection alias
      state: The underlying AcaPy connection state
      connection: Underlying AcaPy connection record
      invitation: Underlying AcaPy inviation record (if any)
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

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


class ContactTimeline(BaseModel, table=True):
    """Contact Timeline.

    Model for the Contact Timeline table (postgresql specific dialects in use).
    Timeline represents history of changes to status and/or state.

    Attributes:
      contact_timeline_id: Unique ID in table
      contact_id: Traction Contact ID
      status: Business and Tenant indicator for Contact state; independent of AcaPy
        Connection state
      state: The underlying AcaPy connection state
      created_at: Timestamp when record was created in Traction
    """

    __tablename__ = "contact_timeline"

    contact_timeline_id: uuid.UUID = Field(
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
