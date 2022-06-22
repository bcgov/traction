import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class PresentCredentialBase(BaseModel):
    tenant_id: uuid.UUID = Field(nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    connection_id: uuid.UUID = Field(nullable=False)
    cred_protocol: str = Field(nullable=False)
    present_request: str = Field(nullable=False)
    present_role: str = Field(nullable=False)
    present_state: str = Field(nullable=False)
    # workflow_id will be null until the tenant kcks it off
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    pres_exch_id: uuid.UUID = Field(nullable=True, default=None)
    presentation: str = Field(nullable=True, default=None)
    cred_def_id: uuid.UUID = Field(nullable=True, default=None)


class PresentCredential(PresentCredentialBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class PresentCredentialCreate(PresentCredentialBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class PresentCredentialRead(PresentCredentialBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PresentCredentialUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from PresentCredentialBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    present_state: str = Field(nullable=False)
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    pres_exch_id: uuid.UUID = Field(nullable=True, default=None)
    presentation: str = Field(nullable=True, default=None)
