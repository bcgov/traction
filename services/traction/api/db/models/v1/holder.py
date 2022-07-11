"""Issuer Database Tables/Models.

Models of the Traction tables for Holder and related data.

"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship
from sqlalchemy import (
    Column,
    select,
    desc,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import StatefulModel, TimestampModel, TrackingModel
from api.db.models.v1.contact import Contact

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class HolderCredential(StatefulModel, TrackingModel, TimestampModel, table=True):
    """Holder Credential.

    Model for the Holder Credential table (postgresql specific dialects in use).
    This will track Holder Credentials/Offers for the Tenants.

    Attributes:
      holder_credential_id: Traction ID for holder credential
      tenant_id: Traction Tenant ID
      contact_id: Traction Contact ID (issuer)
      status: Business and Tenant indicator for Credential state; independent of AcaPy
        Credential Exchange state
      state: The underlying AcaPy credential exchange state
      external_reference_id: Set by tenant to correlate this Credential with entity in
        external system
      tags: Set by tenant for arbitrary grouping of Credentials
      deleted: Holder Credential "soft" delete indicator.
      revoked: when True, this credential has been revoked
      revocation_comment: comment entered when revoking Credential
      thread_id: AcaPy thread id
      credential_exchange_id: AcaPy id for the credential exchange
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "holder_credential"

    holder_credential_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    deleted: bool = Field(nullable=False, default=False)

    revoked: bool = Field(nullable=False, default=False)
    revocation_comment: str = Field(nullable=True)

    # acapy data ---
    thread_id: str = Field(nullable=True)
    credential_exchange_id: str = Field(nullable=True)
    connection_id: str = Field(nullable=True)
    schema_id: str = Field(nullable=True)
    cred_def_id: str = Field(nullable=False)
    credential_id: str = Field(nullable=True)
    revoc_reg_id: str = Field(nullable=True)
    revocation_id: str = Field(nullable=True)
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship()
    # --- relationships

    @classmethod
    async def get_by_id(
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        holder_credential_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "HolderCredential":
        """Get HolderCredential by id.

        Find and return the database Holder Credential record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          holder_credential_id: Traction ID of HolderCredential

        Returns: The Traction HolderCredential (db) record

        Raises:
          NotFoundError: if the HolderCredential cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.holder_credential_id == holder_credential_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="holder_credential_id.id_not_found",
                title="Holder Credential does not exist",
                detail=f"Holder Credential does not exist for id<{holder_credential_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_credential_exchange_id(
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        credential_exchange_id: str,
    ) -> "HolderCredential":
        """Get HolderCredential by Credential Exchange ID.

        Find and return the database HolderCredential record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          credential_exchange_id: acapy message Credential Exchange ID

        Returns: The Traction HolderCredential (db) record

        Raises:
          NotFoundError: if the HolderCredential cannot be found by ID
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.credential_exchange_id == credential_exchange_id)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="holder_credential.credential_exchange_id_not_found",
                title="Holder Credential does not exist",
                detail=f"Holder Credential does not exist for credential exchange id<{credential_exchange_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_contact_id(
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> List["HolderCredential"]:
        """List by Contact ID.

        Find and return list of Holder Credential records for Contact.

          tenant_id: Traction ID of tenant making the call
          contact_id: Traction ID of Contact

        Returns: List of Traction HolderCredential (db) records in descending order
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
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["HolderCredential"]:
        """List by Tenant ID.

        Find and return list of Holder Credential records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Holder Credential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_thread_id(
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        thread_id: str,
    ) -> List["HolderCredential"]:
        """List by Thread ID.

        Find and return list of Holder Credential records for Thread ID.

          tenant_id: Traction ID of tenant making the call
          thread_id: AcaPy Thread ID of Issuer Credential

        Returns: List of Traction HolderCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.thread_id == thread_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def get_by_revocation_ids(
        cls: "HolderCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        revoc_reg_id: str,
        revocation_id: str,
    ) -> "HolderCredential":
        """Get Holder Credential by Revocation IDs.

        Find and return the database Holder Credential record by the revocation ids.

        Args:
          db: database session
          tenant_id: Traction tenant (holder) id
          revoc_reg_id: acapy revocation message Revocation Registry ID
          revocation_id: acapy revocation message Revocation ID

        Returns: The Traction Holder Credential (db) record

        Raises:
          NotFoundError: if the HolderCredential cannot be found by IDs
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.revoc_reg_id == revoc_reg_id)
            .where(cls.revocation_id == revocation_id)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="holder_credential.revocation_ids_not_found",
                title="Holder Credential does not exist",
                detail=f"Holder Credential does not exist for revocation registration id<{revoc_reg_id}> / revocation id<{revocation_id}>",  # noqa: E501
            )
        return db_rec
