# Import all the models, so that Base has them before being imported by Alembic

from api.db.models.base import BaseTable, Timeline  # noqa: F401
from api.db.models.tenant import Tenant  # noqa: F401
from api.db.models.tenant_webhook import TenantWebhook  # noqa: F401
from api.db.models.tenant_webhook_msg import TenantWebhookMsg  # noqa: F401

from api.db.models.v1.contact import Contact  # noqa: F401
from api.db.models.v1.connection_invitation import ConnectionInvitation  # noqa: F401
from api.db.models.v1.governance import SchemaTemplate, CredentialTemplate  # noqa: F401
from api.db.models.v1.issuer import IssuerCredential  # noqa: F401
from api.db.models.v1.message import Message  # noqa: F401
from api.db.models.v1.tenant_permissions import TenantPermissions  # noqa: F401
from api.db.models.v1.tenant_configuration import (
    TenantConfiguration,
    TenantAutoResponseLog,
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
]
