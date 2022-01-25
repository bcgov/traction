import uuid
from datetime import datetime

from sqlalchemy import Column, func
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    id: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: datetime = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at: datetime = Column(
        TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now()
    )
    __name__: str
    __mapper_args__ = {"eager_defaults": True}

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
