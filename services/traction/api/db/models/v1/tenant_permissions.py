"""Tenant Permissions Tables/Models.

Models of the Traction tables for tenant permission. This is configuration at the
Traction level - what the innkeeper has enabled or allowed.

"""
import uuid

from sqlmodel import Field
from sqlalchemy import (
    select,
)

from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.models.base import TimestampModel


class TenantPermissions(TimestampModel, table=True):
    """TenantPermissions.

    This is the model for the Tenant Permissions table. This is configuration to allow
    or deny a tenant to do certain things in Traction.  ie. Can the tenant store data in
     Traction?

    This allows the Innkeeper to act as a gatekeeper for the Traction installation.

    For example, this installation of Traction has a data retention policy that does not
     meet the policy required by the Tenant. We do not want that tenant to store their
    data here unless they have agreed and understood our data retention policy. Or, we
    require assurances and acceptance that there is no personal information being stored
     in this Traction installation.

    Attributes:
      tenant_id: Traction Tenant ID
      endorser_approval: when True, the endorser (if configured) has (generally) given
       this tenant approval. This does not mean ALL subsequent transactions will be
       approved.
      create_schema_templates: when True, then tenant can create schema templates
       (and schemas on the ledger). Requires endorser_approval = True.
      create_credential_templates: when True, the tenant can created credential
       templates (and credential definitions on the ledger).
       Requires endorser_approval = True.
      issue_credentials: when True, then tenant is allowed to issue credentials.
        Requires endorser_approval = True.
      store_messages: when True, then tenant can store messages they have sent via
        Traction
      store_issuer_credentials: when True, then tenant can store data for credentials
        they have issued via Traction
      created_at: Timestamp when record was created in Traction
      updated_at: Timestamp when record was last modified in Traction
    """

    __tablename__ = "tenant_permissions"

    tenant_id: uuid.UUID = Field(foreign_key="tenant.id", index=True, primary_key=True)

    endorser_approval: bool = Field(nullable=False, default=False)
    create_schema_templates: bool = Field(nullable=False, default=False)
    create_credential_templates: bool = Field(nullable=False, default=False)
    issue_credentials: bool = Field(nullable=False, default=False)
    store_messages: bool = Field(nullable=False, default=False)
    store_issuer_credentials: bool = Field(nullable=False, default=False)

    @classmethod
    async def get_by_id(
        cls: "TenantPermissions",
        db: AsyncSession,
        tenant_id: uuid.UUID,
    ) -> "TenantPermissions":
        """Get TenantPermissions by tenant id.

        Find and return the database record.
        If one does not exist, insert a default and return it.

        Args:
          db: database session
          tenant_id: Traction ID of tenant making the call

        Returns: The Traction TenantPermissions (db) record

        Raises:

        """

        q = select(cls).where(cls.tenant_id == tenant_id)
        q_result = await db.execute(q)
        db_rec = q_result.scalar_one_or_none()
        if not db_rec:
            # perhaps this is an old tenant, just create a default record
            db_rec = cls(tenant_id=tenant_id)
            db.add(db_rec)
            await db.commit()

        return db_rec
