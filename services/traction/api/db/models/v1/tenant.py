"""Tenant Permissions Tables/Models.

Models of the Traction tables for tenant permission. This is configuration at the
Traction level - what the innkeeper has enabled or allowed.

"""
import uuid
from typing import Optional
from sqlmodel import Field


from api.db.models.base import TimestampModel

# CURRENTLY UNUSED ATTACHED BY UNCOMMENTING IMPORT IN api/db/models/__init__.py


class Tenant2(TimestampModel, table=True):
    """Tenant.

    This model holds basic information for the tenants that have been
    'checked-in' to the traction service by the 'innkeeper'. Entries
    where is_active is true can provide there wallet_id and wallet_key
    (wallet_key is not known by the innkeeper) to access traction's
    endpoints and execute actions on traction and the aca-py agent underneath.
    """

    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True, primary_key=True)

    name: str = Field(index=True, nullable=False)
    wallet_id: uuid.UUID = Field(nullable=False)
    is_active: bool = Field(nullable=False, default=False)
    wallet_token: Optional[str] = Field(nullable=True)

    tenant_type: str = Field(nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "tenant",
        "polymorphic_on": "tenant_type",
    }
