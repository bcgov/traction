from datetime import datetime
from uuid import UUID

from api.models.schema.base import BaseSchema


class AccessKeySchemaBase(BaseSchema):
    tenant_id: UUID
    is_admin: bool
    is_active: bool


class InAccessKeySchema(AccessKeySchemaBase):
    password: str


class AccessKeySchema(AccessKeySchemaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class OutAccessKeySchema(AccessKeySchema):
    """"""
