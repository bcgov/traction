"""Issuer Database Tables/Models.

Models of the Traction tables for Issuer and related data.

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
    JSON,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import BaseModel
from api.db.models.v1.contact import Contact
from api.db.models.v1.governance import CredentialTemplate

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class IssuedCredential(BaseModel, table=True):
    """Issued Credential.

    Model for the Issued Credential table (postgresql specific dialects in use).
    This will track Issued Credentials for the Tenants.

    Attributes:
      issued_credential_id: Traction ID for issued credential
      credential_template_id: Traction Credential Template ID
      contact_id: Traction Contact ID
      cred_def_id: Credential Definition ID (ledger)
      tenant_id: Traction Tenant ID
      status: Business and Tenant indicator for Credential state; independent of AcaPy
        Credential Exchange state
      external_reference_id: Set by tenant to correlate this Credential with entity in
        external system
      revoked: when True, this credential has been revoked
      deleted: Issued Credential "soft" delete indicator.
      credential_persisted: when True, store the credential attributes and preview
      tags: Set by tenant for arbitrary grouping of Credentials
      comment: Comment supplied when issuing
      credential_preview: attributes (list of name / values ) for offered/issued cred.
        This will be empty once offer is made and credential_persisted = False.
      revocation_comment: comment entered when revoking Credential
      state: The underlying AcaPy credential exchange state
      thread_id: AcaPy thread id
      credential_exchange_id: AcaPy id for the credential exchange
      revoc_reg_id: revocation registry id (needed for revocation)
      revocation_id: credential revocation id (needed for revocation)
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "issued_credential"

    issued_credential_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    credential_template_id: uuid.UUID = Field(
        foreign_key="credential_template.credential_template_id", index=True
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    status: str = Field(nullable=False)
    external_reference_id: str = Field(nullable=True)
    revoked: bool = Field(nullable=False, default=False)
    deleted: bool = Field(nullable=False, default=False)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    credential_persisted: bool = Field(nullable=False, default=False)

    comment: str = Field(nullable=True)
    revocation_comment: str = Field(nullable=True)

    # acapy data ---
    state: str = Field(nullable=False)
    cred_def_id: str = Field(nullable=False, index=True)
    thread_id: str = Field(nullable=True)
    credential_exchange_id: str = Field(nullable=True)
    revoc_reg_id: str = Field(nullable=True)
    revocation_id: str = Field(nullable=True)
    credential_preview: dict = Field(default={}, sa_column=Column(JSON))
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship(back_populates="issued_credentials")
    credential_template: Optional[CredentialTemplate] = Relationship(
        back_populates="issued_credentials"
    )
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
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        issued_credential_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "IssuedCredential":
        """Get IssuedCredential by id.

        Find and return the database CredentialDefinition record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          issued_credential_id: Traction ID/LedgerID of IssuedCredential

        Returns: The Traction IssuedCredential (db) record

        Raises:
          NotFoundError: if the IssuedCredential cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.issued_credential_id == issued_credential_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="issued_credential.id_not_found",
                title="Issued Credential does not exist",
                detail=f"Issued Credential does not exist for id<{issued_credential_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_credential_template_id(
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        credential_template_id: uuid.UUID,
    ) -> List["IssuedCredential"]:
        """List by Credential Template ID.

        Find and return list of Issued Credential records for Credential Template.

          tenant_id: Traction ID of tenant making the call
          credential_template_id: Traction ID of Credential Template

        Returns: List of Traction IssuedCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.credential_template_id == credential_template_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_cred_def_id(
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        cred_def_id: str,
    ) -> List["IssuedCredential"]:
        """List by Cred Def ID.

        Find and return list of Issued Credential records for Cred. Def.

          tenant_id: Traction ID of tenant making the call
          cred_def_id: Traction ID of Credential Definition

        Returns: List of Traction IssuedCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.cred_def_id == cred_def_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_contact_id(
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        contact_id: uuid.UUID,
    ) -> List["IssuedCredential"]:
        """List by Contact ID.

        Find and return list of Issued Credential records for Credential Template.

          tenant_id: Traction ID of tenant making the call
          contact_id: Traction ID of Contact

        Returns: List of Traction IssuedCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.contact_id == contact_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_tenant_id(
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["IssuedCredential"]:
        """List by Tenant ID.

        Find and return list of Issued Credential records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Issued Credential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_thread_id(
        cls: "IssuedCredential",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        thread_id: str,
    ) -> List["IssuedCredential"]:
        """List by Thread ID.

        Find and return list of Issued Credential records for Thread ID.

          tenant_id: Traction ID of tenant making the call
          thread_id: AcaPy Thread ID of Issued Credential

        Returns: List of Traction IssuedCredential (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.thread_id == thread_id)
            .where(cls.tenant_id == tenant_id)
            .options(selectinload(cls.contact), selectinload(cls.credential_template))
            .order_by(desc(cls.updated_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs


class IssuedCredentialTimeline(BaseModel, table=True):
    """Issued Credential Timeline.

    Model for Issued Credential Timeline table (postgresql specific dialects in use).
    Timeline represents history of changes to status and/or state.

    Attributes:
      issued_credential_timeline_id: Unique ID in table
      issued_credential_id: Traction Issued Credential ID
      status: Business and Tenant indicator for Issued Credential state; independent of
        AcaPy Credential State
      state: The underlying AcaPy Credential state
      created_at: Timestamp when record was created in Traction
    """

    __tablename__ = "issued_credential_timeline"

    issued_credential_timeline_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    issued_credential_id: uuid.UUID = Field(
        foreign_key="issued_credential.issued_credential_id", index=True
    )

    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )

    @classmethod
    async def list_by_issued_credential_id(
        cls: "IssuedCredentialTimeline",
        db: AsyncSession,
        issued_credential_id: UUID,
    ) -> List:
        """List by Issued Credential ID.

        Find and return list of Timeline records for Issued Credential.

        Args:
          db: database session
          issued_credential_id: Traction ID of Issued Credential

        Returns: List of Traction Issued Credential Timeline (db) records in descending
          order
        """

        q = (
            select(cls)
            .where(cls.issued_credential_id == issued_credential_id)
            .order_by(desc(cls.created_at))
        )
        q_result = await db.execute(q)
        db_items = q_result.scalars()
        return db_items
