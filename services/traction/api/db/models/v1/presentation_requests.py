"""Verification requests for proof.

Models of the Traction tables for Connection Invitation and related data.

"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, desc
from sqlalchemy import Column, func, text, String, select
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSON, ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import BaseModel

from api.db.models.v1.contact import Contact

from api.endpoints.models.v1.errors import (
    NotFoundError,
)

# SQL Model doesn't handle single table inheritence well enough....
class VerifierPresentationRequest(BaseModel, table=True):
    """Verifier Presentation Request

    Model for the Verifier Presentation Requesttable (postgresql specific dialects in use).
    This will track verifications of proof for the Tenants.

    Attributes:
    """

    __tablename__ = "verifier_presentation_request"

    v_presentation_request_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    tenant_id: uuid.UUID = Field(
        foreign_key="tenant.id", index=True
    )  # TODO why isn't this in base
    contact_id: uuid.UUID = Field(foreign_key="contact.contact_id", index=True)
    status: str = Field(nullable=False)
    external_reference_id: str = Field(nullable=True)
    deleted: bool = Field(nullable=False, default=False)
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    comment: str = Field(nullable=True)

    # acapy data ---
    # role: str = Field(nullable=False)  # verifier, prover
    state: str = Field(nullable=False)
    pres_exch_id: uuid.UUID = Field(nullable=False, index=True)
    proof_request: dict = Field(default={}, sa_column=Column(JSON))
    # --- acapy data

    # relationships ---
    contact: Optional[Contact] = Relationship()  # don't back populate
    # --- relationships

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )  # TODO why isn't this in base
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )  # TODO why isn't this in base
    # __mapper_args__ = {"polymorphic_identity": "role", "polymorphic_on": "type"}

    classmethod

    async def get_by_id(
        cls: "VerifierPresentationRequest",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        v_presentation_request_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "VerifierPresentationRequest":
        """Get VerifierPresentationRequest by id.

        Find and return the database CredentialDefinition record

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call
          v_presentation_request_id: Traction ID of VerifierPresentationRequest

        Returns: The Traction VerifierPresentationRequest (db) record

        Raises:
          NotFoundError: if the VerifierPresentationRequest cannot be found by ID and deleted
          flag
        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.v_presentation_request_id == v_presentation_request_id)
            .where(cls.deleted == deleted)
            .options(selectinload(cls.contact))
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="presentation_request.id_not_found",
                title="Verifier Presentation Request does not exist",
                detail=f"Issuer Credential does not exist for id<{v_presentation_request_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_tenant_id(
        cls: "VerifierPresentationRequest",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["VerifierPresentationRequest"]:
        """List by Tenant ID.

        Find and return list of Issuer Credential records for Tenant.

          tenant_id: Traction ID of tenant making the call

        Returns: List of Traction Issuer Credential (db) records in descending order
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
