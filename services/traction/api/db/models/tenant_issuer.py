import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantIssuerBase(BaseModel):
    tenant_id: uuid.UUID = Field(nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    # workflow_id will be null until the tenant kcks it off
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    endorser_connection_id: uuid.UUID = Field(nullable=True, default=None)
    endorser_connection_state: str = Field(nullable=True, default=None)
    public_did: str = Field(nullable=True, default=None)
    public_did_state: str = Field(nullable=True, default=None)


class TenantIssuer(TenantIssuerBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class TenantIssuerCreate(TenantIssuerBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class TenantIssuerRead(TenantIssuerBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantIssuerUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from TenantIssuerBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    endorser_connection_id: uuid.UUID = Field(nullable=True, default=None)
    endorser_connection_state: str = Field(nullable=True, default=None)
    public_did: str = Field(nullable=True, default=None)
    public_did_state: str = Field(nullable=True, default=None)
