from datetime import datetime
from uuid import UUID

from pydantic.main import BaseModel

from api.endpoints.models.v1.base import GetResponse, ListItemParameters, ListResponse
from api.endpoints.models.v1.tenant import PublicDIDStatus, IssuerStatus, TenantItem


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


class CheckInPayload(BaseModel):
    name: str
    allow_issue_credentials: bool | None = False


class CheckInItem(BaseModel):
    tenant_id: UUID
    name: str
    wallet_id: UUID
    wallet_key: UUID


class CheckInResponse(GetResponse[CheckInItem]):
    pass


class TenantListParameters(ListItemParameters[str, str]):
    public_did_status: PublicDIDStatus | None = PublicDIDStatus.none
    issuer: bool | None = False
    issuer_status: IssuerStatus | None = IssuerStatus.none
    deleted: bool | None = False


class TenantListResponse(ListResponse[TenantItem]):
    pass
