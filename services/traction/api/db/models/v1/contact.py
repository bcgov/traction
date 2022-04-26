import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field
from sqlalchemy import Column, func, text, String
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSON, ARRAY

from api.db.models.base import BaseModel


class Contact(BaseModel, table=True):
    """Contact represents a person or organization we can interact with.
    In Traction, this is a wrapper around AcaPy connections. Contacts belong to a single Traction tenant.  # noqa: E501

    :param contact_id: Traction Contact ID
    :type uuid
    :param tenant_id: Traction Tenant ID, owner of this Contact
    :type uuid
    :param alias: A human readable label or name for the Contact, does not have to match the AcaPy Connection alias  # noqa: E501
    :type str
    :param status: Business and Tenant indicator for Contact state; independent of AcaPy Connection state  # noqa: E501
    :type str: api.endpoints.models.v1.contacts.ContactStatusType
    :param ping_enabled: Set to true to auto-ping the Contact
    :type bool
    :param last_response_at: Last time any interaction was made with this Contact; independent of ping enabled  # noqa: E501
    :type datetime
    :param external_reference_id: Set by tenant to correlate this Contact with entity in external system  # noqa: E501
    :type str
    :param tags: Set by tenant for arbitrary grouping of Contacts
    :type List[str]
    :param deleted: Contacts soft delete indicator.
    :type bool
    :param connection_id: Underlying AcaPy connection id
    :type uuid
    :param connection_alias: Underlying AcaPy connection alias
    :type str
    :param public_did: Represents the Contact's agent Public DID (if any)
    :type str
    :param role: Our role in relation to this Contact
    :type str: class:api.endpoints.models.connections.ConnectionRoleType
    :param state: The underlying AcaPy connection state
    :type str: class:api.endpoints.models.connections.ConnectionStateType
    :param connection: Underlying AcaPy connection record
    :type dict
    :param invitation: Underlying AcaPy inviation record (if any)
    :type dict
    :param created_at: Timestamp when Contact was created in Traction
    :type datetime
    :param updated_at: Timestamp when Contact was last modified in Traction
    :type datetime
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
    """Contact Timeline is a record of any change to a Contact's status or state.

    :param contact_timeline_id: Unique ID in table
    :type uuid
    :param contact_id: Traction Contact ID
    :type uuid
    :param status: Business and Tenant indicator for Contact state; independent of AcaPy Connection state  # noqa: E501
    :type str: api.endpoints.models.v1.contacts.ContactStatusType
    :param state: The underlying AcaPy connection state
    :type str: class:api.endpoints.models.connections.ConnectionStateType
    :param created_at: Timestamp when Contact Timeline was created in Traction (effectively time Contact status/state changed)  # noqa: E501
    :type datetime
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
