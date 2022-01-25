from datetime import datetime
from uuid import UUID

from api.models.schema.base import BaseSchema


class TenantSchemaBase(BaseSchema):
    is_active: bool


class InTenantSchema(TenantSchemaBase):
    name: str
    wallet_id: UUID
    wallet_key: UUID


class TenantSchema(TenantSchemaBase):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


class OutTenantSchema(TenantSchema):
    """"""


class RequestCheckInSchema(BaseSchema):
    name: str


class ResponseCheckInSchema(BaseSchema):
    id: UUID
    name: str
    wallet_id: UUID
    wallet_name: UUID
    wallet_key: UUID
    tenant_api_key: UUID
