"""Contact Database Tables/Models.

Models of the Traction tables for Contacts and related data.

"""
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship
from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import (
    StatefulModel,
    TimestampModel,
    TrackingModel,
    TenantScopedModel,
)
from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class Contact(
    StatefulModel, TrackingModel, TimestampModel, TenantScopedModel, table=True
):
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
      connection_id: Underlying AcaPy connection id (found in connection)
      connection_alias: Underlying AcaPy connection alias (found in connection)
      invitation_key: Underlying AcaPy connection invitation_key (found in invitation)
      state: The underlying AcaPy connection state
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
    alias: str = Field(nullable=False, index=True)

    ping_enabled: bool = Field(nullable=False, default=False)
    last_response_at: datetime = Field(nullable=True)

    deleted: bool = Field(nullable=False, default=False)
    # acapy data ---
    connection_id: uuid.UUID = Field(nullable=False)
    connection_alias: str = Field(nullable=False)
    invitation_key: str = Field(nullable=False)
    public_did: str = Field(nullable=True)
    role: str = Field(nullable=False, index=True)
    # --- acapy data

    # relationships ---
    issuer_credentials: List["IssuerCredential"] = Relationship(  # noqa: F821
        back_populates="contact"
    )
    messages: List["Message"] = Relationship(back_populates="contact")  # noqa: F821
    # --- relationships

    @classmethod
    async def get_by_id(
        cls: "Contact",
        db: AsyncSession,
        tenant_id: UUID,
        contact_id: UUID,
        deleted: bool | None = False,
    ) -> "Contact":
        """Get Contact by ID.

        Find and return the database Contact record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          contact_id: Traction ID of Contact

        Returns: The Traction Contact (db) record

        Raises:
          NotFoundError: if the contact cannot be found by ID and deleted flag
        """

        q = (
            cls.tenant_select(fallback_tenant_id=tenant_id)
            .where(cls.contact_id == contact_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_contact = q_result.scalar_one_or_none()
        if not db_contact:
            raise NotFoundError(
                code="contact.id_not_found",
                title="Contact does not exist",
                detail=f"Contact does not exist for id<{contact_id}>",
            )
        return db_contact

    @classmethod
    async def get_by_connection_id(
        cls: "Contact",
        db: AsyncSession,
        tenant_id: UUID,
        connection_id: UUID,
        deleted: bool | None = False,
    ) -> "Contact":
        """Get Contact by Connection ID.

        Find and return the database Contact record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          connection_id: AcaPy Connection ID of Contact

        Returns: The Traction Contact (db) record

        Raises:
          NotFoundError: if the contact cannot be found by ID and deleted flag
        """

        q = (
            cls.tenant_select(fallback_tenant_id=tenant_id)
            .where(cls.connection_id == connection_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_contact = q_result.scalar_one_or_none()
        if not db_contact:
            raise NotFoundError(
                code="contact.id_not_found",
                title="Contact does not exist",
                detail=f"Contact does not exist for connection id<{connection_id}>",
            )
        return db_contact
