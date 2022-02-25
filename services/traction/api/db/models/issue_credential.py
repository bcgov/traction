import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class IssueCredentialBase(BaseModel):
    tenant_id: uuid.UUID = Field(nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    connection_id: uuid.UUID = Field(nullable=False)
    cred_type: str = Field(nullable=False)
    cred_protocol: str = Field(nullable=False)
    cred_def_id: str = Field(nullable=True, default=None)
    credential: str = Field(nullable=False)
    issue_role: str = Field(nullable=False)
    issue_state: str = Field(nullable=False)
    # workflow_id will be null until the tenant kcks it off
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    cred_exch_id: uuid.UUID = Field(nullable=True, default=None)


class IssueCredential(IssueCredentialBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class IssueCredentialCreate(IssueCredentialBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class IssueCredentialRead(IssueCredentialBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class IssueCredentialUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from IssueCredentialBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    issue_state: str = Field(nullable=False)
    workflow_id: uuid.UUID = Field(nullable=True, default=None)
    cred_exch_id: uuid.UUID = Field(nullable=True, default=None)
