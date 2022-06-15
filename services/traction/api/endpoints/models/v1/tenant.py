from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from api.endpoints.models.v1.base import GetResponse


class IssuerStatus(str, Enum):
    none = "N/A"
    requested = "Requested"
    active = "Active"


class PublicDIDStatus(str, Enum):
    none = "N/A"
    private = "Private"
    requested = "Requested"
    endorsed = "Endorsed"
    published = "Published"
    public = "Public"


class TenantItem(BaseModel):
    tenant_id: UUID
    wallet_id: UUID
    name: str
    public_did: str | None = None
    public_did_status: PublicDIDStatus | None = PublicDIDStatus.none
    issuer: bool
    issuer_status: IssuerStatus | None = IssuerStatus.none
    deleted: bool = False
    created_at: datetime
    updated_at: datetime


class TenantGetResponse(GetResponse[TenantItem]):
    pass


class TenantPermissionsItem(BaseModel):
    tenant_id: UUID
    store_messages: bool
    store_issuer_credentials: bool
    created_at: datetime
    updated_at: datetime


class TenantPermissionsGetResponse(GetResponse[TenantPermissionsItem]):
    pass


class UpdateTenantPermissionsPayload(BaseModel):
    tenant_id: UUID
    store_messages: bool | None = False
    store_issuer_credentials: bool | None = False


class UpdateTenantPermissionsResponse(GetResponse[TenantPermissionsItem]):
    pass
