from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from api.db.base_class import Base


class AccessKey(Base):
    __tablename__ = "access_key"

    password = Column(String, nullable=False, unique=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=False)

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id"),
    )
