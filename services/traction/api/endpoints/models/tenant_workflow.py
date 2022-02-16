from enum import Enum


class TenantWorkflowTypeType(str, Enum):
    issuer = "api.services.IssuerWorkflow"


class TenantWorkflowStateType(str, Enum):
    pending = "pending"
    active = "active"
    completed = "completed"
    error = "error"
