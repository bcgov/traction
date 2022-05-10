from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime


from pydantic import BaseModel


class PublicDIDStateType(str, Enum):
    private = "private"
    requested = "requested"
    endorsed = "endorsed"
    published = "published"
    public = "public"


class AdminTenantIssueRead(BaseModel):
    """AdminTenantIssueRead.

    ResponseModel for Traction Tenant details related to issuance

    Attributes:
      tenant_id: traction's tenant id
      wallet_id: the acapy wallet id
      public_did: uuid, the wallet's public did
      public_did_state: str, state of tenant's public did
      created_at: datetime, tenant issuer details was created
      updated_at: datetime, tenant issuer details were updated
    """

    tenant_id: UUID
    wallet_id: UUID
    public_did: Optional[str]
    public_did_state: Optional[PublicDIDStateType]
    created_at: datetime
    updated_at: datetime
