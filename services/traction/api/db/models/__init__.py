# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import BaseTable, Timeline  # noqa: F401
from api.db.models.tenant import Tenant  # noqa: F401
from api.db.models.tenant_webhook import TenantWebhook  # noqa: F401
from api.db.models.tenant_webhook_msg import TenantWebhookMsg  # noqa: F401
from api.db.models.issue_credential import IssueCredential  # noqa: F401
from api.db.models.present_credential import PresentCredential  # noqa: F401
from api.db.models.tenant_issuer import TenantIssuer  # noqa: F401
from api.db.models.tenant_workflow import TenantWorkflow  # noqa: F401

from api.db.models.v1.contact import Contact  # noqa: F401
from api.db.models.v1.connection_invitation import ConnectionInvitation  # noqa: F401
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate  # noqa: F401
from api.db.models.v1.holder import HolderCredential  # noqa: F401
from api.db.models.v1.issuer import IssuerCredential  # noqa: F401
from api.db.models.v1.message import Message  # noqa: F401
from api.db.models.v1.verifier_presentation import VerifierPresentation  # noqa: F401
from api.db.models.v1.tenant_permissions import TenantPermissions  # noqa: F401
from api.db.models.v1.tenant_configuration import (
    TenantConfiguration,
    TenantAutoResponseLog,
    TenantWebhookLog,
)  # noqa: F401


__all__ = [
    "BaseTable",
    "Tenant",
    "TenantWebhook",
    "TenantWebhookMsg",
    "Contact",
    "ConnectionInvitation",
    "SchemaTemplate",
    "CredentialTemplate",
    "IssuerCredential",
    "Message",
    "Timeline",
    "TenantPermissions",
    "TenantConfiguration",
    "TenantAutoResponseLog",
    "TenantWebhookLog",
    "HolderCredential",
]
