import uuid
from datetime import datetime

from sqlmodel import Field

from api.db.models.base import BaseModel, BaseTable


class TenantWorkflowBase(BaseModel):
    wallet_id: uuid.UUID = Field(nullable=False)
    workflow_type: str = Field(nullable=False)
    workflow_state: str = Field(nullable=False)
    workflow_state_msg: str = Field(nullable=True, default=None)
    wallet_bearer_token: str = Field(nullable=True, default=None)


class TenantWorkflow(TenantWorkflowBase, BaseTable, table=True):
    # This is the class that represents the table
    pass


class TenantWorkflowCreate(TenantWorkflowBase):
    # This is the class that represents interface for creating a tenant
    # we must set all the required fields,
    # but do not need to set optional (and shouldn't)
    pass


class TenantWorkflowRead(TenantWorkflowBase):
    # This is the class that represents interface for reading a tenant
    # here we indicate id, created_at and updated_at must be included
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TenantWorkflowUpdate(BaseModel):
    # This is our update interface
    # This does NOT inherit from TenantWorkflowBase,
    # so no need to worry about accidentally updating id or other fields
    id: uuid.UUID
    workflow_state: str = Field(nullable=False)
    workflow_state_msg: str = Field(nullable=True, default=None)
    wallet_bearer_token: str = Field(nullable=True, default=None)
