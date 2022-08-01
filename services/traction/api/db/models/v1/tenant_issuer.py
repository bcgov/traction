"""Tenant Permissions Tables/Models.

Models of the Traction tables for tenant permission. This is configuration at the
Traction level - what the innkeeper has enabled or allowed.

"""
import uuid

from sqlmodel import Field


from api.db.models.base import StatefulModel
from api.db.models.v1.tenant import Tenant2

# CURRENTLY UNUSED ATTACHED BY UNCOMMENTING IMPORT IN api/db/models/__init__.py

# uses single table inheritanct
# https://docs.sqlalchemy.org/en/14/orm/inheritance.html#single-table-inheritance


class TenantIssuer(Tenant2, StatefulModel, table=True):
    """TenantIssuer.

    This is the model to store issuer specfic data for
    entries in the table of type 'issuer'.
    """

    # workflow_id will be null until the tenant kicks it off
    endorser_connection_id: uuid.UUID = Field(nullable=True, default=None)
    endorser_connection_state: str = Field(nullable=True, default=None)
    public_did: str = Field(nullable=True, default=None)
    public_did_state: str = Field(nullable=True, default=None)

    __mapper_args__ = {
        "polymorphic_identity": "issuer",
    }
