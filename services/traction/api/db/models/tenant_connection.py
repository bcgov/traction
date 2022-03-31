import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantConnectionBase(BaseModel):
    tenant_id: uuid.UUID = Field(nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    alias: str = Field(nullable=False)
    connection_role: str = Field(nullable=False)
    connection_state: str = Field(nullable=False)
    connection_protocol: str = Field(nullable=True, default=None)
    connection_id: uuid.UUID = Field(nullable=True, default=None)
    invitation: str = Field(nullable=True, default=None)
    invitation_url: str = Field(nullable=True, default=None)
    their_public_did: str = Field(nullable=True, default=None)
    # workflow_id will be null until the tenant kicks it off
    workflow_id: uuid.UUID = Field(nullable=True, default=None)


class TenantConnection(TenantConnectionBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class TenantConnectionCreate(TenantConnectionBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class TenantConnectionRead(TenantConnectionBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantConnectionUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from TenantConnectionBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    connection_id: uuid.UUID = Field(nullable=True, default=None)
    connection_protocol: str = Field(nullable=True, default=None)
    connection_state: str = Field(nullable=True, default=None)
    invitation: str = Field(nullable=True, default=None)
    invitation_url: str = Field(nullable=True, default=None)
    their_public_did: str = Field(nullable=True, default=None)
