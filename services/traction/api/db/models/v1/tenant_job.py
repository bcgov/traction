"""Tenant Job.

Models of the Traction tables for Tenant Jobs.
Some functions that a tenant would like to perform need to be allowed by the Innkeeper.
This table is to track the progress of those flows.

For example, if a tenant would like to issue credentials, there is a sequence of events
that need to happen by the innkeeper and the tenant before issuance is possible.

"""
import uuid
from enum import Enum

from sqlmodel import Field
from sqlalchemy import Column, text, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import (
    TimestampModel,
    TenantScopedModel,
    StatefulModel,
)


class TenantJobType(str, Enum):
    endorser = "Endorser"
    public_did = "Public DID"
    issuer = "Issuer"


class TenantJobStatusType(str, Enum):
    requested = "Requested"  # requested by tenant
    approved = "Approved"  # approved by innkeeper, tenant can proceed
    denied = "Denied"  # denied by innkeeper, job terminates
    processing = "Processing"  # job is in flight, check state field for progress
    error = "Error"  # error during processing
    completed = "Completed"  # job is completed, value in completed_value
    active = "Active"  # job complete and anything dependent on this can proceed
    default = "N/A"  # job has not been started.


class TenantJobStateType(str, Enum):
    """
    state should be different types for different jobs...
    """

    default = "N/A"  # flow has not been started.


class TenantJob(TenantScopedModel, StatefulModel, TimestampModel, table=True):
    __tablename__ = "tenant_job"
    __table_args__ = (UniqueConstraint("tenant_id", "job_type"),)

    tenant_job_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    job_type: str = Field(nullable=False)
    data: dict = Field(default={}, sa_column=Column(JSON))
    comment: str = Field(nullable=True)

    @classmethod
    async def get_for_tenant(
        cls: "TenantJob",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        job_type: str,
    ) -> "TenantJob":
        """Get TenantJob by tenant id and flow type.

        Find and return the database record.
        If one does not exist, insert a default and return it.

        Args:
          db: database session
          tenant_id: Traction ID of tenant this flow belongs to
          job_type: the particular job we are interested n

        Returns: The Traction TenantJob (db) record

        Raises:

        """

        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.job_type == job_type)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            db_rec = cls(
                tenant_id=tenant_id,
                job_type=job_type,
                status=TenantJobStatusType.default,
                state=TenantJobStateType.default,
            )
            db.add(db_rec)
            await db.commit()

        return db_rec
