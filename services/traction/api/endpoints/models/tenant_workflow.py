from enum import Enum


class TenantWorkflowTypeType(str, Enum):
    connection = "api.services.ConnectionWorkflow"
    issuer = "api.services.IssuerWorkflow"
    schema = "api.services.SchemaWorkflow"
    issue_cred = "api.services.IssueCredentialWorkflow"
    present_cred = "api.services.PresentCredentialWorkflow"


class TenantWorkflowStateType(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    error = "error"
