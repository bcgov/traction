"""Governance Database Tables/Models.

Models of the Traction tables for Governance and related data. This includes ledger
related tables for schemas and credential definitions.

"""
import uuid
from datetime import datetime
from typing import List

from sqlmodel import Field, Relationship
from sqlalchemy import (
    Column,
    func,
    String,
    select,
    desc,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, ARRAY, UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import BaseModel, StatefulModel

from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class SchemaTemplate(StatefulModel, table=True):
    """SchemaTemplate.

    This is the model for the Schema table (postgresql specific dialects in use).
    Schemas are registered on the ledger, so there can be only one...
    However, each Tenant can import the same schema for their own purposes. For now,
    there will be redundancy in the Schema data, we are going to wait on usage to
    determine if we need to normalize and have a singular table for Schemas for all and
    then join table for Schema/Tenant.


    There is already a table for v0 API named tenantschema and this is named differently
     to avoid confusion and interference.  When v0 is retired/deleted, perhaps we change
     the name then...

    For a given tenant, the schema can be found by the schema_template_id (Traction id)
    or schema_id (ledger id).

    Attributes:
      schema_template_id: Traction ID
      tenant_id: Traction Tenant ID, owner of this Contact
      schema_id: This will be the ledger schema id - this is not a UUID
      name: a "pretty" name for the schema, this can be different than the name on the
        ledger (schema_name).
      status: Status of the schema as it is being endorsed and registered
      tags: Set by tenant for arbitrary grouping of their Schemas
      deleted: Schema/Tenant "soft" delete indicator.
      imported: When True, this tenant imported the schema, otherwise they created it
      version: version, on ledger
      attributes: list of attribute names, on ledger
      schema_name: name as is appears on the ledger
      transaction_id: id used when schema is being endorsed and registered
      state: The underlying AcaPy endorser state
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "schema_template"
    __table_args__ = (UniqueConstraint("tenant_id", "schema_id"),)
    schema_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)
    schema_id: str = Field(nullable=True, index=True)

    name: str = Field(nullable=False)

    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    deleted: bool = Field(nullable=False, default=False)
    imported: bool = Field(nullable=False, default=False)
    # ledger data ---
    version: str = Field(nullable=False)
    attributes: List[str] = Field(sa_column=Column(ARRAY(String)))
    schema_name: str = Field(nullable=True)
    transaction_id: str = Field(nullable=True)
    # --- ledger data

    @classmethod
    async def get_by_id(
        cls: "SchemaTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        schema_template_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "SchemaTemplate":
        """Get SchemaTemplate by schema_template_id.

        Find and return the database SchemaTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          schema_template_id: Traction ID of Schema Template

        Returns: The Traction SchemaTemplate (db) record

        Raises:
          NotFoundError: if the SchemaTemplate cannot be found by ID and deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.schema_template_id == schema_template_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="schema_template.id_not_found",
                title="Schema Template does not exist",
                detail=f"Schema Template does not exist for id<{schema_template_id}>",
            )
        return db_rec

    @classmethod
    async def get_by_schema_id(
        cls: "SchemaTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        schema_id: str,
        deleted: bool | None = False,
    ) -> "SchemaTemplate":
        """Get SchemaTemplate by schema_id.

        Find and return the database SchemaTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          schema_id: Ledger Schema ID of Schema Template

        Returns: The Traction SchemaTemplate (db) record

        Raises:
          NotFoundError: if the SchemaTemplate cannot be found by schema ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.schema_id == schema_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="schema_template.schema_id_not_found",
                title="Schema Template does not exist",
                detail=f"Schema Template does not exist for schema_id<{schema_id}>",
            )
        return db_rec

    @classmethod
    async def get_by_transaction_id(
        cls: "SchemaTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        transaction_id: str,
        deleted: bool | None = False,
    ) -> "SchemaTemplate":
        """Get SchemaTemplate by transaction_id.

        Find and return the database SchemaTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          transaction_id: Transaction ID from endorser

        Returns: The Traction SchemaTemplate (db) record

        Raises:
          NotFoundError: if the SchemaTemplate cannot be found by schema ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.transaction_id == transaction_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="schema_template.transaction_id_not_found",
                title="Schema Template does not exist",
                detail=f"Schema Template does not exist for transaction_id<{transaction_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_tenant_id(
        cls: "SchemaTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["SchemaTemplate"]:
        """List by Tenant ID.

        Find and return list of SchemaTemplate records for Tenant.

        Args:
          db: database session
          tenant_id: Traction ID of Tenant

        Returns: List of Traction SchemaTemplate (db) records in descending order
        """

        q = select(cls).where(cls.tenant_id == tenant_id).order_by(desc(cls.updated_at))
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs


