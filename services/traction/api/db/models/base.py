import uuid
from datetime import datetime
from typing import Optional

import pydantic
from sqlalchemy.exc import DBAPIError
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, func, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from api.db.session import async_session
from api.endpoints.models.v1.errors import NotFoundError


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
    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    error_status_detail: str = Field(nullable=True)


class TimelineModel(BaseModel):
    status: str = Field(nullable=False)
    state: str = Field(nullable=False)
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP, nullable=False, server_default=func.now())
    )
