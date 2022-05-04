"""Contact Database Tables/Models.

Models of the Traction tables for Contacts and related data.

"""
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field
from sqlalchemy import Column, func, text, String, select
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSON, ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import BaseModel

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class Invitation(BaseModel, table=True):
    """Invitation.

    This is the model for the Invitation table (postgresql specific dialects in use).
    Invitations belong to one and only one Tenant.

    Attributes:
      invitation_id: Traction Contact ID
      tenant_id: Traction Tenant ID, owner of this Contact
      name: Label or Name for the Invitation
      status: Business and Tenant indicator for Invitation status
      tags: Set by tenant for adding to resulting Contacts that used this invitation
      reusable: When true, this invitation is reusable
      public: When true, this invitation is public
      deleted: Invitations "soft" delete indicator.
      connection_id: Underlying AcaPy connection id
      connection_alias: Underlying AcaPy connection alias
      invitation_url: URL to call to accept/use this invitation
      state: The underlying AcaPy connection state
      connection: Underlying AcaPy connection record
      invitation: Underlying AcaPy inviation record (if any)
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    invitation_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)

    name: str = Field(nullable=False, index=True)
    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    reusable: bool = Field(nullable=False, default=False)
    public: bool = Field(nullable=False, default=False)

    tags: List[str] = Field(sa_column=Column(ARRAY(String)))

    deleted: bool = Field(nullable=False, default=False)
    # acapy data ---
    connection_id: uuid.UUID = Field(nullable=False)
    connection_alias: str = Field(nullable=False)
    invitation_url: str = Field(nullable=False)
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

    @classmethod
    async def get_by_id(
        cls: "Invitation",
        db: AsyncSession,
        tenant_id: UUID,
        invitation_id: UUID,
        deleted: bool | None = False,
    ) -> "Invitation":
        """Get Invitation by ID.

        Find and return the database Invitation record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          invitation_id: Traction ID of Invitation

        Returns: The Traction Invitation (db) record

        Raises:
          NotFoundError: if the invitation cannot be found by ID and deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.invitation_id == invitation_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_item = q_result.scalar_one_or_none()
        if not db_item:
            raise NotFoundError(
                code="invitation.id_not_found",
                title="Invitation does not exist",
                detail=f"Invitation does not exist for id<{invitation_id}>",
            )
        return db_item

    @classmethod
    async def get_by_name(
        cls: "Invitation",
        db: AsyncSession,
        tenant_id: UUID,
        name: UUID,
        deleted: bool | None = False,
    ) -> "Invitation":
        """Get Invitation by Name.

        Find and return the database Invitation record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          name: name of Invitation

        Returns: The Traction Invitation (db) record or None if not found

        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.name == name)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_item = q_result.scalar_one_or_none()
        return db_item
