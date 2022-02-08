import uuid
from datetime import datetime
from typing import Optional

import pydantic
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, func, text
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP


class BaseSchema(pydantic.BaseModel):
    class Config(pydantic.BaseModel.Config):
        orm_mode = True
        read_with_orm_mode = True


class BaseModel(SQLModel, BaseSchema):
    __mapper_args__ = {"eager_defaults": True}


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
