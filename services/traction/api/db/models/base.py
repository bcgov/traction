import builtins
import uuid
from datetime import datetime
from typing import Optional, List

import logging
import pydantic
from sqlalchemy.exc import DBAPIError
from starlette_context import context
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, func, text, select, desc, String
from sqlalchemy.sql.expression import Select
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, VARCHAR, ARRAY
from sqlmodel.ext.asyncio.session import AsyncSession
from api.endpoints.dependencies.tenant_context import get_from_context

from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError

logger = logging.getLogger(__name__)


class BaseSchema(pydantic.BaseModel):
    class Config(pydantic.BaseModel.Config):
        orm_mode = True
        read_with_orm_mode = True


class BaseModel(SQLModel, BaseSchema):
    __mapper_args__ = {"eager_defaults": True}

    @classmethod
    async def update_by_id(cls, item_id: UUID, values: dict):
        """Update Item by ID.

        This is a utility method in a self contained session and transaction.
        This will fetch the item by id, and update using the values dictionary provided.

        Args:
          item_id: Traction ID of the record.
          values: dictionary of values to update.

        Returns:
            the updated record

        Raises:
            NotFoundError if record is not found
            DBAPIError if other database level error, transaction is rolled back.
        """
        async with async_session() as db:
            try:
                o = await db.get(cls, item_id)
                if o:
                    for key in values.keys():
                        try:
                            setattr(o, key, values[key])
                        except AttributeError:
                            # this is the same as calling hasattr first
                            pass
                    db.add(o)
                    await db.commit()
                    return await db.get(cls, item_id)
                else:
                    raise NotFoundError(
                        code=f"{cls.__tablename__}.update.id_not_found",
                        title="Update Error",
                        detail=f"Cannot perform update. ID <{item_id}> not found.",
                    )
            except DBAPIError as e:
                await db.rollback()
                raise e


class TenantScopedModel(BaseModel):
    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True)

    @classmethod
    def tenant_select(cls) -> Select:
        result = None
        tenant_context_id = get_from_context("TENANT_ID")

        # load from starlette context
        if tenant_context_id:
            result = select(cls).where(cls.tenant_id == tenant_context_id)
        # couldn't load tenant context for some reason
        else:
            logger.warning(
                f"""QUERY ON {cls.__name__}: starlette_context.context["TENANT_ID"] not set,
                EXECUTING AN UNSAFE QUERY"""
            )
            result = select(cls)

        return result


class BaseTable(BaseModel):
    # the following are marked optional because they are generated on the server
    # these will be included in each class where we set table=true (our table classes)
    id: Optional[uuid.UUID] = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


class TimestampModel(BaseModel):
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
        )
    )


class StatefulModel(BaseModel):
    def check_error_status_detail(context):
        try:
            if context.get_current_parameters()["status"] != "Error":
                return None
        except builtins.KeyError:
            pass

    status: str = Field(nullable=False)
    state: str = Field(nullable=False)

    error_status_detail: Optional[str] = Field(
        sa_column=Column(VARCHAR, nullable=True, onupdate=check_error_status_detail)
    )


class Timeline(StatefulModel, table=True):

    timeline_id: uuid.UUID = Field(
        sa_column=Column(
            UUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        )
    )

    item_id: uuid.UUID = Field(nullable=False, index=True)

    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )

    @classmethod
    async def list_by_item_id(
        cls: "TimelineModel",
        db: AsyncSession,
        item_id: UUID,
    ) -> List:
        """List by Item ID.

        Find and return list of Timeline records for item.

        Args:
          db: database session
          item_id: Traction ID of item (Schema Template, Credential Template etc)

        Returns: List of Traction Schema Template Timeline (db) records in descending
          order
        """

        q = select(cls).where(cls.item_id == item_id).order_by(desc(cls.created_at))
        q_result = await db.execute(q)
        db_items = q_result.scalars().all()
        return db_items


class TimelineModel(BaseModel):
    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )


class TrackingModel(BaseModel):
    tags: List[str] = Field(sa_column=Column(ARRAY(String)))
    external_reference_id: str = Field(nullable=True)
