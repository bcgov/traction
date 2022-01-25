from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID

from api.db.base_class import Base


class Tenant(Base):
    __tablename__ = "tenant"

    name = Column(String, nullable=False, unique=True)
    wallet_id = Column(UUID(as_uuid=True), nullable=False)
    wallet_key = Column(UUID(as_uuid=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
