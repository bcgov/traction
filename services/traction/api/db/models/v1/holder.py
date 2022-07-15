"""Holder Database Tables/Models.

Models of the Traction tables for Holder and related data.

"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship
from sqlalchemy import (
    Column,
    desc,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import (
    StatefulModel,
    TimestampModel,
    TrackingModel,
    TenantScopedModel,
)
from api.db.models.v1.contact import Contact

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class HolderCredential(
    StatefulModel, TrackingModel, TimestampModel, TenantScopedModel, table=True
):
    """Holder Credential.

    Model for the Holder Credential table (postgresql specific dialects in use).
    This will track Holder Credentials/Offers for the Tenants.

    Attributes:
      holder_credential_id: Traction ID for holder credential
      tenant_id: Traction Tenant ID
      contact_id: Traction Contact ID (issuer)
      alias: tenant provided name/alias to identify the credential
      rejection_comment: tenant provided comment when rejecting offer (sent to issuer)
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
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    deleted: bool = Field(nullable=False, default=False)

    alias: str = Field(nullable=True)
    rejection_comment: str = Field(nullable=True)

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
            cls.tenant_select()
            .where(cls.holder_credential_id == holder_credential_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact))
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
        credential_exchange_id: str,
    ) -> "HolderCredential":
        """Get HolderCredential by Credential Exchange ID.

        Find and return the database HolderCredential record

        Args:
          db: database session
          credential_exchange_id: acapy message Credential Exchange ID

        Returns: The Traction HolderCredential (db) record

        Raises:
          NotFoundError: if the HolderCredential cannot be found by ID
        """

        q = (
            cls.tenant_select()
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
        contact_id: uuid.UUID,
    ) -> List["HolderCredential"]:
        """List by Contact ID.

        Find and return list of Holder Credential records for Contact.

          contact_id: Traction ID of Contact

        Returns: List of Traction HolderCredential (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .where(cls.contact_id == contact_id)
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
    ) -> List["HolderCredential"]:
        """List by Tenant ID.

        Find and return list of Holder Credential records for Tenant.

        Returns: List of Traction Holder Credential (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_thread_id(
        cls: "HolderCredential",
        db: AsyncSession,
        thread_id: str,
    ) -> List["HolderCredential"]:
        """List by Thread ID.

        Find and return list of Holder Credential records for Thread ID.

          tenant_id: Traction ID of tenant making the call
          thread_id: AcaPy Thread ID of Issuer Credential

        Returns: List of Traction HolderCredential (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .where(cls.thread_id == thread_id)
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
        revoc_reg_id: str,
        revocation_id: str,
    ) -> "HolderCredential":
        """Get Holder Credential by Revocation IDs.

        Find and return the database Holder Credential record by the revocation ids.

        Args:
          db: database session
          revoc_reg_id: acapy revocation message Revocation Registry ID
          revocation_id: acapy revocation message Revocation ID

        Returns: The Traction Holder Credential (db) record

        Raises:
          NotFoundError: if the HolderCredential cannot be found by IDs
        """

        q = (
            cls.tenant_select()
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


class HolderPresentation(
    StatefulModel, TrackingModel, TimestampModel, TenantScopedModel, table=True
):
    """Holder Presentation.

    Model for the Holder Presentation table (postgresql specific dialects in use).
    This will track Holder Presentations/Offers for the Tenants.

    Attributes:
      holder_presentation_id: Traction ID for holder presentation
      tenant_id: Traction Tenant ID
      contact_id: Traction Contact ID (issuer)
      alias: tenant provided name/alias to identify the presentation
      status: Business and Tenant indicator for Presentation state; independent of AcaPy
        Presentation Exchange state
      state: The underlying AcaPy presentation exchange state
      external_reference_id: Set by tenant to correlate this Presentation with entity in
        external system
      tags: Set by tenant for arbitrary grouping of Presentations
      deleted: Holder Presentation "soft" delete indicator.
      thread_id: AcaPy thread id
      presentation_exchange_id: AcaPy id for the presentation exchange
      connection_id: AcaPy connection id for the Contact
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "holder_presentation"

    holder_presentation_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    deleted: bool = Field(nullable=False, default=False)

    alias: str = Field(nullable=True)

    # acapy data ---
    thread_id: str = Field(nullable=True)
    presentation_exchange_id: str = Field(nullable=True)
    connection_id: str = Field(nullable=True)
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship()
    # --- relationships

    @classmethod
    async def get_by_id(
        cls: "HolderPresentation",
        db: AsyncSession,
        holder_presentation_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "HolderPresentation":
        """Get HolderPresentation by id.

        Find and return the database Holder Presentation record

        Args:
          db: database session
          holder_presentation_id: Traction ID of HolderPresentation

        Returns: The Traction HolderPresentation (db) record

        Raises:
          NotFoundError: if the HolderPresentation cannot be found by ID and deleted
          flag
        """

        q = (
            cls.tenant_select()
            .where(cls.holder_presentation_id == holder_presentation_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="holder_presentation_id.id_not_found",
                title="Holder Presentation does not exist",
                detail=f"Holder Presentation does not exist for id<{holder_presentation_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_presentation_exchange_id(
        cls: "HolderPresentation",
        db: AsyncSession,
        presentation_exchange_id: str,
    ) -> "HolderPresentation":
        """Get HolderPresentation by Presentation Exchange ID.

        Find and return the database HolderPresentation record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          presentation_exchange_id: acapy message Presentation Exchange ID

        Returns: The Traction HolderPresentation (db) record

        Raises:
          NotFoundError: if the HolderPresentation cannot be found by ID
        """

        q = (
            cls.tenant_select()
            .where(cls.presentation_exchange_id == presentation_exchange_id)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="holder_presentation.presentation_exchange_id_not_found",
                title="Holder Presentation does not exist",
                detail=f"Holder Presentation does not exist for presentation exchange id<{presentation_exchange_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_contact_id(
        cls: "HolderPresentation",
        db: AsyncSession,
        contact_id: uuid.UUID,
    ) -> List["HolderPresentation"]:
        """List by Contact ID.

        Find and return list of Holder Presentation records for Contact.

          contact_id: Traction ID of Contact

        Returns: List of Traction HolderPresentation (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .where(cls.contact_id == contact_id)
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_tenant_id(
        cls: "HolderPresentation",
        db: AsyncSession,
    ) -> List["HolderPresentation"]:
        """List by Tenant ID.

        Find and return list of Holder Presentation records for Tenant.


        Returns: List of Traction Holder Presentation (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_thread_id(
        cls: "HolderPresentation",
        db: AsyncSession,
        thread_id: str,
    ) -> List["HolderPresentation"]:
        """List by Thread ID.

        Find and return list of Holder Presentation records for Thread ID.

          thread_id: AcaPy Thread ID of Holder Presentation

        Returns: List of Traction HolderPresentation (db) records in descending order
        """

        q = (
            cls.tenant_select()
            .where(cls.thread_id == thread_id)
            .options(selectinload(cls.contact))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs
