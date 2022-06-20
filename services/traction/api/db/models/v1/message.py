"""(Basic) Message Tables/Models.

Models of the Traction tables for Messages (layer over AcaPy basic messaging).

"""
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship
from sqlalchemy import (
    Column,
    func,
    String,
    select,
    desc,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import BaseModel
from api.db.models.v1.contact import Contact

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class Message(BaseModel, table=True):
    """Message.

    Model for the Message table (postgresql specific dialects in use).
    This will track Messages for the Tenants (between contacts).

    Attributes:
      message_id: Traction ID for message OR when receiving, it is the AcaPy message_id
      tenant_id: Traction Tenant ID
      contact_id: Traction Contact ID
      status: Business and Tenant indicator for Credential state; independent of AcaPy
        Basic Message Exchange state
      role: sender or recipient
      deleted: Issuer Credential "soft" delete indicator.
      tags: Set by tenant for arbitrary grouping of Credentials
      content: actual content of the message
      state: The underlying AcaPy message exchange state
      sent_time: sent_time data in AcaPy payload
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    message_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    status: str = Field(nullable=False)
    role: str = Field(nullable=False)
    deleted: bool = Field(nullable=False, default=False)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    content: str = Field(nullable=True)

    # acapy data ---
    state: str = Field(nullable=False)
    sent_time: datetime = Field(sa_column=Column(TIMESTAMP, nullable=True))
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship(back_populates="messages")
    # --- relationships

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )

    @classmethod
    async def get_by_id(
        cls: "Message",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        message_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "Message":
        """Get Message by id.

        Find and return the database Message record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          message_id: Traction ID of Message

        Returns: The Traction Message (db) record

        Raises:
          NotFoundError: if the Message cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.message_id == message_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="message.id_not_found",
                title="Message does not exist",
                detail=f"Message does not exist for id<{message_id}>",
            )
        return db_rec

    @classmethod
    async def list_by_contact_id(
        cls: "Message",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> List["Message"]:
        """List by Contact ID.

        Find and return list of Message records for Contact.

          tenant_id: Traction ID of tenant making the call
          contact_id: Traction ID of Contact

        Returns: List of Traction Message (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.contact_id == contact_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_tenant_id(
        cls: "Message",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["Message"]:
        """List by Tenant ID.

        Find and return list of Message records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Message (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs
