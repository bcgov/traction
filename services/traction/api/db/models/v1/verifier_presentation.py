"""Verification Presentation for proof.

Models of the Traction tables for Verification Presentation and related data.

"""
import uuid
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, desc
from sqlalchemy import Column, text, select
from sqlalchemy.dialects.postgresql import UUID, JSON
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


class VerifierPresentation(
    TenantScopedModel, StatefulModel, TrackingModel, TimestampModel, table=True
):
    """Verification Presentation

    Model for the Verification Presentation table (postgresql specific
    dialects in use).This will track verifications of proof for the Tenants.

    Attributes:
    """

    __tablename__ = "verifier_presentation"

    verifier_presentation_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    deleted: bool = Field(nullable=False, default=False)
    comment: str = Field(nullable=True)

    # acapy data ---
    pres_exch_id: uuid.UUID = Field(nullable=True)

    # all in proof_request, store locally for searching/filtering
    version: str = Field(nullable=True)
    name: str = Field(nullable=True)
    proof_request: dict = Field(default={}, sa_column=Column(JSON))
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship(
        sa_relationship_kwargs={"lazy": "joined"}
    )  # don't back populate
    # --- relationships

    @classmethod
    async def get_by_id(
        cls: "VerifierPresentation",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        verifier_presentation_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "VerifierPresentation":
        """Get VerifierPresentation by id.

        Find and return the database VerifierPresentation record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          verifier_presentation_id: Traction ID of VerifierPresentation

        Returns: The Traction VerifierPresentation (db) record

        Raises:
          NotFoundError: if the VerifierPresentation cannot be
          found by ID and deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.verifier_presentation_id == verifier_presentation_id)
            .where(cls.deleted == deleted)
            .options(cls.contact)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="verifier_presentation.id_not_found",
                title="Verification Presentation does not exist",
                detail=f"Verification Presentation does not exist for id<{verifier_presentation_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def get_by_pres_exch_id(
        cls: "VerifierPresentation",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        pres_exch_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "VerifierPresentation":
        """Get VerifierPresentation by id.

        Find and return the database VerifierPresentation record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          pres_exch_id: Traction ID of VerifierPresentation

        Returns: The Traction VerifierPresentation (db) record

        Raises:
          NotFoundError: if the VerifierPresentation cannot be
          found by ID and deleted flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.pres_exch_id == pres_exch_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="verifier_presentation.id_not_found",
                title="Verification Presentation does not exist",
                detail=f"Verification Presentation does not exist for pres_exch_id<{pres_exch_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_tenant_id(
        cls: "VerifierPresentation",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["VerifierPresentation"]:
        """List by Tenant ID.

        Find and return list of Verification Request records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Verification Request (db) records in descending order
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
