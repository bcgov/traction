"""Issuer Database Tables/Models.

Models of the Traction tables for Issuer and related data.

"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship
from sqlalchemy import (
    Column,
    select,
    desc,
    JSON,
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
from api.db.models.v1.governance import CredentialTemplate

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class IssuerCredential(
    TenantScopedModel, StatefulModel, TrackingModel, TimestampModel, table=True
):
    """Issuer Credential.

    Model for the Issuer Credential table (postgresql specific dialects in use).
    This will track Issuer Credentials for the Tenants.

    Attributes:
      issuer_credential_id: Traction ID for issuer credential
      credential_template_id: Traction Credential Template ID
      contact_id: Traction Contact ID
      cred_def_id: Credential Definition ID (ledger)
      status: Business and Tenant indicator for Credential state; independent of AcaPy
        Credential Exchange state
      external_reference_id: Set by tenant to correlate this Credential with entity in
        external system
      revoked: when True, this credential has been revoked
      deleted: Issuer Credential "soft" delete indicator.
      preview_persisted: when True, store the credential attributes and preview
      tags: Set by tenant for arbitrary grouping of Credentials
      comment: Comment supplied when issuing
      credential_preview: attributes (list of name / values ) for offered/issued cred.
        This will be empty once offer is made and preview_persisted = False.
      revocation_comment: comment entered when revoking Credential
      state: The underlying AcaPy credential exchange state
      thread_id: AcaPy thread id
      credential_exchange_id: AcaPy id for the credential exchange
      revoc_reg_id: revocation registry id (needed for revocation)
      revocation_id: credential revocation id (needed for revocation)
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "issuer_credential"

    issuer_credential_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    credential_template_id: uuid.UUID = Field(
        foreign_key="credential_template.credential_template_id", index=True
    )
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    revoked: bool = Field(nullable=False, default=False)
    deleted: bool = Field(nullable=False, default=False)
    preview_persisted: bool = Field(nullable=False, default=False)

    comment: str = Field(nullable=True)
    revocation_comment: str = Field(nullable=True)

    # acapy data ---
    cred_def_id: str = Field(nullable=False, index=True)
    thread_id: str = Field(nullable=True)
    credential_exchange_id: str = Field(nullable=True)
    revoc_reg_id: str = Field(nullable=True)
    revocation_id: str = Field(nullable=True)
    credential_preview: dict = Field(default={}, sa_column=Column(JSON))
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship(back_populates="issuer_credentials")
    credential_template: Optional[CredentialTemplate] = Relationship(
        back_populates="issuer_credentials"
    )
    # --- relationships

    @classmethod
    async def get_by_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        issuer_credential_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "IssuerCredential":
        """Get IssuerCredential by id.

        Find and return the database CredentialDefinition record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          issuer_credential_id: Traction ID of IssuerCredential

        Returns: The Traction IssuerCredential (db) record

        Raises:
          NotFoundError: if the IssuerCredential cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.issuer_credential_id == issuer_credential_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="issuer_credential.id_not_found",
                title="Issuer Credential does not exist",
                detail=f"Issuer Credential does not exist for id<{issuer_credential_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_credential_exchange_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        credential_exchange_id: str,
    ) -> "IssuerCredential":
        """Get IssuerCredential by Credential Exchange ID.

        Find and return the database IssuerCredential record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          credential_exchange_id: acapy message Credential Exchange ID

        Returns: The Traction IssuerCredential (db) record

        Raises:
          NotFoundError: if the IssuerCredential cannot be found by ID
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.credential_exchange_id == credential_exchange_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="issuer_credential.credential_exchange_id_not_found",
                title="Issuer Credential does not exist",
                detail=f"Issuer Credential does not exist for credential exchange id<{credential_exchange_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_credential_template_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        credential_template_id: uuid.UUID,
    ) -> List["IssuerCredential"]:
        """List by Credential Template ID.

        Find and return list of Issuer Credential records for Credential Template.

          tenant_id: Traction ID of tenant making the call
          credential_template_id: Traction ID of Credential Template

        Returns: List of Traction IssuerCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.credential_template_id == credential_template_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_cred_def_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        cred_def_id: str,
    ) -> List["IssuerCredential"]:
        """List by Cred Def ID.

        Find and return list of Issuer Credential records for Cred. Def.

          tenant_id: Traction ID of tenant making the call
          cred_def_id: Traction ID of Credential Definition

        Returns: List of Traction IssuerCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.cred_def_id == cred_def_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_contact_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> List["IssuerCredential"]:
        """List by Contact ID.

        Find and return list of Issuer Credential records for Contact.

          tenant_id: Traction ID of tenant making the call
          contact_id: Traction ID of Contact

        Returns: List of Traction IssuerCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.contact_id == contact_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs

    @classmethod
    async def list_by_tenant_id(
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["IssuerCredential"]:
        """List by Tenant ID.

        Find and return list of Issuer Credential records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Issuer Credential (db) records in descending order
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
        cls: "IssuerCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        thread_id: str,
    ) -> List["IssuerCredential"]:
        """List by Thread ID.

        Find and return list of Issuer Credential records for Thread ID.

          tenant_id: Traction ID of tenant making the call
          thread_id: AcaPy Thread ID of Issuer Credential

        Returns: List of Traction IssuerCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.thread_id == thread_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs
