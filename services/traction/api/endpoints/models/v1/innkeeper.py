from datetime import datetime
from uuid import UUID

from pydantic.main import BaseModel

from api.endpoints.models.v1.base import GetResponse


class TenantPermissionsItem(BaseModel):
    tenant_id: UUID
    endorser_approval: bool
    create_schema_templates: bool
    create_credential_templates: bool
    issue_credentials: bool
    store_messages: bool
    store_issuer_credentials: bool
    created_at: datetime
    updated_at: datetime


class TenantPermissionsGetResponse(GetResponse[TenantPermissionsItem]):
    pass


class UpdateTenantPermissionsPayload(BaseModel):
    tenant_id: UUID
    endorser_approval: bool | None = False
    create_schema_templates: bool | None = False
    create_credential_templates: bool | None = False
    issue_credentials: bool | None = False
    store_messages: bool | None = False
    store_issuer_credentials: bool | None = False


class UpdateTenantPermissionsResponse(GetResponse[TenantPermissionsItem]):
    pass