class CredentialTemplate(BaseModel, table=True):
    """Credential Template.

    Model for the Credential Definition table (postgresql specific dialects in use).
    This will track Credential Definitions for the Tenants.

    For a given tenant, the Credential Tempalte can be found by the
    credential_template_id (Traction id) or cred_def_id (ledger id).

    Attributes:
      credential_template_id: Traction ID
      tenant_id: Traction Tenant ID
      schema_template_id: Traction ID for Schema Template
      cred_def_id: Credential Definition ID from the ledger
      schema_id: Ledger ID of Schema this credential definition is for
      name: based on SchemaTemplate.name, but allow override here...
      status: Status of the credential definition as it is being endorsed and registered
      deleted: Credential Definition "soft" delete indicator.
      transaction_id: id used when schema is being endorsed and registered
      tags: Set by tenant for arbitrary grouping of Credential Templates/Definitions
      tag: tag used to create the credential definition (on ledger)
      attributes: list of attribute names (on ledger)
      state: The underlying AcaPy endorser state
      revocation_enabled: when True, subsequent Credentials can be revoked.
      revocation_registry_size: how large the default revocation registry is
      revocation_registry_state: The underlying AcaPy endorser state for revocation
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "credential_template"
    credential_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", nullable=False, index=True)
    schema_template_id: uuid.UUID = Field(
        foreign_key="schema_template.schema_template_id", nullable=False, index=True
    )
    cred_def_id: str = Field(nullable=True, index=True)
    schema_id: str = Field(nullable=True)

    name: str = Field(nullable=False)
    status: str = Field(nullable=False)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    deleted: bool = Field(nullable=False, default=False)
    state: str = Field(nullable=False)

    # ledger(ish) data ---
    transaction_id: str = Field(nullable=True)
    tag: str = Field(nullable=False)
    attributes: List[str] = Field(sa_column=Column(ARRAY(String)))
    revocation_enabled: bool = Field(nullable=False, default=False)
    revocation_registry_size: int = Field(nullable=True, default=None)
    revocation_registry_state: str = Field(nullable=False)
    # --- ledger data

    # relationships ---
    issuer_credentials: List["IssuerCredential"] = Relationship(  # noqa: F821
        back_populates="credential_template"
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
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        credential_template_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "CredentialTemplate":
        """Get CredentialDefinition by cred def id.

        Find and return the database CredentialTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          credential_template_id: Traction ID of CredentialTemplate

        Returns: The Traction CredentialTemplate (db) record

        Raises:
          NotFoundError: if the CredentialTemplate cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.credential_template_id == credential_template_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="credential_template.id_not_found",
                title="Credential Template does not exist",
                detail=f"Credential Template does not exist for id<{credential_template_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_cred_def_id(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        cred_def_id: str,
        deleted: bool | None = False,
    ) -> "CredentialTemplate":
        """Get CredentialDefinition by cred def id.

        Find and return the database CredentialTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          cred_def_id: Ledger Cred Def ID of CredentialTemplate

        Returns: The Traction CredentialTemplate (db) record

        Raises:
          NotFoundError: if the CredentialTemplate cannot be found by Cred Def ID and
          deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.cred_def_id == cred_def_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="credential_template.cred_def_id_not_found",
                title="Credential Template does not exist",
                detail=f"Credential Template does not exist for cred_def_id<{cred_def_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_transaction_id(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        transaction_id: str,
        deleted: bool | None = False,
    ) -> "CredentialTemplate":
        """Get CredentialTemplate by transaction_id.

        Find and return the database CredentialTemplate record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          transaction_id: Transaction ID from endorser

        Returns: The Traction CredentialTemplate (db) record

        Raises:
          NotFoundError: if the CredentialTemplate cannot be found by schema ID and
          deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.transaction_id == transaction_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="credential_template.transaction_id_not_found",
                title="Credential Template does not exist",
                detail=f"Credential Template does not exist for transaction_id<{transaction_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_schema_and_tag(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        schema_id: str,
        tag: str,
    ) -> "CredentialTemplate":
        """Get CredentialTemplate by schema id (ledger) and tag.

        Use this to determine if we can create a new template. If we have a tag for
        this schema, then we cannot reliably create the cred def on the ledger.

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          schema_id: ledger schema id
          tag: cred def tag

        Returns: The Traction CredentialTemplate (db) record or None

        """
        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.schema_id == schema_id)
            .where(cls.tag == tag)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        return db_rec

    @classmethod
    async def list_by_schema_template_id(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        schema_template_id: uuid.UUID,
        status: str | None = None,
    ) -> List["CredentialTemplate"]:
        """List by Schema Template ID.

        Find and return list of Credential Template records for Schema (Tenant).

          tenant_id: Traction ID of tenant making the call
          schema_template_id: Traction ID of SchemaTemplate
          status: optional, if provided return only items that have this status

        Returns: List of Traction CredentialTemplate (db) records in descending order
        """
        filters = [
            cls.tenant_id == tenant_id,
            cls.schema_template_id == schema_template_id,
        ]
        if status:
            filters.append(cls.status == status)

        q = select(cls).filter(*filters).order_by(desc(cls.updated_at))
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_schema_id(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        schema_id: str,
    ) -> List["CredentialTemplate"]:
        """List by Schema ID.

        Find and return list of Credential Template records for Schema (Tenant).

          tenant_id: Traction ID of tenant making the call
          schema_id: Ledger ID of Schema

        Returns: List of Traction CredentialTemplate (db) records in descending order
        """

        q = (
            select(cls)
            .where(cls.schema_id == schema_id)
            .where(cls.tenant_id == tenant_id)
            .order_by(desc(cls.created_at))
        )
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs

    @classmethod
    async def list_by_tenant_id(
        cls: "CredentialTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["CredentialTemplate"]:
        """List by Tenant ID.

        Find and return list of Credential Template records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction CredentialTemplate (db) records in descending order
        """

        q = select(cls).where(cls.tenant_id == tenant_id).order_by(desc(cls.updated_at))
        q_result = await db.execute(q)
        db_recs = q_result.scalars()
        return db_recs
