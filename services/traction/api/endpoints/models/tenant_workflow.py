from enum import Enum


class TenantWorkflowTypeType(str, Enum):
    issuer = "api.services.IssuerWorkflow"
    schema = "api.services.SchemaWorkflow"
    issue_cred = "api.services.IssueCredentialWorkflow"


class TenantWorkflowStateType(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    error = "error"
