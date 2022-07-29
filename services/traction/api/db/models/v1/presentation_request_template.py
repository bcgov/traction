"""Presentation Request Templates.

Models of the Traction tables for Presentation Request Templates and related data.
Presentation Request Templates allow a tenant (verifier) to pre-create and re-use
presentation requests (proof requests).

"""
import uuid
from typing import List
from sqlmodel import Field, desc
from sqlalchemy import Column, text, select
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import (
    StatefulModel,
    TimestampModel,
    TrackingModel,
    TenantScopedModel,
)


from api.endpoints.models.v1.errors import (
    NotFoundError,
)


class PresentationRequestTemplate(
    TenantScopedModel, StatefulModel, TrackingModel, TimestampModel, table=True
):
    __tablename__ = "presentation_request_template"

    presentation_request_template_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    name: str = Field(nullable=False)
    deleted: bool = Field(nullable=False, default=False)
    comment: str = Field(nullable=True)

    presentation_request: dict = Field(default={}, sa_column=Column(JSON))

    @classmethod
    async def get_by_id(
        cls: "PresentationRequestTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        deleted: bool | None = False,
    ) -> "PresentationRequestTemplate":
        q = (
            select(cls)
            .where(cls.tenant_id == tenant_id)
            .where(cls.presentation_request_template_id == item_id)
            .where(cls.deleted == deleted)
        )
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            raise NotFoundError(
                code="presentation_request_template.id_not_found",
                title="Presentation Request Template does not exist",
                detail=f"Presentation Request Template  does not exist for id<{item_id}>",  # noqa: E501
            )
        return db_rec

    @classmethod
    async def list_by_tenant_id(
        cls: "PresentationRequestTemplate",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> List["PresentationRequestTemplate"]:
        q = select(cls).where(cls.tenant_id == tenant_id).order_by(desc(cls.updated_at))
        q_result = await db.execute(q)
        db_recs = q_result.scalars().all()
        return db_recs
