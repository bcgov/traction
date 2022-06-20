from datetime import datetime
from enum import Enum
from typing import Optional
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


class TenantConfigurationItem(BaseModel):
    webhook_url: str | None = None
    webhook_key: str | None = None
    auto_respond_messages: bool
    auto_response_message: str | None = None
    store_messages: bool
    store_issuer_credentials: bool
    created_at: datetime
    updated_at: datetime


class TenantConfigurationGetResponse(GetResponse[TenantConfigurationItem]):
    pass


class UpdateTenantConfigurationPayload(BaseModel):
    webhook_url: Optional[str]
    webhook_key: Optional[str]
    auto_respond_messages: Optional[bool]
    auto_response_message: Optional[str]
    store_messages: Optional[bool]
    store_issuer_credentials: Optional[bool]


class UpdateTenantConfigurationResponse(GetResponse[TenantConfigurationItem]):
    pass
